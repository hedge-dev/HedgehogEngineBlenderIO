using SharpNeedle.Framework.HedgehogEngine.Mirage;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Numerics;

namespace HEIO.NET.VertexUtils
{
    internal class MeshProcessor
    {
        private readonly struct CompTri : IComparable<CompTri>
        {
            public readonly int i1, i2, i3;

            public CompTri(int i1, int i2, int i3)
            {
                if (i1 > i2)
                {
                    (i1, i2) = (i2, i1);
                }

                if (i2 > i3)
                {
                    (i2, i3) = (i3, i2);
                }

                if (i1 > i2)
                {
                    (i1, i2) = (i2, i1);
                }

                this.i1 = i1;
                this.i2 = i2;
                this.i3 = i3;
            }

            public int CompareTo(CompTri other)
            {
                if (i1 != other.i1)
                {
                    return i1 > other.i1 ? 1 : -1;
                }

                if (i2 != other.i2)
                {
                    return i2 > other.i2 ? 1 : -1;
                }

                if (i3 != other.i3)
                {
                    return i3 > other.i3 ? 1 : -1;
                }

                return 0;
            }
        }

        private readonly Topology _topology;
        private readonly int _morphCount;
        private readonly EqualityComparer<Vertex>? _mergeComparer;
        private readonly bool _mergeSplitEdges;

        private readonly List<Vertex> _tempVertices = [];
        private readonly List<List<Vector2>> _tempTexcoords = [];
        private readonly List<List<Vector4>> _tempColors = [];
        private readonly List<int> _tempTriangles = [];
        private readonly List<int> _tempSetSizes = [];

        public MeshData ResultData { get; }


        public MeshProcessor(string name, Topology topology, bool merge, float mergeDistance, bool mergeSplitEdges, int morphCount)
        {
            _topology = topology;
            _morphCount = morphCount;

            if (merge)
            {
                _mergeSplitEdges = mergeSplitEdges;
                _mergeComparer = Vertex.GetMergeComparer(mergeDistance, !mergeSplitEdges, morphCount > 0);
            }

            ResultData = new(
                name,
                [], [],
                _mergeSplitEdges ? [] : null,
                _mergeSplitEdges ? [] : null,
                [], [], true,
                [], [], [],
                [], []
            );
        }


        private Vertex[] GetVertices(GPUMesh gpuMesh)
        {
            Vertex[] vertices = new Vertex[gpuMesh.Vertices.Length];

            for (int i = 0; i < vertices.Length; i++)
            {
                GPUVertex vertex = gpuMesh.Vertices[i];

                vertices[i] = new Vertex(
                    vertex.Position,
                    _morphCount,
                    vertex.Normal,
                    vertex.Tangent,
                    [.. vertex.Weights
                        .Where(x => x.Weight != 0)
                        .Select(x => new VertexWeight(gpuMesh.BoneIndices[x.Index], x.Weight))
                        .OrderBy(x => x.Index)]
                );
            }

            return vertices;
        }

        public void AddGroupInfo(string groupname, int groupSize)
        {
            ResultData.GroupNames.Add(groupname);
            ResultData.GroupSizes.Add(groupSize);
        }

        public void AddMesh(Mesh mesh, bool addVertices = true)
        {
            ResultData.SetMaterials.Add(mesh.Material);
            ResultData.SetSlots.Add(mesh.Slot);

            GPUMesh gpuMesh = GPUMesh.ReadFromMesh(mesh, _topology);

            if (!gpuMesh.UseByteColors)
            {
                ResultData.UseByteColors = false;
            }

            while (gpuMesh.TexcoordSets > ResultData.TextureCoordinates.Count)
            {
                ResultData.TextureCoordinates.Add([.. Enumerable.Range(0, ResultData.TriangleIndices.Count).Select(x => default(Vector2))]);
                _tempTexcoords.Add([.. Enumerable.Range(0, _tempTriangles.Count).Select(x => default(Vector2))]);
            }

            while (gpuMesh.ColorSets > ResultData.Colors.Count)
            {
                ResultData.Colors.Add([.. Enumerable.Range(0, ResultData.TriangleIndices.Count).Select(x => Vector4.One)]);
                _tempColors.Add([.. Enumerable.Range(0, _tempTriangles.Count).Select(x => Vector4.One)]);
            }

            _tempTriangles.AddRange(gpuMesh.Triangles.Select(x => x + _tempVertices.Count));
            _tempSetSizes.Add(gpuMesh.Triangles.Length / 3);

            for (int i = 0; i < ResultData.TextureCoordinates.Count; i++)
            {
                if (i < gpuMesh.TexcoordSets)
                {
                    _tempTexcoords[i].AddRange(gpuMesh.Triangles.Select(x => gpuMesh.Vertices[x].TextureCoordinates[i]));
                }
                else
                {
                    _tempTexcoords[i].AddRange(Enumerable.Range(0, gpuMesh.Triangles.Length).Select(x => default(Vector2)));
                }
            }

            for (int i = 0; i < ResultData.Colors.Count; i++)
            {
                if (i < gpuMesh.ColorSets)
                {
                    _tempColors[i].AddRange(gpuMesh.Triangles.Select(x => gpuMesh.Vertices[x].Colors[i]));
                }
                else
                {
                    _tempColors[i].AddRange(Enumerable.Range(0, gpuMesh.Triangles.Length).Select(x => Vector4.One));
                }
            }

            if(addVertices)
            {
                _tempVertices.AddRange(GetVertices(gpuMesh));
            }
        }

        public void AddMorphPositions(Vector3[] positions, int morphIndex, int offset)
        {
            for(int i = 0; i < positions.Length; i++)
            {
                _tempVertices[offset + i].MorphPositions![morphIndex] = positions[i];
            }
        }

        public void ProcessData()
        {
            DistinctMap<Vertex> vertices = _mergeComparer == null
                    ? new(_tempVertices, null)
                    : DistinctMap.CreateDistinctMap(_tempVertices, _mergeComparer);

            int vertexIndexOffset = ResultData.Vertices.Count;
            foreach (Vertex vertex in vertices.Values)
            {
                if (_mergeSplitEdges)
                {
                    Vertex toAdd = vertex;
                    toAdd.Normal = default;
                    toAdd.Tangent = default;
                    ResultData.Vertices.Add(toAdd);
                }
                else
                {
                    ResultData.Vertices.Add(vertex);
                }
            }

            SortedSet<CompTri> usedTriangles = [];

            int triangleIndex = 0;

            for (int i = 0; i < _tempTriangles.Count;)
            {
                int v1 = _tempTriangles[i];
                int v2 = _tempTriangles[i + 1];
                int v3 = _tempTriangles[i + 2];

                int t1 = vertices[v1];
                int t2 = vertices[v2];
                int t3 = vertices[v3];

                if (t1 == t2 || t2 == t3 || t3 == t1 || !usedTriangles.Add(new(t1, t2, t3)))
                {
                    int offset = 0;
                    for (int j = 0; j < _tempSetSizes.Count; offset += _tempSetSizes[j], j++)
                    {
                        if (triangleIndex - offset < _tempSetSizes[j])
                        {
                            _tempSetSizes[j]--;
                            break;
                        }
                    }

                    i += 3;
                    continue;
                }

                for (int j = 0; j < 3; j++, i++,
                    t1 = t2, t2 = t3,
                    v1 = v2, v2 = v3)
                {
                    Vertex vertex = _tempVertices[v1];

                    ResultData.TriangleIndices.Add(vertexIndexOffset + t1);
                    ResultData.PolygonNormals?.Add(vertex.Normal);
                    ResultData.PolygonTangents?.Add(vertex.Tangent);

                    for (int k = 0; k < ResultData.TextureCoordinates.Count; k++)
                    {
                        Vector2 texcoord = _tempTexcoords[k][i];
                        ResultData.TextureCoordinates[k].Add(new(texcoord.X, 1 - texcoord.Y));
                    }

                    for (int k = 0; k < ResultData.Colors.Count; k++)
                    {
                        ResultData.Colors[k].Add(_tempColors[k][i]);
                    }
                }

                triangleIndex++;
            }

            foreach (int setSize in _tempSetSizes)
            {
                ResultData.SetSizes.Add(setSize);
            }

            _tempVertices.Clear();
            _tempSetSizes.Clear();
            _tempTriangles.Clear();

            foreach (List<Vector2> texCoords in _tempTexcoords)
            {
                texCoords.Clear();
            }

            foreach (List<Vector4> colors in _tempColors)
            {
                colors.Clear();
            }
        }
    }

}
