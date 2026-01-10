using HEIO.NET.Modeling;
using HEIO.NET.Modeling.GPU;
using J113D.Common;
using SharpNeedle.Framework.HedgehogEngine.Mirage.ModelData;
using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.Linq;
using System.Numerics;

namespace HEIO.NET.Modeling.ConvertFrom
{
    internal class GPUMeshConverter
    {
        private readonly Topology _topology;
        private readonly int _morphCount;
        private readonly EqualityComparer<Vertex>? _mergeComparer;
        private readonly bool _mergeSplitEdges;

        private readonly List<Vertex> _tempVertices = [];
        private readonly List<List<Vector2>> _tempTexcoords = [];
        private readonly List<List<Vector4>> _tempColors = [];
        private readonly List<int> _tempTriangles = [];
        private int _tempSetOffset = 0;

        public MeshData ResultData { get; }


        public GPUMeshConverter(string name, Topology topology, bool merge, float mergeDistance, bool mergeSplitEdges, int morphCount)
        {
            _topology = topology;
            _morphCount = morphCount;

            if(merge)
            {
                _mergeSplitEdges = mergeSplitEdges;
                _mergeComparer = Vertex.GetMergeComparer(mergeDistance, !mergeSplitEdges, morphCount > 0);
            }

            ResultData = new(name, _mergeSplitEdges);
        }


        private Vertex[] GetVertices(GPUMesh gpuMesh)
        {
            Vertex[] vertices = new Vertex[gpuMesh.Vertices.Count];

            for(int i = 0; i < vertices.Length; i++)
            {
                GPUVertex vertex = gpuMesh.Vertices[i];

                vertices[i] = new Vertex(
                    vertex.Position,
                    _morphCount,
                    vertex.Normal,
                    vertex.UVDirection,
                    gpuMesh.MultiTangent ? vertex.UVDirection2 : vertex.UVDirection,
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
            ResultData.GroupSetCounts.Add(groupSize);
        }

        public void AddMesh(Mesh mesh, bool addVertices = true)
        {
            GPUMesh gpuMesh = MeshConverter.ConvertToGPUMesh(mesh, _topology);

            ResultData.MeshSets.Add(new(
                gpuMesh.UseByteColors,
                gpuMesh.Vertices[0].Weights.Length > 4,
                gpuMesh.MultiTangent,
                mesh.Material,
                mesh.Slot,
                gpuMesh.Triangles.Count / 3
            ));

            if(gpuMesh.MultiTangent && ResultData.PolygonUVDirections != null && ResultData.PolygonUVDirections2 == null)
            {
                ResultData.PolygonUVDirections2 = new List<UVDirection>(ResultData.PolygonUVDirections);
            }

            void AddBase<T, W>(IList<W> output, int fallbackLength, T fallback) where W : IList<T>
            {
                if(new List<T>(Enumerable.Range(0, fallbackLength).Select(x => fallback)) is W w)
                {
                    output.Add(w);
                }
                else
                {
                    throw new UnreachableException();
                }
            }

            while(gpuMesh.TexcoordSets > ResultData.TextureCoordinates.Count)
            {
                AddBase(ResultData.TextureCoordinates, ResultData.TriangleIndices.Count, default(Vector2));
                AddBase(_tempTexcoords, _tempTriangles.Count, default(Vector2));
            }

            while(gpuMesh.ColorSets > ResultData.Colors.Count)
            {
                AddBase(ResultData.Colors, ResultData.TriangleIndices.Count, Vector4.One);
                AddBase(_tempColors, _tempTriangles.Count, Vector4.One);
            }

            _tempTriangles.AddRange(gpuMesh.Triangles.Select(x => x + _tempVertices.Count));

            void AddNew<T>(List<List<T>> output, int inputSets, int outputSets, Func<GPUVertex, int, T> getValue, T fallback)
            {
                for(int i = 0; i < outputSets; i++)
                {
                    if(i < inputSets)
                    {
                        output[i].AddRange(gpuMesh.Triangles.Select(x => getValue(gpuMesh.Vertices[x], i)));
                    }
                    else
                    {
                        output[i].AddRange(Enumerable.Range(0, gpuMesh.Triangles.Count).Select(x => fallback));
                    }
                }
            }

            AddNew(_tempTexcoords, gpuMesh.TexcoordSets, ResultData.TextureCoordinates.Count, (v, i) => new Vector2(v.TextureCoordinates[i].X, 1 - v.TextureCoordinates[i].Y), default);
            AddNew(_tempColors, gpuMesh.ColorSets, ResultData.Colors.Count, (v, i) => v.Colors[i], Vector4.One);

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
            foreach(Vertex vertex in vertices.Values)
            {
                if(_mergeSplitEdges)
                {
                    Vertex toAdd = vertex;
                    toAdd.Normal = default;
                    toAdd.UVDirection = default;
                    toAdd.UVDirection2 = default;
                    ResultData.Vertices.Add(toAdd);
                }
                else
                {
                    ResultData.Vertices.Add(vertex);
                }
            }

            SortedSet<CompTri> usedTriangles = [];

            int triangleIndex = 0;

            for(int i = 0; i < _tempTriangles.Count;)
            {
                int v1 = _tempTriangles[i];
                int v2 = _tempTriangles[i + 1];
                int v3 = _tempTriangles[i + 2];

                int t1 = vertices[v1];
                int t2 = vertices[v2];
                int t3 = vertices[v3];

                if(t1 == t2 || t2 == t3 || t3 == t1 || !usedTriangles.Add(new(t1, t2, t3)))
                {
                    int offset = 0;
                    for(int j = _tempSetOffset; j < ResultData.MeshSets.Count; offset += ResultData.MeshSets[j].Size, j++)
                    {
                        if(triangleIndex - offset < ResultData.MeshSets[j].Size)
                        {
                            ResultData.MeshSets[j].Size--;
                            break;
                        }
                    }

                    i += 3;
                    continue;
                }

                for(int j = 0; j < 3; j++, i++,
                    t1 = t2, t2 = t3,
                    v1 = v2, v2 = v3)
                {
                    Vertex vertex = _tempVertices[v1];

                    ResultData.TriangleIndices.Add(vertexIndexOffset + t1);
                    ResultData.PolygonNormals?.Add(vertex.Normal);
                    ResultData.PolygonUVDirections?.Add(vertex.UVDirection);
                    ResultData.PolygonUVDirections2?.Add(vertex.UVDirection2);

                    for(int k = 0; k < ResultData.TextureCoordinates.Count; k++)
                    {
                        ResultData.TextureCoordinates[k].Add(_tempTexcoords[k][i]);
                    }

                    for(int k = 0; k < ResultData.Colors.Count; k++)
                    {
                        ResultData.Colors[k].Add(_tempColors[k][i]);
                    }
                }

                triangleIndex++;
            }

            _tempVertices.Clear();
            _tempTriangles.Clear();
            _tempSetOffset = ResultData.MeshSets.Count;

            foreach(List<Vector2> texCoords in _tempTexcoords)
            {
                texCoords.Clear();
            }

            foreach(List<Vector4> colors in _tempColors)
            {
                colors.Clear();
            }
        }

        public void NormalizeBindPositions(Model model)
        {
            Matrix4x4[] normalizeMatrices = new Matrix4x4[model.Nodes.Count];
            bool allIdentity = true;

            for(int i = 0; i < model.Nodes.Count; i++)
            {
                Matrix4x4 bindMatrix = model.Nodes[i].Transform;

                Matrix4x4.Invert(bindMatrix, out Matrix4x4 boneMatrix);
                Matrix4x4 normalizeMatrix = bindMatrix * Normalized(boneMatrix);

                if(CheckIsIdentity(normalizeMatrix))
                {
                    normalizeMatrix = Matrix4x4.Identity;
                }
                else
                {
                    allIdentity = false;
                }

                normalizeMatrices[i] = normalizeMatrix;
            }

            if(allIdentity)
            {
                return;
            }

            Vector3 TransformPosition(Vector3 input, VertexWeight[] weights)
            {
                Matrix4x4 matrix = new();

                foreach(VertexWeight weight in weights)
                {
                    matrix += normalizeMatrices[weight.Index] * weight.Weight;
                }

                return Vector3.Transform(new(input.X, input.Y, input.Z), matrix);
            }

            for(int i = 0; i < ResultData.Vertices.Count; i++)
            {
                Vertex vertex = ResultData.Vertices[i];

                vertex.Position = TransformPosition(vertex.Position, vertex.Weights);

                if(vertex.MorphPositions != null)
                {
                    for(int j = 0; j < vertex.MorphPositions.Length; j++)
                    {
                        vertex.MorphPositions[j] = TransformPosition(vertex.MorphPositions[j], vertex.Weights);
                    }
                }

                ResultData.Vertices[i] = vertex;
            }
        }

        private static Matrix4x4 Normalized(Matrix4x4 input)
        {
            float l1 = new Vector3(input.M11, input.M12, input.M13).Length();
            float l2 = new Vector3(input.M21, input.M22, input.M23).Length();
            float l3 = new Vector3(input.M31, input.M32, input.M33).Length();
            return new(
                input.M11 / l1, input.M12 / l1, input.M13 / l1, input.M14 / l1,
                input.M21 / l2, input.M22 / l2, input.M23 / l2, input.M24 / l2,
                input.M31 / l3, input.M32 / l3, input.M33 / l3, input.M34 / l3,
                input.M41, input.M42, input.M43, input.M44
            );
        }

        private static bool CheckIsIdentity(Matrix4x4 a)
        {
            const float p1 = 1.0001f;
            const float n1 = 0.9999f;
            const float p0 = 0.0001f;
            const float n0 = -0.0001f;

            return a.M11 is > n1 and < p1
                && a.M12 is > n0 and < p0
                && a.M13 is > n0 and < p0
                && a.M14 is > n0 and < p0
                && a.M21 is > n0 and < p0
                && a.M22 is > n1 and < p1
                && a.M23 is > n0 and < p0
                && a.M24 is > n0 and < p0
                && a.M31 is > n0 and < p0
                && a.M32 is > n0 and < p0
                && a.M33 is > n1 and < p1
                && a.M34 is > n0 and < p0
                && a.M41 is > n0 and < p0
                && a.M42 is > n0 and < p0
                && a.M43 is > n0 and < p0
                && a.M44 is > n1 and < p1;
        }
    }
}

