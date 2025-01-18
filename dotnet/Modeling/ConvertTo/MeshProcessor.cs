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
    internal class MeshProcessor : IProcessable
    {
        public string GroupName { get; }
        public Mesh[]? Result { get; private set; }
        public Vector3 AABBMin { get; private set; }
        public Vector3 AABBMax { get; private set; }

        private readonly TriangleData[] _triangleData;
        private readonly int _weightSets;
        private readonly Topology _topology;

        private readonly List<Vertex> _vertices;
        private readonly List<ProcessTriangleCorner> _triangles;

        private readonly GPUMesh _gpuMesh;

        public MeshProcessor(string groupName, MeshSlot slot, Material material, TriangleData[] triangleData, bool addWeights, Topology topology)
        {
            GroupName = groupName;

            _triangleData = triangleData;
            _weightSets = addWeights ? (triangleData.Any(x => x.data.MeshSets[x.setIndex].Enable8Weights) ? 2 : 1) : 0;
            _topology = topology;

            _vertices = [];
            _triangles = [];

            AABBMin = new(float.PositiveInfinity);
            AABBMax = new(float.NegativeInfinity);

            _gpuMesh = new(
                int.Clamp(_triangleData.Max(x => x.data.TextureCoordinates.Count), 1, 4),
                1,
                _triangleData.All(x => x.data.MeshSets[x.setIndex].UseByteColors),
                false,
                triangleData.Any(x => x.data.MeshSets[x.setIndex].EnableMultiTangent),
                Topology.TriangleList,
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

                        _triangles.Add(ProcessTriangleCorner.EvalProcessTriangles(
                            newVertexIndex,
                            triangleData.data,
                            faceIndex,
                            _gpuMesh.TexcoordSets,
                            _gpuMesh.ColorSets
                        ));
                    }
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

                gpuMesh.EvaluateBoneIndices(boneIndices);

                result[i] = gpuMesh;
            }

            return result;
        }


        public void Process(bool hedgehogEngine2, bool optimizedVertexData)
        {
            if(Result != null)
            {
                return;
            }

            EvaluateTriangleData();

            GPUVertex[] gpuVertices = ProcessTriangleCorner.EvaluateGPUData(
                [.. _vertices],
                [.. _triangles],
                _weightSets,
                out int[] gpuTriangles,
                out HashSet<short> usedBones,
                out _
            );

            ((List<GPUVertex>)_gpuMesh.Vertices).AddRange(gpuVertices);
            ((List<int>)_gpuMesh.Triangles).AddRange(gpuTriangles);

            GPUMesh[] gpuMeshes;

            if(usedBones.Count <= 25 || hedgehogEngine2)
            {
                _gpuMesh.BlendIndex16 = usedBones.Count > 255;
                _gpuMesh.EvaluateBoneIndices(usedBones);
                gpuMeshes = [_gpuMesh];
            }
            else
            {
                gpuMeshes = BoneLimitSplit(25);
            }

            if(_topology == Topology.TriangleStrips)
            {
                foreach(GPUMesh gpuMesh in gpuMeshes)
                {
                    gpuMesh.ToStrips();
                }
            }

            Result = gpuMeshes.Select(x => MeshConverter.ConvertToMesh(x, hedgehogEngine2, optimizedVertexData)).ToArray();
        }
    }
}
