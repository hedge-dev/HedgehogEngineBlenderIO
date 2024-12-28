using SharpNeedle.Framework.HedgehogEngine.Mirage;
using SharpNeedle.Framework.HedgehogEngine.Needle.Archive;

namespace HEIO.NET
{
    public readonly struct ModelSet
    {
        public ModelBase[] Models { get; }
        public LODInfoBlock? LODInfo { get; }

        public ModelSet(ModelBase[] models, LODInfoBlock? lODInfo)
        {
            Models = models;
            LODInfo = lODInfo;
        }
    }
}
