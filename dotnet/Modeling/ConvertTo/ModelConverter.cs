using SharpNeedle.Framework.HedgehogEngine.Mirage;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Numerics;
using System.Threading.Tasks;

namespace HEIO.NET.Modeling.ConvertTo
{
    internal class ModelConverter
    {
        private static MeshProcessor[] ExtractProcessData(MeshCompileData compileData, Topology topology)
        {
            Dictionary<(string, MeshSlot, Material), List<TriangleData>> triangleData = [];

            foreach(MeshData mesh in compileData.MeshData)
            {
                int setIndex = 0;

                for(int i = 0; i < mesh.GroupNames.Count; i++)
                {
                    string groupName = mesh.GroupNames[i];

                    int setEnd = setIndex + mesh.GroupSetCounts[i];
                    for(; setIndex < setEnd; setIndex++)
                    {
                        MeshDataSetInfo set = mesh.MeshSets[setIndex];

                        if(!triangleData.TryGetValue((groupName, set.Slot, set.Material.Resource!), out List<TriangleData>? triangleDataList))
                        {
                            triangleDataList = [];
                            triangleData[(groupName, set.Slot, set.Material.Resource!)] = triangleDataList;
                        }

                        triangleDataList.Add(new(mesh, setIndex));
                    }
                }
            }

            return [.. triangleData.Select(
                x => new MeshProcessor(
                    x.Key.Item1,
                    x.Key.Item2,
                    x.Key.Item3,
                    [.. x.Value],
                    compileData.Nodes != null,
                    topology
            ))];
        }


        public static ModelBase[] CompileMeshData(MeshCompileData[] compileData, bool hedgehogEngine2, Topology topology, bool optimizedVertexData)
        {
            List<MeshProcessor> processors = [];
            List<int> processDataSizes = [];

            ParallelLoopResult parallelLoopResult = Parallel.ForEach(compileData, (cData, _, i) =>
            {
                MeshProcessor[] processor = ExtractProcessData(cData, topology);
                lock(processors)
                    lock(processDataSizes)
                    {
                        processors.AddRange(processor);
                        processDataSizes.Add(processor.Length);
                    }
            });

            if(!parallelLoopResult.IsCompleted)
            {
                throw new InvalidOperationException("Collecting process data failed!");
            }

            parallelLoopResult = Parallel.ForEach(processors, (processor) => processor.Process(hedgehogEngine2, optimizedVertexData));

            if(!parallelLoopResult.IsCompleted)
            {
                throw new InvalidOperationException("Converting meshdata failed!");
            }

            ModelBase[] result = new ModelBase[compileData.Length];

            int processorOffset = 0;
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
                model.DataVersion = hedgehogEngine2 && data.Nodes?.Length > 256 ? 6u : 5u;
                
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

                int end = processorOffset + processDataSizes[i];
                for(; processorOffset < end; processorOffset++)
                {
                    MeshProcessor processor = processors[processorOffset];

                    aabbMin = Vector3.Min(aabbMin, processor.AABBMin);
                    aabbMax = Vector3.Max(aabbMax, processor.AABBMax);

                    if(!groups.TryGetValue(processor.GroupName, out MeshGroup? group))
                    {
                        group = new()
                        {
                            Name = processor.GroupName
                        };

                        groups[processor.GroupName] = group;
                        model.Groups.Add(group);
                    }

                    group.AddRange(processor.Result!);   
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
