using HEIO.NET.Modeling.GPU;
using SharpNeedle.Framework.HedgehogEngine.Mirage;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Numerics;
using System.Runtime.ExceptionServices;

namespace HEIO.NET.Modeling.ConvertTo
{
    internal class MeshProcessor : IProcessable
    {
        public string GroupName { get; }
        public Mesh[]? Result { get; private set; }
        public Vector3 AABBMin { get; private set; }
        public Vector3 AABBMax { get; private set; }

        private readonly TriangleData[] _triangleData;
        private readonly MeshSlot _slot;
        private readonly Material _material;

        private readonly Topology _topology;
        private readonly int _texcoordSets;
        private readonly bool[] _texcoordSetsUsed;
        private readonly int _weightSets;

        private readonly List<Vertex> _vertices;
        private readonly List<ProcessTriangleCorner> _triangles;

        public MeshProcessor(string groupName, MeshSlot slot, Material material, TriangleData[] triangleData, bool addWeights, Topology topology)
        {
            GroupName = groupName;

            _triangleData = triangleData;
            _slot = slot;
            _material = material;

            _topology = topology;
            _weightSets = addWeights ? (triangleData.Any(x => x.data.MeshSets[x.setIndex].Enable8Weights) ? 2 : 1) : 0;
            _texcoordSets = int.Clamp(_triangleData.Max(x => x.data.TextureCoordinates.Count), 1, 4);
            _texcoordSetsUsed = new bool[_texcoordSets];

            _vertices = [];
            _triangles = [];

            AABBMin = new(float.PositiveInfinity);
            AABBMax = new(float.NegativeInfinity);
        }

        private void EvaluateTriangleData()
        {
            foreach(TriangleData triangleData in _triangleData)
            {
                int[] vertexIndexMap = new int[triangleData.data.Vertices.Count];
                Array.Fill(vertexIndexMap, -1);

                int start = triangleData.data.MeshSets.Take(triangleData.setIndex).Sum(x => x.Size);
                int end = start + triangleData.data.MeshSets[triangleData.setIndex].Size;
                int texcoordCount = int.Min(_texcoordSets, triangleData.data.TextureCoordinates.Count);

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

                        ProcessTriangleCorner corner = ProcessTriangleCorner.EvalProcessTriangles(
                            newVertexIndex,
                            triangleData.data,
                            faceIndex,
                            _texcoordSets,
                            1
                        );

                        for(int j = 1; j < texcoordCount; j++)
                        {
                            Vector2 uv = triangleData.data.TextureCoordinates[j][faceIndex];
                            _texcoordSetsUsed[j] |= uv.X != 0f || uv.Y != 0f;
                        }

                        _triangles.Add(corner);
                    }
                }
            }
        }

        private static GPUMesh[] BoneLimitSplit(GPUMesh gpuMesh, int boneLimit)
        {
            short[][] vertexBoneIndices = gpuMesh.Vertices.Select(x => x.Weights.Where(x => x.Weight > 0).Select(x => x.Index).ToArray()).ToArray();

            List<(List<int> cornerIndices, HashSet<short> boneIndices)> boneSets = [];
            HashSet<short> tempBoneIndices = [];
            HashSet<short> tempBoneIndices2 = [];

            for(int i = 0; i < gpuMesh.Triangles.Count; i += 3)
            {
                int v1 = gpuMesh.Triangles[i];
                int v2 = gpuMesh.Triangles[i + 1];
                int v3 = gpuMesh.Triangles[i + 2];

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
            int[] indexMap = new int[gpuMesh.Vertices.Count];

            for(int i = 0; i < result.Length; i++)
            {
                (List<int> vertexIndices, HashSet<short> boneIndices) = boneSets[i];

                GPUMesh splitGpuMesh = new(
                    gpuMesh.TexcoordSets,
                    gpuMesh.ColorSets,
                    gpuMesh.UseByteColors,
                    gpuMesh.BlendIndex16,
                    gpuMesh.MultiTangent,
                    gpuMesh.Topology,
                    gpuMesh.Material,
                    gpuMesh.Slot
                );

                Array.Fill(indexMap, -1);

                foreach(int vertexIndex in vertexIndices)
                {
                    int newVertexIndex = indexMap[vertexIndex];

                    if(newVertexIndex == -1)
                    {
                        newVertexIndex = splitGpuMesh.Vertices.Count;
                        splitGpuMesh.Vertices.Add(splitGpuMesh.Vertices[vertexIndex].Copy());
                        indexMap[vertexIndex] = newVertexIndex;
                    }

                    splitGpuMesh.Triangles.Add(newVertexIndex);
                }

                splitGpuMesh.EvaluateBoneIndices(boneIndices);

                result[i] = splitGpuMesh;
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

            int realTexcoordCount = _texcoordSets;

            for(; realTexcoordCount > 1; realTexcoordCount--)
            {
                if(_texcoordSetsUsed[realTexcoordCount - 1])
                {
                    break;
                }
            }

            GPUMesh gpuMesh = new(
                realTexcoordCount,
                1,
                _triangleData.All(x => x.data.MeshSets[x.setIndex].UseByteColors),
                false,
                _triangleData.Any(x => x.data.MeshSets[x.setIndex].EnableMultiTangent),
                Topology.TriangleList,
                _material,
                _slot
            );

            ((List<GPUVertex>)gpuMesh.Vertices).AddRange(gpuVertices);
            ((List<int>)gpuMesh.Triangles).AddRange(gpuTriangles);

            GPUMesh[] gpuMeshes;

            if(usedBones.Count <= 25 || hedgehogEngine2)
            {
                gpuMesh.BlendIndex16 = usedBones.Count > 255;
                gpuMesh.EvaluateBoneIndices(usedBones);
                gpuMeshes = [gpuMesh];
            }
            else
            {
                gpuMeshes = BoneLimitSplit(gpuMesh, 25);
            }

            if(_topology == Topology.TriangleStrips)
            {
                foreach(GPUMesh arrayGpuMesh in gpuMeshes)
                {
                    arrayGpuMesh.ToStrips();
                }
            }

            Result = gpuMeshes.Select(x => MeshConverter.ConvertToMesh(x, hedgehogEngine2, optimizedVertexData)).ToArray();
        }
    }
}
