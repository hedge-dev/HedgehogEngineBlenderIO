using HEIO.NET.Internal.Modeling;

namespace HEIO.NET.External.Structs
{
    public unsafe struct CVertexWeight : IConvertInternal<VertexWeight>
    {
        public short index;
        public float weight;

        public CVertexWeight(VertexWeight vertexWeight)
        {
            index = vertexWeight.Index;
            weight = vertexWeight.Weight;
        }

        public static CVertexWeight FromInternal(VertexWeight vertexWeight)
        {
            return new(vertexWeight);
        }

        public readonly VertexWeight ToInternal()
        {
            return new(index, weight);
        }
    }
}
