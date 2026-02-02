using SharpNeedle.Framework.HedgehogEngine.Mirage.ModelData;
using SharpNeedle.Framework.HedgehogEngine.Needle.Archive;
using System;

namespace HEIO.NET.Internal
{
    public static class ModelHelper
    {
        public static NeedleArchive CreateLODArchive(ModelBase[] models, byte[] lodCascades, float[] lodUnknowns)
        {
            NeedleArchive result = new()
            {
                OffsetMode = NeedleArchiveDataOffsetMode.SelfRelative
            };

            LODInfoBlock lodBlock = new()
            {
                Unknown1 = 4
            };
            result.DataBlocks.Add(lodBlock);

            (ModelBase model, byte lodCascade, float lodUnknown)[] items = new (ModelBase model, byte lodCascade, float lodUnknown)[models.Length];
            for (int i = 0; i < items.Length; i++)
            {
                items[i] = (models[i], lodCascades[i], lodUnknowns[i]);
            }

            Array.Sort(items, (a, b) => a.lodCascade.CompareTo(b.lodCascade));

            if (items[^1].lodCascade != 31)
            {
                lodBlock.Unknown1 |= 0x80;
            }

            foreach ((ModelBase model, byte lodCascade, float lodUnknown) in items)
            {
                if (lodCascade > 31)
                {
                    throw new ArgumentException($"Invalid LOD cascade level {lodCascades} for model {models[0].Name}!", nameof(lodCascades));
                }

                lodBlock.Items.Add(new()
                {
                    CascadeFlag = 1 << lodCascade,
                    Unknown2 = lodUnknown,
                    CascadeLevel = lodCascade
                });

                result.DataBlocks.Add(new ModelBlock()
                {
                    Resource = model
                });
            }


            return result;
        }
    }
}
