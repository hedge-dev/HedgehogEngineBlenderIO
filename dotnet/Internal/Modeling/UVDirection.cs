using System.Numerics;

namespace HEIO.NET.Internal.Modeling
{
    public struct UVDirection
    {
        public Vector3 Tangent { get; set; }

        public Vector3 Binormal { get; set; }

        public UVDirection(Vector3 tangent, Vector3 binormal)
        {
            Tangent = tangent;
            Binormal = binormal;
        }

        public static bool AreNormalsEqual(Vector3 a, Vector3 b)
        {
            return Vector3.Dot(a, b) >= 0.999f;
        }
    }
}
