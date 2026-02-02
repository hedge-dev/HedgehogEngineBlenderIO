using HEIO.NET.Internal.Modeling;
using System.Numerics;

namespace HEIO.NET.External.Structs
{
    public unsafe struct CUVDirection : IConvertInternal<UVDirection>
    {
        public Vector3 tangent;
        public Vector3 binormal;

        public CUVDirection(UVDirection direction)
        {
            tangent = direction.Tangent;
            binormal = direction.Binormal;
        }

        public static CUVDirection FromInternal(UVDirection direction)
        {
            return new(direction);
        }

        public readonly UVDirection ToInternal()
        {
            return new(tangent, binormal);
        }
    }
}
