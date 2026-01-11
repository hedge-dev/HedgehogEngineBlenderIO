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
        private static IProcessable[] ExtractProcessData(MeshCompileData compileData, Topology topology)
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

                foreach(MeshDataGroupInfo group in mesh.Groups)
                {
                    int setEnd = setIndex + group.Size;

                    for(; setIndex < setEnd; setIndex++)
                    {
                        MeshDataSetInfo set = mesh.MeshSets[setIndex];

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


        public static ModelBase[] CompileMeshData(MeshCompileData[] compileData, ModelVersionMode versionMode, Topology topology, bool optimizedVertexData, bool multithreading)
        {
            IProcessable[][] processors = new IProcessable[compileData.Length][];
            void processProcessor(MeshCompileData cData, ParallelLoopState? state, long i)
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

                parallelLoopResult = Parallel.ForEach(processors.SelectMany(x => x), (processor) => processor.Process(versionMode, optimizedVertexData));

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
                    processor.Process(versionMode, optimizedVertexData);
                }
            }

            ModelBase[] result = new ModelBase[compileData.Length];

            for(int i = 0; i < compileData.Length; i++)
            {
                MeshCompileData data = compileData[i];

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

                if(data.SCAParameters != null)
                {
                    model.SetupNodes();
                    SampleChunkNode dataRoot = model.Root!.Children[0];

                    dataRoot.InsertChild(0, new("UserAABB", 0));

                    if(topology != Topology.TriangleStrips)
                    {
                        // triangle list
                        dataRoot.InsertChild(0, new("Topology", 3));
                    }

                    if(data.SCAParameters.Length > 0)
                    {

                        SampleChunkNode nodesExt = new("NodesExt", 1);
                        dataRoot.InsertChild(0, nodesExt);

                        foreach(SampleChunkNode scaParameter in data.SCAParameters)
                        {
                            nodesExt.AddChild(scaParameter);
                        }
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

    }
}
