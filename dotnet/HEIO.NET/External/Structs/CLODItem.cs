using SharpNeedle.Framework.HedgehogEngine.Needle.Archive;

namespace HEIO.NET.External.Structs
{
    public unsafe struct CLODItem : IConvertInternal<LODInfoBlock.LODItem>
    {
        public int cascadeFlag;
        public float unknown2;
        public byte cascadeLevel;

        public CLODItem(LODInfoBlock.LODItem item)
        {
            cascadeFlag = item.CascadeFlag;
            unknown2 = item.Unknown2;
            cascadeLevel = item.CascadeLevel;
        }

        public static CLODItem FromInternal(LODInfoBlock.LODItem item)
        {
            return new(item);
        }

        public LODInfoBlock.LODItem ToInternal()
        {
            return new()
            {
                CascadeFlag = cascadeFlag,
                Unknown2 = unknown2,
                CascadeLevel = cascadeLevel
            };
        }
    }
}
