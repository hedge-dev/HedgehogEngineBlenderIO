using SharpNeedle.Framework.HedgehogEngine.Mirage;
using SharpNeedle.Framework.HedgehogEngine.Mirage.MaterialData;
using SharpNeedle.Framework.HedgehogEngine.Mirage.ModelData;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Numerics;
using System.Threading.Tasks;

namespace HEIO.NET.Internal.Modeling.ConvertTo
{
    internal class ModelConverter
    {
        private static IProcessable[] ExtractProcessData(MeshDataSet compileData, Topology topology)
        {
            Dictionary<(string, MeshSlot, Material), List<TriangleData>> triangleData = [];
            List<MorphProcessor> morphProcessors = [];

            foreach(MeshData mesh in compileData.MeshData)
            {
                if(mesh.MorphNames != null && compileData.Nodes != null)
                {
                    morphProcessors.Add(new(mesh, topology));
                    continue;
                }

                int setIndex = 0;

                foreach(MeshDataMeshGroupInfo group in mesh.Groups)
                {
                    int setEnd = setIndex + group.Size;

                    for(; setIndex < setEnd; setIndex++)
                    {
                        MeshDataMeshSetInfo set = mesh.MeshSets[setIndex];

                        if(!triangleData.TryGetValue((group.Name, set.Slot, set.Material.Resource!), out List<TriangleData>? triangleDataList))
                        {
                            triangleDataList = [];
                            triangleData[(group.Name, set.Slot, set.Material.Resource!)] = triangleDataList;
                        }

                        triangleDataList.Add(new(mesh, setIndex));
                    }
                }
            }

            return [
                .. triangleData.Select(
                    x => new MeshProcessor(
                        x.Key.Item1,
                        x.Key.Item2,
                        x.Key.Item3,
                        [.. x.Value],
                        compileData.Nodes != null,
                        topology
                    )),
                .. morphProcessors
            ];
        }


        public static ModelBase[] CompileMeshData(MeshDataSet[] compileData, ModelVersionMode versionMode, Topology topology, bool compressedVertexData, bool multithreading)
        {
            IProcessable[][] processors = new IProcessable[compileData.Length][];
            void processProcessor(MeshDataSet cData, ParallelLoopState? state, long i)
            {
                IProcessable[] processor = ExtractProcessData(cData, topology);
                lock(processors)
                {
                    processors[i] = processor;
                }
            }

            if(multithreading)
            {
                ParallelLoopResult parallelLoopResult = Parallel.ForEach(compileData, processProcessor);

                if(!parallelLoopResult.IsCompleted)
                {
                    throw new InvalidOperationException("Collecting process data failed!");
                }

                parallelLoopResult = Parallel.ForEach(processors.SelectMany(x => x), (processor) => processor.Process(versionMode, compressedVertexData));

                if(!parallelLoopResult.IsCompleted)
                {
                    throw new InvalidOperationException("Converting meshdata failed!");
                }
            }
            else
            {
                for(int i = 0; i < compileData.Length; i++)
                {
                    processProcessor(compileData[i], null, i);
                }

                foreach(IProcessable processor in processors.SelectMany(x => x))
                {
                    processor.Process(versionMode, compressedVertexData);
                }
            }

            ModelBase[] result = new ModelBase[compileData.Length];

            for(int i = 0; i < compileData.Length; i++)
            {
                MeshDataSet data = compileData[i];

                ModelBase model = data.Nodes == null
                    ? new TerrainModel()
                    : new Model()
                    {
                        Nodes = [.. data.Nodes]
                    };

                model.Name = data.Name;

                model.DataVersion = versionMode switch
                {
                    ModelVersionMode.HE1 => 5,
                    ModelVersionMode.HE1_V4 => 4,
                    _ => data.Nodes?.Length > 256 ? 6u : 5u,
                };

                if(data.SampleChunkNodeRoot != null)
                {
                    model.SetupNodes();
                    SampleChunkNode dataRoot = model.Root!.Children[0];

                    dataRoot.InsertChild(0, new("UserAABB", 0));

                    if(topology != Topology.TriangleStrips)
                    {
                        // triangle list
                        dataRoot.InsertChild(0, new("Topology", 3));
                    }

                    if(data.SampleChunkNodeRoot.FindNode("NodesExt") is SampleChunkNode nodesExt)
                    {
                        dataRoot.InsertChild(0, CloneTree(nodesExt));
                    }
                }

                Dictionary<string, MeshGroup> groups = [];

                Vector3 aabbMin = new(float.PositiveInfinity);
                Vector3 aabbMax = new(float.NegativeInfinity);

                foreach(IProcessable processor in processors[i])
                {
                    aabbMin = Vector3.Min(aabbMin, processor.AABBMin);
                    aabbMax = Vector3.Max(aabbMax, processor.AABBMax);

                    if(processor is MeshProcessor meshProcessor)
                    {
                        if(!groups.TryGetValue(meshProcessor.GroupName, out MeshGroup? group))
                        {
                            group = new()
                            {
                                Name = meshProcessor.GroupName
                            };

                            groups[meshProcessor.GroupName] = group;
                            model.Groups.Add(group);
                        }

                        group.AddRange(meshProcessor.Result!);
                    }
                    else if(processor is MorphProcessor morphProcessor)
                    {
                        Model modelmodel2 = (Model)model;
                        modelmodel2.Morphs ??= [];
                        modelmodel2.Morphs!.Add(morphProcessor.Result!);
                    }

                }

                if(model is Model modelmodel)
                {
                    modelmodel.Bounds = new(aabbMin, aabbMax);
                }

                result[i] = model;
            }

            return result;
        }

        private static SampleChunkNode CloneTree(SampleChunkNode root)
        {
            SampleChunkNode result = new(root.Name, root.Value);

            foreach (SampleChunkNode node in root)
            {
                result.AddChild(CloneTree(node));
            }

            return result;
        }
    }
}
