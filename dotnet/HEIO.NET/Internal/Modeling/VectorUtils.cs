using System.Numerics;

namespace HEIO.NET.Internal.Modeling
{
    internal static class VectorUtils
    {
        /// <summary>
        /// Picked off the normal of an icosahedron
        /// </summary>
        private static readonly Vector3 _sspVector = new(
            0.7946527600288391f, 
            0.5773528218269348f, 
            0.18759159743785858f
        );

        public static float GetPositionSSP(this Vector3 value)
        {
            return Vector3.Dot(value, _sspVector);
        }

        public static bool CompareArrayDistances(Vector3[] a, Vector3[] b, float mergeDistanceSquared)
        {
            for (int i = 0; i < a.Length; i++)
            {
                if (Vector3.DistanceSquared(a[i], b[i]) >= mergeDistanceSquared)
                {
                    return false;
                }
            }

            return true;
        }
    }
}
