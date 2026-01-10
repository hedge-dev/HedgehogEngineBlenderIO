using HEIO.NET.Modeling;

namespace HEIO.NET.Modeling.ConvertTo
{
    internal readonly struct TriangleData
    {
        public readonly MeshData data;
        public readonly int setIndex;

        public TriangleData(MeshData data, int setIndex)
        {
            this.data = data;
            this.setIndex = setIndex;
        }
    }
}
