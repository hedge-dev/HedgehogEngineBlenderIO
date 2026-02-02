using System.Numerics;

namespace HEIO.NET.Internal.Modeling.ConvertTo
{
    internal interface IProcessable
    {
        public Vector3 AABBMin { get; }
        public Vector3 AABBMax { get; }

        public void Process(ModelVersionMode versionMode, bool compressVertexData);
    }
}
