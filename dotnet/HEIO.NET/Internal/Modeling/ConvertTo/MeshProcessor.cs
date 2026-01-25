using HEIO.NET.Internal.Modeling.GPU;
using J113D.Common;
using SharpNeedle.Framework.HedgehogEngine.Mirage.MaterialData;
using SharpNeedle.Framework.HedgehogEngine.Mirage.ModelData;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Numerics;
using System.Reflection;

namespace HEIO.NET.Internal.Modeling.ConvertTo
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
        private readonly bool _enableMultiTangent;

        private readonly List<Vertex> _vertices;
        private readonly List<ProcessTriangleCorner> _triangles;

        public MeshProcessor(string groupName, MeshSlot slot, Material material, TriangleData[] triangleData, bool addWeights, Topology topology)
        {
            GroupName = groupName;

            _triangleData = triangleData;
            _slot = slot;
            _material = material;

            _topology = topology;
            _weightSets = addWeights ? triangleData.Any(x => x.data.MeshSets[x.setIndex].Enable8Weights) ? 2 : 1 : 0;
            _texcoordSets = int.Clamp(_triangleData.Max(x => x.data.TextureCoordinates.Count), 1, 4);
            _texcoordSetsUsed = new bool[_texcoordSets];
            _enableMultiTangent = _triangleData.Any(x => x.data.MeshSets[x.setIndex].EnableMultiTangent);

            _vertices = [];
            _triangles = [];

            AABBMin = new(float.PositiveInfinity);
            AABBMax = new(float.NegativeInfinity);
        }

        private void EvaluateTriangleData()
        {
            foreach (TriangleData triangleData in _triangleData)
            {
                int[] vertexIndexMap = new int[triangleData.data.Vertices.Count];
                Array.Fill(vertexIndexMap, -1);

                int start = triangleData.data.MeshSets.Take(triangleData.setIndex).Sum(x => x.Size);
                int end = start + triangleData.data.MeshSets[triangleData.setIndex].Size;
                int texcoordCount = int.Min(_texcoordSets, triangleData.data.TextureCoordinates.Count);

                for (int i = start; i < end; i++)
                {
                    for (int t = 2; t >= 0; t--)
                    {
                        int faceIndex = i * 3 + t;

                        int vertexIndex = triangleData.data.TriangleIndices[faceIndex];
                        int newVertexIndex = vertexIndexMap[vertexIndex];
                        if (newVertexIndex == -1)
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
                            1,
                            _enableMultiTangent
                        );

                        for (int j = 1; j < texcoordCount; j++)
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

            for (int i = 0; i < gpuMesh.Triangles.Count; i += 3)
            {
                int v1 = gpuMesh.Triangles[i];
                int v2 = gpuMesh.Triangles[i + 1];
                int v3 = gpuMesh.Triangles[i + 2];

                tempBoneIndices.Clear();
                tempBoneIndices.UnionWith(vertexBoneIndices[v1]);
                tempBoneIndices.UnionWith(vertexBoneIndices[v2]);
                tempBoneIndices.UnionWith(vertexBoneIndices[v3]);

                bool found = false;

                foreach ((List<int> vertexIndices, HashSet<short> boneIndices) in boneSets)
                {
                    tempBoneIndices2.Clear();
                    tempBoneIndices2.UnionWith(tempBoneIndices);
                    tempBoneIndices2.UnionWith(boneIndices);

                    if (tempBoneIndices2.Count <= boneLimit)
                    {
                        boneIndices.UnionWith(tempBoneIndices);
                        vertexIndices.Add(v1);
                        vertexIndices.Add(v2);
                        vertexIndices.Add(v3);
                        found = true;
                        break;
                    }
                }

                if (!found)
                {
                    List<int> cornerIndices = [v1, v2, v3];
                    HashSet<short> boneIndices = new(tempBoneIndices);
                    boneSets.Add((cornerIndices, boneIndices));
                }
            }

            GPUMesh[] result = new GPUMesh[boneSets.Count];
            int[] indexMap = new int[gpuMesh.Vertices.Count];

            for (int i = 0; i < result.Length; i++)
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

                foreach (int vertexIndex in vertexIndices)
                {
                    int newVertexIndex = indexMap[vertexIndex];

                    if (newVertexIndex == -1)
                    {
                        newVertexIndex = splitGpuMesh.Vertices.Count;
                        splitGpuMesh.Vertices.Add(gpuMesh.Vertices[vertexIndex].Copy());
                        indexMap[vertexIndex] = newVertexIndex;
                    }

                    splitGpuMesh.Triangles.Add(newVertexIndex);
                }

                splitGpuMesh.EvaluateBoneIndices(boneIndices);

                result[i] = splitGpuMesh;
            }

            return result;
        }


        private static GPUMesh[] VertexLimitSplit(GPUMesh gpuMesh)
        {
            const int vertexLimit = ushort.MaxValue + 1;

            List<GPUMesh> result = [];

            List<GPUVertex> gpuVertices = [];
            List<int> triangles = [];

            int[] indexMap = new int[gpuMesh.Triangles.Count];
            Array.Fill(indexMap, -1);

            List<int> nextIndices = [.. gpuMesh.Triangles];

            while(nextIndices.Count > 0)
            {
                int[] currentIndices = [.. nextIndices];
                nextIndices.Clear();

                for (int i = 0; i < currentIndices.Length; i += 3)
                {
                    int t1 = currentIndices[i];
                    int t2 = currentIndices[i + 1];
                    int t3 = currentIndices[i + 2];

                    int v1 = indexMap[t1];
                    int v2 = indexMap[t2];
                    int v3 = indexMap[t3];

                    int unavailableCount =
                        (v1 != 0 ? 1 : 0)
                        + (v2 != 0 ? 1 : 0)
                        + (v3 != 0 ? 1 : 0);

                    if (unavailableCount > 0)
                    {
                        if (gpuVertices.Count + unavailableCount > vertexLimit)
                        {
                            nextIndices.Add(t1);
                            nextIndices.Add(t2);
                            nextIndices.Add(t3);
                            continue;
                        }

                        if(v1 == -1)
                        {
                            v1 = gpuVertices.Count;
                            indexMap[t1] = v1;
                            gpuVertices.Add(gpuMesh.Vertices[t1]);
                        }

                        if (v2 == -1)
                        {
                            v2 = gpuVertices.Count;
                            indexMap[t2] = v2;
                            gpuVertices.Add(gpuMesh.Vertices[t2]);
                        }

                        if (v3 == -1)
                        {
                            v3 = gpuVertices.Count;
                            indexMap[t3] = v3;
                            gpuVertices.Add(gpuMesh.Vertices[t3]);
                        }
                    }

                    triangles.Add(v1);
                    triangles.Add(v2);
                    triangles.Add(v3);
                }

                result.Add(new(
                    [.. gpuVertices],
                    gpuMesh.TexcoordSets,
                    gpuMesh.ColorSets,
                    gpuMesh.UseByteColors,
                    gpuMesh.BlendIndex16,
                    gpuMesh.MultiTangent,
                    gpuMesh.Topology,
                    [.. triangles],
                    [.. gpuMesh.BoneIndices],
                    gpuMesh.Material,
                    gpuMesh.Slot
                ));

                gpuVertices.Clear();
                triangles.Clear();
                Array.Fill(indexMap, -1);
            }

            return [.. result];
        }

        private static GPUMesh[] VertexLimitSplitStrips(GPUMesh gpuMesh)
        {
            const int vertexLimit = ushort.MaxValue;

            List<GPUMesh> result = [];

            List<GPUVertex> gpuVertices = [];
            List<int> triangles = [];

            int[] indexMap = new int[gpuMesh.Triangles.Count];
            Array.Fill(indexMap, -1);

            List<int> nextIndices = [.. gpuMesh.Triangles];
            List<int> newStrip = [];

            while (nextIndices.Count > 0)
            {
                int[] currentIndices = [.. nextIndices];
                nextIndices.Clear();

                void addStrip()
                {
                    int unavailableCount = 0;
                    foreach(int index in newStrip.Distinct())
                    {
                        if (indexMap[index] == -1)
                        {
                            unavailableCount++;
                        }
                    }

                    if (unavailableCount > 0 && gpuVertices.Count + unavailableCount > vertexLimit)
                    {
                        nextIndices.AddRange(newStrip);
                        nextIndices.Add(-1);
                    }
                    else
                    {
                        for(int i = 0; i < newStrip.Count; i++)
                        {
                            int index = newStrip[i];
                            int vertexIndex = indexMap[index];

                            if (vertexIndex == -1)
                            {
                                vertexIndex = gpuVertices.Count;
                                indexMap[index] = vertexIndex;
                                gpuVertices.Add(gpuMesh.Vertices[index]);
                            }

                            newStrip[i] = vertexIndex;
                        }

                        triangles.AddRange(newStrip);
                        triangles.Add(-1);
                    }

                    newStrip.Clear();
                }

                for(int i = 0; i < currentIndices.Length; i++)
                {
                    int index = currentIndices[i];
                    if(index == -1)
                    {
                        addStrip();
                    }
                    else
                    {
                        newStrip.Add(index);
                    }
                }

                if(newStrip.Count > 0)
                {
                    addStrip();
                }

                result.Add(new(
                    [.. gpuVertices],
                    gpuMesh.TexcoordSets,
                    gpuMesh.ColorSets,
                    gpuMesh.UseByteColors,
                    gpuMesh.BlendIndex16,
                    gpuMesh.MultiTangent,
                    gpuMesh.Topology,
                    [.. triangles[..^1]], // removing last -1
                    [.. gpuMesh.BoneIndices], 
                    gpuMesh.Material,
                    gpuMesh.Slot
                ));

                gpuVertices.Clear();
                triangles.Clear();
                Array.Fill(indexMap, -1);
            }

            return [.. result];
        }

        public void Process(ModelVersionMode versionMode, bool optimizedVertexData)
        {
            if (Result != null)
            {
                return;
            }

            EvaluateTriangleData();

            GPUVertex[] gpuVertices = ProcessTriangleCorner.EvaluateGPUData(
                [.. _vertices],
                [.. _triangles],
                _weightSets,
                out int[] gpuTriangles,
                out HashSet<short> usedBones
            );

            int realTexcoordCount = _texcoordSets;

            for (; realTexcoordCount > 1; realTexcoordCount--)
            {
                if (_texcoordSetsUsed[realTexcoordCount - 1])
                {
                    break;
                }
            }

            GPUMesh gpuMesh = new(
                realTexcoordCount,
                1,
                _triangleData.All(x => x.data.MeshSets[x.setIndex].UseByteColors),
                false,
                _enableMultiTangent,
                Topology.TriangleList,
                _material,
                _slot
            );

            ((List<GPUVertex>)gpuMesh.Vertices).AddRange(gpuVertices);
            ((List<int>)gpuMesh.Triangles).AddRange(gpuTriangles);

            GPUMesh[] gpuMeshes;

            if (usedBones.Count <= 25 || versionMode == ModelVersionMode.HE2)
            {
                gpuMesh.BlendIndex16 = usedBones.Count > 255;
                gpuMesh.EvaluateBoneIndices(usedBones);
                gpuMeshes = [gpuMesh];
            }
            else
            {
                gpuMeshes = BoneLimitSplit(gpuMesh, 25);
            }

            ushort vertexLimit;
            Func<GPUMesh, GPUMesh[]> vertexLimitSplit;

            if (_topology == Topology.TriangleStrips)
            {
                foreach (GPUMesh arrayGpuMesh in gpuMeshes)
                {
                    arrayGpuMesh.ToStrips();
                }

                vertexLimit = ushort.MaxValue - 1;
                vertexLimitSplit = VertexLimitSplitStrips;
            }
            else
            {
                vertexLimit = ushort.MaxValue;
                vertexLimitSplit = VertexLimitSplit;
            }

            if (gpuMeshes.Any(x => x.Vertices.Count > vertexLimit))
            {
                List<GPUMesh> splitMeshes = [];

                foreach (GPUMesh splitMesh in gpuMeshes)
                {
                    if (splitMesh.Vertices.Count > vertexLimit)
                    {
                        splitMeshes.AddRange(vertexLimitSplit(splitMesh));
                    }
                    else
                    {
                        splitMeshes.Add(splitMesh);
                    }
                }

                gpuMeshes = [.. splitMeshes];
            }

            Result = gpuMeshes.Select(x => MeshConverter.ConvertToMesh(x, versionMode, optimizedVertexData)).ToArray();
        }
    }
}
