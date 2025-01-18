using HEIO.NET.Modeling.GPU;
using SharpNeedle.Framework.HedgehogEngine.Mirage;
using System;
using System.Collections;
using System.Collections.Generic;
using System.ComponentModel;
using System.Linq;
using System.Numerics;

namespace HEIO.NET.Modeling.ConvertTo
{
    internal class MeshProcessor
    {
        public string GroupName { get; }

        public Mesh[]? Result { get; private set; }

        public Vector3 AABBMin { get; private set; }

        public Vector3 AABBMax { get; private set; }

        private readonly TriangleData[] _triangleData;
        private readonly int _weightSets;

        private readonly List<Vertex> _vertices;
        private readonly List<ProcessTriangleCorner> _triangles;
        private readonly HashSet<short> _usedBones;

        private readonly GPUMesh _gpuMesh;

        public MeshProcessor(string groupName, MeshSlot slot, Material material, TriangleData[] triangleData, bool addWeights, Topology topology)
        {
            GroupName = groupName;

            _triangleData = triangleData;
            _weightSets = addWeights ? (triangleData.Any(x => x.data.MeshSets[x.setIndex].Enable8Weights) ? 2 : 1) : 0;

            _vertices = [];
            _triangles = [];
            _usedBones = [];

            AABBMin = new(float.PositiveInfinity);
            AABBMax = new(float.NegativeInfinity);

            _gpuMesh = new(
                int.Clamp(_triangleData.Max(x => x.data.TextureCoordinates.Count), 1, 4),
                1,
                _triangleData.All(x => x.data.UseByteColors),
                false,
                triangleData.Any(x => x.data.EnableMultiTangent),
                topology,
                material,
                slot
            );
        }

        private void EvaluateTriangleData()
        {
            foreach(TriangleData triangleData in _triangleData)
            {
                int[] vertexIndexMap = new int[triangleData.data.Vertices.Count];
                Array.Fill(vertexIndexMap, -1);

                int start = triangleData.data.MeshSets.Take(triangleData.setIndex).Sum(x => x.Size);
                int end = start + triangleData.data.MeshSets[triangleData.setIndex].Size;

                for(int i = start; i < end; i++)
                {
                    for(int t = 2; t >= 0; t--)
                    {
                        int faceIndex = (i * 3) + t;

                        int vertexIndex = triangleData.data.TriangleIndices[faceIndex];
                        int newVertexIndex = vertexIndexMap[vertexIndex];
                        if(newVertexIndex == -1)
                        {
                            newVertexIndex = _vertices.Count;
                            Vertex vertex = triangleData.data.Vertices[vertexIndex];
                            _vertices.Add(vertex);
                            AABBMin = Vector3.Min(AABBMin, vertex.Position);
                            AABBMax = Vector3.Max(AABBMax, vertex.Position);
                            vertexIndexMap[vertexIndex] = newVertexIndex;
                        }

                        Vector2[] textureCoordinates = new Vector2[_gpuMesh.TexcoordSets];
                        for(int j = 0; j < triangleData.data.TextureCoordinates.Count; j++)
                        {
                            Vector2 uv = triangleData.data.TextureCoordinates[j][faceIndex];
                            textureCoordinates[j] = new(uv.X, 1 - uv.Y);
                        }

                        Vector2 fallbackTextureCoordinate = triangleData.data.TextureCoordinates.Count == 0
                            ? Vector2.Zero : triangleData.data.TextureCoordinates[0][faceIndex];

                        for(int j = triangleData.data.TextureCoordinates.Count; j < _gpuMesh.TexcoordSets; j++)
                        {
                            textureCoordinates[j] = fallbackTextureCoordinate;
                        }

                        Vector4[] colors = new Vector4[_gpuMesh.ColorSets];

                        for(int j = 0; j < triangleData.data.Colors.Count; j++)
                        {
                            colors[j] = triangleData.data.Colors[j][faceIndex];
                        }

                        Vector4 fallbackColor = triangleData.data.Colors.Count == 0
                            ? Vector4.One : triangleData.data.Colors[0][faceIndex];

                        for(int j = triangleData.data.Colors.Count; j < _gpuMesh.ColorSets; j++)
                        {
                            colors[j] = fallbackColor;
                        }

                        _triangles.Add(new(
                            newVertexIndex,
                            triangleData.data.PolygonTangents![faceIndex],
                            textureCoordinates,
                            colors
                        ));
                    }
                }
            }
        }

        private void EvaluateGPUData()
        {
            if(J113D.Common.DistinctMap.TryCreateDistinctMap([.. _triangles], out J113D.Common.DistinctMap<ProcessTriangleCorner> cornerMap))
            {
                ((List<int>)_gpuMesh.Triangles).AddRange(cornerMap.Map!);
            }
            else
            {
                ((List<int>)_gpuMesh.Triangles).AddRange(Enumerable.Range(0, _triangles.Count));
            }

            ProcessTriangleCorner[] distinctCorners = cornerMap.ValueArray;
            int weightCount = _weightSets * 4;

            for(int i = 0; i < distinctCorners.Length; i++)
            {
                ProcessTriangleCorner corner = distinctCorners[i];
                Vertex vertex = _vertices[corner.vertexIndex];

                GPUVertex gpuVertex = new(_gpuMesh.TexcoordSets, _gpuMesh.ColorSets, weightCount)
                {
                    Position = vertex.Position,
                    Normal = vertex.Normal,
                    Tangent = corner.tangent
                };

                for(int j = 0; j < _gpuMesh.TexcoordSets; j++)
                {
                    gpuVertex.TextureCoordinates[j] = corner.textureCoordinates[j];
                }

                for(int j = 0; j < _gpuMesh.ColorSets; j++)
                {
                    gpuVertex.Colors[j] = corner.colors[j];
                }

                if(weightCount != 0)
                {
                    TransferWeights(vertex.Weights, gpuVertex.Weights);
                }

                _gpuMesh.Vertices.Add(gpuVertex);
            }
        }

        private void TransferWeights(VertexWeight[] input, VertexWeight[] output)
        {
            if(input.Length == 0)
            {
                _usedBones.Add(0);
                output[0] = new(0, 1);
                return;
            }

            int limit = int.Min(output.Length, input.Length);
            int j = 0;
            float sum = 0;
            foreach(VertexWeight weight in input.OrderByDescending(x => x.Weight))
            {
                _usedBones.Add(weight.Index);
                output[j] = weight;
                sum += weight.Weight;

                j++;
                if(j >= limit)
                {
                    break;
                }
            }

            if(sum != 1f)
            {
                sum = 1f / sum;
                for(j = 0; j < limit; j++)
                {
                    output[j].Weight *= sum;
                }
            }
        }

        private GPUMesh[] BoneLimitSplit(int boneLimit)
        {
            short[][] vertexBoneIndices = _gpuMesh.Vertices.Select(x => x.Weights.Where(x => x.Weight > 0).Select(x => x.Index).ToArray()).ToArray();

            List<(List<int> cornerIndices, HashSet<short> boneIndices)> boneSets = [];
            HashSet<short> tempBoneIndices = [];
            HashSet<short> tempBoneIndices2 = [];

            for(int i = 0; i < _gpuMesh.Triangles.Count; i += 3)
            {
                int v1 = _gpuMesh.Triangles[i];
                int v2 = _gpuMesh.Triangles[i + 1];
                int v3 = _gpuMesh.Triangles[i + 2];

                tempBoneIndices.Clear();
                tempBoneIndices.UnionWith(vertexBoneIndices[v1]);
                tempBoneIndices.UnionWith(vertexBoneIndices[v2]);
                tempBoneIndices.UnionWith(vertexBoneIndices[v3]);

                bool found = false;

                foreach((List<int> vertexIndices, HashSet<short> boneIndices) in boneSets)
                {
                    tempBoneIndices2.Clear();
                    tempBoneIndices2.UnionWith(tempBoneIndices);
                    tempBoneIndices2.UnionWith(boneIndices);

                    if(tempBoneIndices2.Count <= boneLimit)
                    {
                        boneIndices.UnionWith(tempBoneIndices);
                        vertexIndices.Add(v1);
                        vertexIndices.Add(v2);
                        vertexIndices.Add(v3);
                        found = true;
                        break;
                    }
                }

                if(!found)
                {
                    List<int> cornerIndices = [v1, v2, v3];
                    HashSet<short> boneIndices = new(tempBoneIndices);
                    boneSets.Add((cornerIndices, boneIndices));
                }
            }

            GPUMesh[] result = new GPUMesh[boneSets.Count];
            int[] indexMap = new int[_gpuMesh.Vertices.Count];

            for(int i = 0; i < result.Length; i++)
            {
                (List<int> vertexIndices, HashSet<short> boneIndices) = boneSets[i];

                GPUMesh gpuMesh = new(
                    _gpuMesh.TexcoordSets,
                    _gpuMesh.ColorSets,
                    _gpuMesh.UseByteColors,
                    _gpuMesh.BlendIndex16,
                    _gpuMesh.MultiTangent,
                    _gpuMesh.Topology,
                    _gpuMesh.Material,
                    _gpuMesh.Slot
                );

                Array.Fill(indexMap, -1);

                foreach(int vertexIndex in vertexIndices)
                {
                    int newVertexIndex = indexMap[vertexIndex];

                    if(newVertexIndex == -1)
                    {
                        newVertexIndex = gpuMesh.Vertices.Count;
                        gpuMesh.Vertices.Add(_gpuMesh.Vertices[vertexIndex].Copy());
                        indexMap[vertexIndex] = newVertexIndex;
                    }

                    gpuMesh.Triangles.Add(newVertexIndex);
                }

                EvaluateBoneIndices(gpuMesh, boneIndices);

                result[i] = gpuMesh;
            }

            return result;
        }

        private static void EvaluateBoneIndices(GPUMesh gpuMesh, HashSet<short> usedBones)
        {
            if(usedBones.Count == 0)
            {
                return;
            }

            ((List<short>)gpuMesh.BoneIndices).AddRange(usedBones.Order());

            if(usedBones.Max() <= gpuMesh.BoneIndices.Count - 1)
            {
                return;
            }

            short[] boneMap = new short[usedBones.Max() + 2];
            boneMap[0] = -1;
            for(short i = 0; i < gpuMesh.BoneIndices.Count; i++)
            {
                boneMap[gpuMesh.BoneIndices[i] + 1] = i;
            }

            for(int i = 0; i < gpuMesh.Vertices.Count; i++)
            {
                VertexWeight[] weights = gpuMesh.Vertices[i].Weights;
                for(int j = 0; j < weights.Length; j++)
                {
                    weights[j].Index = boneMap[weights[j].Index + 1];
                }
            }
        }

        private static void EvaluateStrips(GPUMesh gpuMesh)
        {
            int[][] strips = J113D.Strippify.TriangleStrippifier.Global.Strippify([.. gpuMesh.Triangles]);
            List<int> triangles = (List<int>)gpuMesh.Triangles;
            triangles.Clear();

            for(int i = 0; i < strips.Length; i++)
            {
                triangles.AddRange(strips[i]);

                if(i < strips.Length - 1)
                {
                    triangles.Add(ushort.MaxValue);
                }
            }
        }

        public Mesh[] Process(bool hedgehogEngine2, bool optimizedVertexData)
        {
            if(Result == null)
            {
                EvaluateTriangleData();
                EvaluateGPUData();

                GPUMesh[] gpuMeshes;

                if(_usedBones.Count <= 25 || hedgehogEngine2)
                {
                    _gpuMesh.BlendIndex16 = _usedBones.Count > 255;
                    EvaluateBoneIndices(_gpuMesh, _usedBones);
                    gpuMeshes = [_gpuMesh];
                }
                else
                {
                    gpuMeshes = BoneLimitSplit(25);
                }

                foreach(GPUMesh gpuMesh in gpuMeshes)
                {
                    if(gpuMesh.Topology == Topology.TriangleStrips)
                    {
                        EvaluateStrips(gpuMesh);
                    }
                }

                Result = gpuMeshes.Select(x => MeshConverter.ConvertToMesh(x, hedgehogEngine2, optimizedVertexData)).ToArray();
            }

            return Result;
        }
    }
}
