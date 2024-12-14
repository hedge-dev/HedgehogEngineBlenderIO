using HEIO.NET.VertexUtils;
using SharpNeedle.Framework.HedgehogEngine.Mirage;
using SharpNeedle.Framework.SurfRide.Draw;
using SharpNeedle.Resource;
using SharpNeedle.Structs;
using System;
using System.Collections.Generic;
using System.Numerics;

namespace HEIO.NET
{
    public struct Vertex
    {
        public int SetIndex { get; set; }

        public Vector3 Position { get; set; }

        public Vector3 Normal { get; set; }

        public Vector3 Tangent { get; set; }

        public Vertex(int setIndex, Vector3 position, Vector3 normal, Vector3 tangent)
        {
            SetIndex = setIndex;
            Position = position;
            Normal = normal;
            Tangent = tangent;
        }

        public static EqualityComparer<Vertex> GetMergeComparer(float mergeDistance, bool compareSetIndex, bool compareNormals)
        {
            float mergeDistanceSquared = mergeDistance * mergeDistance;

            if(compareSetIndex)
            {
                if(compareNormals)
                {
                    return EqualityComparer<Vertex>.Create((v1, v2) =>
                        Vector3.DistanceSquared(v1.Position, v2.Position) < mergeDistanceSquared
                        && Vector3.Dot(v1.Normal, v2.Normal) > 0.995f);
                }
                else
                {
                    return EqualityComparer<Vertex>.Create((v1, v2) =>
                        Vector3.DistanceSquared(v1.Position, v2.Position) < mergeDistanceSquared);
                }
            }
            else
            {
                if(compareNormals)
                {
                    return EqualityComparer<Vertex>.Create((v1, v2) =>
                        v1.SetIndex == v2.SetIndex
                        && Vector3.DistanceSquared(v1.Position, v2.Position) < mergeDistanceSquared
                        && Vector3.Dot(v1.Normal, v2.Normal) > 0.995f);
                }
                else
                {
                    return EqualityComparer<Vertex>.Create((v1, v2) =>
                        v1.SetIndex == v2.SetIndex
                        && Vector3.DistanceSquared(v1.Position, v2.Position) < mergeDistanceSquared);
                }
            }

        }

    }

    public enum VertexMergeMode
    {
        None,
        SubMesh,
        All
    }

    public class MeshData
    {
        public string Name { get; set; }

        public IList<Vertex> Vertices { get; set; }


        public IList<int> TriangleIndices { get; set; }

        public IList<Vector3>? PolygonNormals { get; set; }

        public IList<Vector3>? PolygonTangents { get; set; }

        public IList<Vector2>[] TextureCoordinates { get; set; }

        public IList<IList<Vector4>> Colors { get; set; }

        public bool UseByteColors { get; set; }


        public ResourceReference<Material>[] SetMaterials { get; set; }

        public MeshSlot[] SetSlots { get; }

        public int[] SetSizes { get; set; }


        public MeshData(string name, IList<Vertex> vertices, IList<int> triangleIndices, IList<Vector3>? polygonNormals, IList<Vector3>? polygonTangents, IList<Vector2>[] textureCoordinates, IList<IList<Vector4>> colors, bool useByteColors, ResourceReference<Material>[] setMaterials, MeshSlot[] setSlots, int[] setSizes)
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

        private static DistinctMap<Vertex> GetVertices(GPUModel gpuModel, VertexMergeMode vertexMergeMode, float mergeDistance, bool mergeSplitEdges)
        {
            Vertex[] vertices = new Vertex[gpuModel.Vertices.Length];

            int setIndex = 0;
            int setVertexIndex = 0;
            int setSize = gpuModel.VertexSetSizes[0];

            for(int i = 0; i < vertices.Length; i++)
            {
                GPUVertex vertex = gpuModel.Vertices[i];

                vertices[i] = new Vertex(
                    setIndex,
                    vertex.Position,
                    mergeSplitEdges ? default : vertex.Normal,
                    mergeSplitEdges ? default : vertex.Tangent
                );

                setVertexIndex++;

                if(setVertexIndex > setSize)
                {
                    setIndex++;
                    setVertexIndex = 0;
                    setSize = gpuModel.VertexSetSizes[setIndex];
                }
            }

            return vertexMergeMode == VertexMergeMode.None
                ? new(vertices, null)
                : DistinctMap.CreateDistinctMap(vertices,
                    Vertex.GetMergeComparer(
                        mergeDistance,
                        vertexMergeMode == VertexMergeMode.SubMesh,
                        !mergeSplitEdges));
        }

        public static MeshData FromHEModel(ModelBase model, VertexMergeMode vertexMergeMode, float mergeDistance, bool mergeSplitEdges)
        {
            GPUModel gpuModel = GPUModel.ReadModelData(model);

            DistinctMap<Vertex> vertexMap = GetVertices(gpuModel, vertexMergeMode, mergeDistance, mergeSplitEdges);

            int loopCount = gpuModel.Triangles.Length;

            List<int> triangleIndices = new(loopCount);
            List<Vector3>? polygonNormals = mergeSplitEdges ? new(loopCount) : null;
            List<Vector3>? polygonTangents = mergeSplitEdges ? new(loopCount) : null;

            List<Vector2>[] textureCoordinates = new List<Vector2>[gpuModel.TexcoordSets];
            for(int i = 0; i < gpuModel.TexcoordSets; i++)
            {
                textureCoordinates[i] = new(loopCount);
            }

            List<Vector4>[] colors = new List<Vector4>[gpuModel.ColorSets];
            for(int i = 0; i < gpuModel.ColorSets; i++)
            {
                colors[i] = new(loopCount);
            }

            int[] triangleSetSizes = [.. gpuModel.TriangleSetSizes];
            SortedSet<CompTri> usedTriangles = [];

            for(int i = 0; i < loopCount;)
            {
                int v1 = gpuModel.Triangles[i];
                int v2 = gpuModel.Triangles[i + 1];
                int v3 = gpuModel.Triangles[i + 2];

                int t1 = vertexMap[v1];
                int t2 = vertexMap[v2];
                int t3 = vertexMap[v3];

                if(t1 == t2 || t2 == t3 || t3 == t1 || !usedTriangles.Add(new(t1, t2, t3)))
                {
                    int triangleIndex = triangleIndices.Count / 3;
                    int offset = 0;
                    for(int j = 0; j < triangleSetSizes.Length; offset += triangleSetSizes[j], j++)
                    {
                        if(triangleIndex - offset < triangleSetSizes[j])
                        {
                            triangleSetSizes[j]--;
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
                    GPUVertex gpuVertex = gpuModel.Vertices[v1];

                    triangleIndices.Add(t1);
                    polygonNormals?.Add(gpuVertex.Normal);
                    polygonTangents?.Add(gpuVertex.Tangent);

                    for(int k = 0; k < gpuModel.TexcoordSets; k++)
                    {
                        textureCoordinates[k].Add(new(gpuVertex.TextureCoordinates[k].X, 1 - gpuVertex.TextureCoordinates[k].Y));
                    }

                    for(int k = 0; k < gpuModel.ColorSets; k++)
                    {
                        colors![k].Add(gpuVertex.Colors![k]);
                    }
                }
            }

            return new(
                model.Name,
                vertexMap.ValueArray,
                triangleIndices,
                polygonNormals,
                polygonTangents,
                textureCoordinates,
                colors,
                gpuModel.UseByteColors,
                gpuModel.SetMaterials,
                gpuModel.SetSlots,
                triangleSetSizes);
        }

    }
}
