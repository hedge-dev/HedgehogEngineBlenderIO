using HEIO.NET.VertexUtils;
using SharpNeedle.Framework.HedgehogEngine.Mirage;
using SharpNeedle.Resource;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Numerics;
using System.Security;

namespace HEIO.NET
{
    public struct Vertex
    {
        public Vector3 Position { get; set; }

        public Vector3 Normal { get; set; }

        public Vector3 Tangent { get; set; }

        public List<VertexWeight> Weights { get; set; }

        public Vertex(Vector3 position, Vector3 normal, Vector3 tangent, List<VertexWeight> weights)
        {
            Position = position;
            Normal = normal;
            Tangent = tangent;
            Weights = [.. weights.Where(x => x.Weight != 0).OrderBy(x => x.Index)];
        }

        public static EqualityComparer<Vertex> GetMergeComparer(float mergeDistance, bool compareNormals)
        {
            float mergeDistanceSquared = mergeDistance * mergeDistance;

            if(compareNormals)
            {
                return EqualityComparer<Vertex>.Create((v1, v2) =>
                    Vector3.DistanceSquared(v1.Position, v2.Position) < mergeDistanceSquared
                    && VertexWeight.CompareEquality(v1.Weights, v2.Weights)
                    && Vector3.Dot(v1.Normal, v2.Normal) > 0.995f);
            }
            else
            {
                return EqualityComparer<Vertex>.Create((v1, v2) =>
                    Vector3.DistanceSquared(v1.Position, v2.Position) < mergeDistanceSquared
                    && VertexWeight.CompareEquality(v1.Weights, v2.Weights));
            }

        }

    }

    public enum VertexMergeMode
    {
        None,
        SubMesh,
        SubMeshGroup,
        All
    }

    public class MeshData
    {
        public string Name { get; set; }

        public IList<Vertex> Vertices { get; set; }


        public IList<int> TriangleIndices { get; set; }

        public IList<Vector3>? PolygonNormals { get; set; }

        public IList<Vector3>? PolygonTangents { get; set; }

        public IList<IList<Vector2>> TextureCoordinates { get; set; }

        public IList<IList<Vector4>> Colors { get; set; }

        public bool UseByteColors { get; set; }


        public IList<ResourceReference<Material>> SetMaterials { get; set; }

        public IList<MeshSlot> SetSlots { get; }

        public IList<int> SetSizes { get; set; }


        public IList<string> GroupNames { get; set; }

        public IList<int> GroupSizes { get; set; }


        public MeshData(
            string name, 
            IList<Vertex> vertices, 
            IList<int> triangleIndices, 
            IList<Vector3>? polygonNormals, 
            IList<Vector3>? polygonTangents,
            IList<IList<Vector2>> textureCoordinates, 
            IList<IList<Vector4>> colors, 
            bool useByteColors, 
            IList<ResourceReference<Material>> setMaterials, 
            IList<MeshSlot> setSlots, 
            IList<int> setSizes, 
            IList<string> groupNames, 
            IList<int> groupSizes)
        {
            Name = name;
            Vertices = vertices;
            TriangleIndices = triangleIndices;
            PolygonNormals = polygonNormals;
            PolygonTangents = polygonTangents;
            TextureCoordinates = textureCoordinates;
            Colors = colors;
            UseByteColors = useByteColors;
            SetMaterials = setMaterials;
            SetSlots = setSlots;
            SetSizes = setSizes;
            GroupNames = groupNames;
            GroupSizes = groupSizes;
        }


        private readonly struct CompTri : IComparable<CompTri>
        {
            public readonly int i1, i2, i3;

            public CompTri(int i1, int i2, int i3)
            {
                if(i1 > i2)
                {
                    (i1, i2) = (i2, i1);
                }

                if(i2 > i3)
                {
                    (i2, i3) = (i3, i2);
                }

                if(i1 > i2)
                {
                    (i1, i2) = (i2, i1);
                }

                this.i1 = i1;
                this.i2 = i2;
                this.i3 = i3;
            }

            public int CompareTo(CompTri other)
            {
                if(i1 != other.i1)
                {
                    return i1 > other.i1 ? 1 : -1;
                }

                if(i2 != other.i2)
                {
                    return i2 > other.i2 ? 1 : -1;
                }

                if(i3 != other.i3)
                {
                    return i3 > other.i3 ? 1 : -1;
                }

                return 0;
            }
        }

        private static Vertex[] GetVertices(GPUMesh gpuMesh)
        {
            Vertex[] vertices = new Vertex[gpuMesh.Vertices.Length];

            for(int i = 0; i < vertices.Length; i++)
            {
                GPUVertex vertex = gpuMesh.Vertices[i];

                vertices[i] = new Vertex(
                    vertex.Position,
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

        public static MeshData FromHEModel(ModelBase model, VertexMergeMode vertexMergeMode, float mergeDistance, bool mergeSplitEdges)
        {
            Topology topology = model.Root?.FindNode("Topology")?.Value == 3 
                ? Topology.TriangleList 
                : Topology.TriangleStrips;

            EqualityComparer<Vertex>? mergeComparer = null;

            if(vertexMergeMode == VertexMergeMode.None)
            {
                mergeDistance = 0;
                mergeSplitEdges = false;
            }
            else
            {
                mergeComparer = Vertex.GetMergeComparer(mergeDistance, !mergeSplitEdges);
            }

            MeshData result = new(
                model.Name, 
                [], [],
                mergeSplitEdges ? [] : null,
                mergeSplitEdges ? [] : null,
                [], [], true,
                [], [], [],
                [], []
            );

            List<Vertex> tempVertices = [];
            List<List<Vector2>> tempTexcoords = [];
            List<List<Vector4>> tempColors = [];
            List<int> tempTriangles = [];
            List<int> tempSetSizes = [];

            void ProcessData()
            {
                DistinctMap<Vertex> vertices = mergeComparer == null
                    ? new(tempVertices, null)
                    : DistinctMap.CreateDistinctMap(tempVertices, mergeComparer);

                int vertexIndexOffset = result.Vertices.Count;
                foreach(Vertex vertex in vertices.Values)
                {
                    if(mergeSplitEdges)
                    {
                        Vertex toAdd = vertex;
                        toAdd.Normal = default;
                        toAdd.Tangent = default;
                        result.Vertices.Add(toAdd);
                    }
                    else
                    {
                        result.Vertices.Add(vertex);
                    }
                }

                SortedSet<CompTri> usedTriangles = [];

                int triangleIndex = 0;

                for(int i = 0; i < tempTriangles.Count;)
                {
                    int v1 = tempTriangles[i];
                    int v2 = tempTriangles[i + 1];
                    int v3 = tempTriangles[i + 2];

                    int t1 = vertices[v1];
                    int t2 = vertices[v2];
                    int t3 = vertices[v3];

                    if(t1 == t2 || t2 == t3 || t3 == t1 || !usedTriangles.Add(new(t1, t2, t3)))
                    {
                        int offset = 0;
                        for(int j = 0; j < tempSetSizes.Count; offset += tempSetSizes[j], j++)
                        {
                            if(triangleIndex - offset < tempSetSizes[j])
                            {
                                tempSetSizes[j]--;
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
                        Vertex vertex = tempVertices[v1];

                        result.TriangleIndices.Add(vertexIndexOffset + t1);
                        result.PolygonNormals?.Add(vertex.Normal);
                        result.PolygonTangents?.Add(vertex.Tangent);

                        for(int k = 0; k < result.TextureCoordinates.Count; k++)
                        {
                            Vector2 texcoord = tempTexcoords[k][i];
                            result.TextureCoordinates[k].Add(new(texcoord.X, 1 - texcoord.Y));
                        }

                        for(int k = 0; k < result.Colors.Count; k++)
                        {
                            result.Colors[k].Add(tempColors[k][i]);
                        }
                    }

                    triangleIndex++;
                }
            
                foreach(int setSize in tempSetSizes)
                {
                    result.SetSizes.Add(setSize);
                }

                tempVertices.Clear();
                tempSetSizes.Clear();
                tempTriangles.Clear();

                foreach(List<Vector2> texCoords in tempTexcoords)
                {
                    texCoords.Clear();
                }

                foreach(List<Vector4> colors in tempColors)
                {
                    colors.Clear();
                }
            }

            foreach(MeshGroup group in model.Groups)
            {
                result.GroupNames.Add(group.Name ?? string.Empty);
                result.GroupSizes.Add(group.Count);

                foreach(Mesh mesh in group)
                {
                    result.SetMaterials.Add(mesh.Material);
                    result.SetSlots.Add(mesh.Slot);

                    GPUMesh gpuMesh = GPUMesh.ReadFromMesh(mesh, topology);

                    if(!gpuMesh.UseByteColors)
                    {
                        result.UseByteColors = false;
                    }

                    while(gpuMesh.TexcoordSets > result.TextureCoordinates.Count)
                    {
                        result.TextureCoordinates.Add([.. Enumerable.Range(0, result.TriangleIndices.Count).Select(x => default(Vector2))]);
                        tempTexcoords.Add([.. Enumerable.Range(0, tempTriangles.Count).Select(x => default(Vector2))]);
                    }

                    while(gpuMesh.ColorSets > result.Colors.Count)
                    {
                        result.Colors.Add([.. Enumerable.Range(0, result.TriangleIndices.Count).Select(x => Vector4.One)]);
                        tempColors.Add([.. Enumerable.Range(0, tempTriangles.Count).Select(x => Vector4.One)]);
                    }

                    tempTriangles.AddRange(gpuMesh.Triangles.Select(x => x + tempVertices.Count));
                    tempSetSizes.Add(gpuMesh.Triangles.Length / 3);

                    for(int i = 0; i < result.TextureCoordinates.Count; i++)
                    {
                        if(i < gpuMesh.TexcoordSets)
                        {
                            tempTexcoords[i].AddRange(gpuMesh.Triangles.Select(x => gpuMesh.Vertices[x].TextureCoordinates[i]));
                        }
                        else
                        {
                            tempTexcoords[i].AddRange(Enumerable.Range(0, gpuMesh.Triangles.Length).Select(x => default(Vector2)));
                        }
                    }

                    for(int i = 0; i < result.Colors.Count; i++)
                    {
                        if(i < gpuMesh.ColorSets)
                        {
                            tempColors[i].AddRange(gpuMesh.Triangles.Select(x => gpuMesh.Vertices[x].Colors[i]));
                        }
                        else
                        {
                            tempColors[i].AddRange(Enumerable.Range(0, gpuMesh.Triangles.Length).Select(x => Vector4.One));
                        }
                    }

                    tempVertices.AddRange(GetVertices(gpuMesh));

                    if(vertexMergeMode == VertexMergeMode.SubMesh)
                    {
                        ProcessData();
                    }
                }

                if(vertexMergeMode == VertexMergeMode.SubMeshGroup)
                {
                    ProcessData();
                }
            }

            ProcessData();

            return result;
        }

    }
}
