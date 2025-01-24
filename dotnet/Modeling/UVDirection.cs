using System.Numerics;

namespace HEIO.NET.Modeling
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
    }
}
