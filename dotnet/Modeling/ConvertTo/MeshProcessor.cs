using HEIO.NET.Modeling.GPU;
using SharpNeedle.Framework.HedgehogEngine.Mirage;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Numerics;

namespace HEIO.NET.Modeling.ConvertTo
{
    internal class MeshProcessor
    {
        public string GroupName { get; }

        public Mesh? Result { get; private set; }

        private readonly TriangleData[] _triangleData;
        private readonly int _weightSets;

        private readonly List<Vertex> _vertices;
        private readonly List<ProcessTriangleCorner> _triangles;
        private readonly HashSet<short> _usedBones;

        private readonly GPUMesh _gpuMesh;

        public MeshProcessor(string groupName, MeshSlot slot, Material material, TriangleData[] triangleData, int weightSets)
        {
            GroupName = groupName;

            _triangleData = triangleData;
            _weightSets = weightSets;

            _vertices = [];
            _triangles = [];
            _usedBones = [];

            _gpuMesh = new(
                int.Clamp(_triangleData.Max(x => x.data.TextureCoordinates.Count), 1, 4),
                1,
                _triangleData.All(x => x.data.UseByteColors),
                Topology.TriangleStrips,
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

                int end = triangleData.offset + triangleData.size;

                for(int i = triangleData.offset; i < end; i++)
                {
                    for(int t = 2; t >= 0; t--)
                    {
                        int faceIndex = (i * 3) + t;

                        int vertexIndex = triangleData.data.TriangleIndices[faceIndex];
                        int newVertexIndex = vertexIndexMap[vertexIndex];
                        if(newVertexIndex == -1)
                        {
                            newVertexIndex = _vertices.Count;
                            _vertices.Add(triangleData.data.Vertices[vertexIndex]);
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
            int[][] strips = J113D.Strippify.TriangleStrippifier.Global.Strippify([.. _triangles], out J113D.Common.DistinctMap<ProcessTriangleCorner> cornerMap);

            ProcessTriangleCorner[] distinctCorners = cornerMap.ValueArray;
            int weightCount = _weightSets * 4;

            for(int i = 0; i < distinctCorners.Length; i++)
            {
                ProcessTriangleCorner corner = distinctCorners[i];
                Vertex vertex = _vertices[corner.vertexIndex];

                GPUVertex gpuVertex = new(_gpuMesh.TexcoordSets, _gpuMesh.ColorSets, weightCount, _gpuMesh.UseByteColors)
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

            int stripOffset = 0;
            for(int i = 0; i < strips.Length; i++)
            {
                int[] strip = strips[i];

                ((List<int>)_gpuMesh.Triangles).AddRange(strip);
                stripOffset += strip.Length;

                if(i < strips.Length - 1)
                {
                    _gpuMesh.Triangles.Add(ushort.MaxValue);
                    stripOffset++;
                }
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

        private void EvaluateBoneIndices()
        {
            ((List<short>)_gpuMesh.BoneIndices).AddRange(_usedBones.Order());

            if(_usedBones.Max() <= _gpuMesh.BoneIndices.Count - 1)
            {
                return;
            }

            short[] boneMap = new short[_usedBones.Max() + 2];
            boneMap[0] = -1;
            for(short i = 0; i < _gpuMesh.BoneIndices.Count; i++)
            {
                boneMap[_gpuMesh.BoneIndices[i] + 1] = i;
            }

            for(int i = 0; i < _gpuMesh.Vertices.Count; i++)
            {
                VertexWeight[] weights = _gpuMesh.Vertices[i].Weights;
                for(int j = 0; j < weights.Length; j++)
                {
                    weights[j].Index = boneMap[weights[j].Index + 1];
                }
            }
        }

        public Mesh Process()
        {
            if(Result == null)
            {
                EvaluateTriangleData();
                EvaluateGPUData();
                EvaluateBoneIndices();
                Result = MeshConverter.ConvertToMesh(_gpuMesh);
            }

            return Result;
        }
    }
}
