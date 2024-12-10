using HEIO.NET.VertexUtils;
using SharpNeedle.Framework.HedgehogEngine.Mirage;
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


        public Vertex(Vector3 position)
        {
            Position = position;
        }

        public static EqualityComparer<Vertex> GetMergeComparer()
        {
            const float mergeDistance = 0.001f * 0.001f;

            return EqualityComparer<Vertex>.Create((v1, v2) =>
                v1.SetIndex == v2.SetIndex
                && Vector3.DistanceSquared(v1.Position, v2.Position) <= mergeDistance);
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

        public IList<Vector3> Normals { get; set; }

        public IList<Vector3> Tangents { get; set; }

        public IList<Vector2>[] TextureCoordinates { get; set; }

        public IList<IList<Vector4Int>>? ByteColors { get; set; }

        public IList<IList<Vector4>>? FloatColors { get; set; }


        public ResourceReference<Material>[] SetMaterials { get; set; }

        public MeshSlot[] SetSlots { get; }

        public int[] SetSizes { get; set; }


        public MeshData(string name, IList<Vertex> vertices, IList<int> triangleIndices, IList<Vector3> normals, IList<Vector3> tangents, IList<Vector2>[] textureCoordinates, IList<IList<Vector4Int>>? byteColors, IList<IList<Vector4>>? floatColors, ResourceReference<Material>[] setMaterials, MeshSlot[] setSlots, int[] setSizes)
        {
            Name = name;
            Vertices = vertices;
            TriangleIndices = triangleIndices;
            Normals = normals;
            Tangents = tangents;
            TextureCoordinates = textureCoordinates;
            ByteColors = byteColors;
            FloatColors = floatColors;
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

        public static MeshData FromHEModel(ModelBase model, VertexMergeMode vertexMergeMode)
        {
            GPUModel gpuModel = GPUModel.ReadModelData(model);

            Vertex[] vertices = new Vertex[gpuModel.Vertices.Length];

            int setIndex = 0;
            int setVertexIndex = 0;
            int setSize = gpuModel.VertexSetSizes[0];

            for(int i = 0; i < vertices.Length; i++)
            {
                vertices[i] = new Vertex(gpuModel.Vertices[i].Position)
                {
                    SetIndex = setIndex
                };

                if(vertexMergeMode == VertexMergeMode.SubMesh)
                {
                    setVertexIndex++;

                    if(setVertexIndex > setSize)
                    {
                        setIndex++;
                        setVertexIndex = 0;
                        setSize = gpuModel.VertexSetSizes[setIndex];
                    }
                }
            }

            DistinctMap<Vertex> vertexMap = vertexMergeMode == VertexMergeMode.None
                ? new(vertices, null)
                : DistinctMap.CreateDistinctMap(vertices, Vertex.GetMergeComparer());

            int loopCount = gpuModel.Triangles.Length;

            List<int> triangleIndices = new(loopCount);
            List<Vector3> normals = new(loopCount);
            List<Vector3> tangents = new(loopCount);

            List<Vector2>[] textureCoordinates = new List<Vector2>[gpuModel.TexcoordSets];
            for(int i = 0; i < gpuModel.TexcoordSets; i++)
            {
                textureCoordinates[i] = new(loopCount);
            }

            List<Vector4Int>[]? byteColors = null;
            List<Vector4>[]? floatColors = null;

            if(gpuModel.UseByteColors)
            {
                byteColors = new List<Vector4Int>[gpuModel.ColorSets];
                for(int i = 0; i < gpuModel.ColorSets; i++)
                {
                    byteColors[i] = new(loopCount);
                }
            }
            else
            {
                floatColors = new List<Vector4>[gpuModel.ColorSets];
                for(int i = 0; i < gpuModel.ColorSets; i++)
                {
                    floatColors[i] = new(loopCount);
                }
            }

            int[] triangleSetSizes = [..gpuModel.TriangleSetSizes];
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
                    normals.Add(gpuVertex.Normal);
                    tangents.Add(gpuVertex.Tangent);

                    for(int k = 0; k < gpuModel.TexcoordSets; k++)
                    {
                        textureCoordinates[k].Add(new(gpuVertex.TextureCoordinates[k].X, 1 - gpuVertex.TextureCoordinates[k].Y));
                    }

                    if(gpuModel.UseByteColors)
                    {
                        for(int k = 0; k < gpuModel.ColorSets; k++)
                        {
                            byteColors![k].Add(gpuVertex.ByteColors![k]);
                        }
                    }
                    else
                    {
                        for(int k = 0; k < gpuModel.ColorSets; k++)
                        {
                            floatColors![k].Add(gpuVertex.FloatColors![k]);
                        }
                    }
                }
            }

            return new(
                model.Name,
                vertexMap.ValueArray,
                triangleIndices,
                normals,
                tangents,
                textureCoordinates,
                byteColors,
                floatColors,
                gpuModel.SetMaterials,
                gpuModel.SetSlots,
                triangleSetSizes);
        }

    }
}
