using SharpNeedle.Framework.HedgehogEngine.Mirage;
using System.Numerics;

namespace HEIO.NET
{
    public static class PythonHelpers
    {
        public static Material.Parameter<Vector4> CreateFloatParameter(Vector4 value)
        {
            return new()
            {
                Value = value
            };
        }

        public static Material.Parameter<bool> CreateBoolParameter(bool value)
        {
            return new()
            {
                Value = value
            };
        }

        public static Matrix4x4 InvertMatrix(Matrix4x4 matrix)
        {
            Matrix4x4.Invert(matrix, out Matrix4x4 result);
            return result;
        }
    }
}
