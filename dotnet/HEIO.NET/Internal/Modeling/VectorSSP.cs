using System.Numerics;

namespace HEIO.NET.Internal.Modeling
{
    internal static class VectorSSP
    {
        /// <summary>
        /// Picked off the normal of an icosahedron
        /// </summary>
        private static readonly Vector3 _sspVector = new(
            0.7946527600288391f, 
            0.5773528218269348f, 
            0.18759159743785858f
        );

        public static float GetSSP(this Vector3 value)
        {
            return Vector3.Dot(value, _sspVector);
        }
    }
}
