using HEIO.NET.Internal.Modeling.GPU;
using SharpNeedle.Framework.HedgehogEngine.Mirage.ModelData;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Numerics;

namespace HEIO.NET.Internal.Modeling.ConvertTo
{
    internal class MorphProcessor : IProcessable
    {
        public MorphModel? Result { get; private set; }
        public Vector3 AABBMin { get; private set; }
        public Vector3 AABBMax { get; private set; }

        private readonly MeshData _data;
        private readonly int _weightSets;
        private readonly Topology _topology;

        private readonly List<ProcessTriangleCorner> _triangles;
        private readonly GPUMesh _gpuMesh;

        public MorphProcessor(MeshData data, Topology topology)
        {
            AABBMin = new(float.PositiveInfinity);
            AABBMax = new(float.NegativeInfinity);

            _data = data;
            _weightSets = 1;
            _topology = topology;

            _triangles = [];
            _gpuMesh = new(
                4,
                1,
                false,
                false,
                false,
                Topology.TriangleList,
                data.MeshSets[0].Material,
                data.MeshSets[0].Slot
            );
        }

        private void EvaluateTriangleData()
        {
            foreach(Vertex vertex in _data.Vertices)
            {
                AABBMin = Vector3.Min(AABBMin, vertex.Position);
                AABBMax = Vector3.Max(AABBMax, vertex.Position);

                foreach(Vector3 morphPos in vertex.MorphPositions!)
                {
                    AABBMin = Vector3.Min(AABBMin, vertex.Position + morphPos);
                    AABBMax = Vector3.Max(AABBMax, vertex.Position + morphPos);
                }
            }

            for(int i = 0; i < _data.TriangleIndices.Count; i += 3)
            {
                for(int t = 2; t >= 0; t--)
                {
                    _triangles.Add(ProcessTriangleCorner.EvalProcessTriangles(
                        _data.TriangleIndices[i + t],
                        _data,
                        i + t,
                        _gpuMesh.TexcoordSets,
                        _gpuMesh.ColorSets
                     ));
                }
            }
        }

        public void Process(ModelVersionMode versionMode, bool optimizedVertexData)
        {
            if(Result != null)
            {
                return;
            }

            EvaluateTriangleData();

            GPUVertex[] gpuVertices = ProcessTriangleCorner.EvaluateGPUData(
                [.. _data.Vertices],
                [.. _triangles],
                _weightSets,
                out int[] gpuTriangles,
                out HashSet<short> usedBones,
                out int[] resultVertexIndices
            );

            if(usedBones.Count > 25 && versionMode != ModelVersionMode.HE2)
            {
                throw new InvalidDataException("HE1 Morph models cannot have more than 25 bones!");
            }

            ((List<GPUVertex>)_gpuMesh.Vertices).AddRange(gpuVertices);
            ((List<int>)_gpuMesh.Triangles).AddRange(gpuTriangles);
            _gpuMesh.BlendIndex16 = usedBones.Count > 255;
            _gpuMesh.EvaluateBoneIndices(usedBones);

            Mesh baseMesh = MeshConverter.ConvertToMesh(_gpuMesh, ModelVersionMode.HE1, false);

            Result = new()
            {
                MeshGroup = new()
                {
                    Name = _data.Groups[0].Name
                }
            };

            int faceOffset = 0;
            foreach(MeshDataSetInfo setInfo in _data.MeshSets)
            {
                Mesh setMesh = new()
                {
                    Slot = setInfo.Slot,
                    Material = setInfo.Material,
                    Faces = gpuTriangles.Skip(faceOffset * 3).Take(setInfo.Size * 3).Select(x => (ushort)x).ToArray(),
                    BoneIndices = baseMesh.BoneIndices,
                    VertexCount = baseMesh.VertexCount,
                    Elements = baseMesh.Elements,
                    VertexSize = baseMesh.VertexSize,
                    Vertices = baseMesh.Vertices,
                };

                if(_topology == Topology.TriangleStrips)
                {
                    ushort[][] strips = J113D.Strippify.TriangleStrippifier.Global.Strippify(setMesh.Faces);
                    List<ushort> triangles = [];

                    for(int i = 0; i < strips.Length; i++)
                    {
                        triangles.AddRange(strips[i]);

                        if(i < strips.Length - 1)
                        {
                            triangles.Add(ushort.MaxValue);
                        }
                    }

                    setMesh.Faces = [.. triangles];
                }

                Result.MeshGroup.Add(setMesh);
                faceOffset += setInfo.Size;
            }

            for(int i = 0; i < _data.MorphNames!.Count; i++)
            {
                Result.Targets.Add(new()
                {
                    Name = _data.MorphNames[i],
                    Positions = resultVertexIndices.Select(x => _data.Vertices[x].MorphPositions![i]).ToArray()
                });
            }
        }
    }
}
