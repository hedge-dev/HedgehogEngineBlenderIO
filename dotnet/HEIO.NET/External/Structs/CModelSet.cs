using HEIO.NET.Internal;
using SharpNeedle.Framework.HedgehogEngine.Mirage.MaterialData;
using SharpNeedle.Framework.HedgehogEngine.Needle.Archive;
using System.Collections.Generic;

namespace HEIO.NET.External.Structs
{
    public unsafe struct CModelSet : IConvertInternal<ModelSet>
    {
        public CMeshDataSet** meshDataSets;
        public int meshDataSetsSize;

        public CLODItem* lodItems;
        public int lodItemsSize;
        public byte lodUnknown1;


        public static CModelSet FromInternal(ModelSet modelSet, Dictionary<Material, nint> materialPointers)
        {
            CMeshDataSet* meshData = Allocate.AllocFromArray(modelSet.MeshDataSets, CMeshDataSet.FromInternal, materialPointers);
            CMeshDataSet** meshDataPointers = (CMeshDataSet**)Allocate.Alloc<nint>(modelSet.MeshDataSets.Length);

            for (int i = 0; i < modelSet.MeshDataSets.Length; i++)
            {
                meshDataPointers[i] = &meshData[i];
            }

            return new()
            {
                meshDataSets = meshDataPointers,
                meshDataSetsSize = modelSet.MeshDataSets.Length,

                lodItems = Allocate.AllocFromArray(modelSet.LODInfo?.Items, CLODItem.FromInternal),
                lodItemsSize = modelSet.LODInfo?.Items.Count ?? 0,
                lodUnknown1 = modelSet.LODInfo?.Unknown1 ?? 0
            };
        }

        public readonly LODInfoBlock? LODInfoToInternal()
        {
            if (lodItemsSize == 0)
            {
                return null;
            }

            return new()
            {
                Items = [.. Util.ToArray<CLODItem, LODInfoBlock.LODItem>(lodItems, lodItemsSize) ?? []],
                Unknown1 = lodUnknown1
            };
        }

        public ModelSet ToInternal()
        {
            MeshDataSet[] meshDataSets = new MeshDataSet[meshDataSetsSize];
            for (int i = 0; i < meshDataSetsSize; i++)
            {
                meshDataSets[i] = this.meshDataSets[i]->ToInternal();
            }

            return new(
                meshDataSets,
                LODInfoToInternal()
            );
        }

        public ModelSet ToInternal(Dictionary<nint, MeshDataSet> internalMeshDataSets)
        {
            MeshDataSet[] meshDataSets = new MeshDataSet[meshDataSetsSize];
            for (int i = 0; i < meshDataSetsSize; i++)
            {
                meshDataSets[i] = internalMeshDataSets[(nint)this.meshDataSets[i]];
            }

            return new(
                meshDataSets,
                LODInfoToInternal()
            );
        }
    }
}
