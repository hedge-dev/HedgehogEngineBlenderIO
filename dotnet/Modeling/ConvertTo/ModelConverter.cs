using SharpNeedle.Framework.HedgehogEngine.Mirage;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;

namespace HEIO.NET.Modeling.ConvertTo
{
    internal class ModelConverter
    {
        private static MeshProcessor[] ExtractProcessData(MeshCompileData compileData)
        {
            Dictionary<(string, MeshSlot, Material), List<TriangleData>> triangleData = [];

            foreach(MeshData mesh in compileData.MeshData)
            {
                int triangleOffset = 0;
                int setIndex = 0;

                for(int i = 0; i < mesh.GroupNames.Count; i++)
                {
                    int groupSize = mesh.GroupSizes[i];
                    string groupName = mesh.GroupNames[i];
                    int groupTriangleOffset = 0;

                    while(groupTriangleOffset < groupSize)
                    {
                        int setSize = mesh.SetSizes[setIndex];
                        MeshSlot slot = mesh.SetSlots[setIndex];
                        Material material = mesh.SetMaterials[setIndex].Resource!;

                        if(!triangleData.TryGetValue((groupName, slot, material), out List<TriangleData>? triangleDataList))
                        {
                            triangleDataList = [];
                            triangleData[(groupName, slot, material)] = triangleDataList;
                        }

                        triangleDataList.Add(new(mesh, triangleOffset, setSize));

                        triangleOffset += setSize;
                        groupTriangleOffset += setSize;
                        setIndex++;
                    }
                }
            }

            return [.. triangleData.Select(
                x => new MeshProcessor(
                    x.Key.Item1,
                    x.Key.Item2,
                    x.Key.Item3,
                    [.. x.Value],
                    compileData.Nodes == null ? 0 : 1
            ))];
        }


        public static ModelBase[] CompileMeshData(MeshCompileData[] compileData)
        {
            List<MeshProcessor> processors = [];
            List<int> processDataSizes = [];

            ParallelLoopResult parallelLoopResult = Parallel.ForEach(compileData, (cData, _, i) =>
            {
                MeshProcessor[] processor = ExtractProcessData(cData);
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

            parallelLoopResult = Parallel.ForEach(processors, (processor) => processor.Process());

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
                model.DataVersion = 5;

                Dictionary<string, MeshGroup> groups = [];

                int end = processorOffset + processDataSizes[i];
                for(; processorOffset < end; processorOffset++)
                {
                    MeshProcessor processor = processors[processorOffset];
                    if(!groups.TryGetValue(processor.GroupName, out MeshGroup? group))
                    {
                        group = new()
                        {
                            Name = processor.GroupName
                        };

                        groups[processor.GroupName] = group;
                        model.Groups.Add(group);
                    }

                    group.Add(processor.Result!);
                }

                result[i] = model;
            }

            return result;
        }

    }
}
