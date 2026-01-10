using SharpNeedle.Framework.HedgehogEngine.Mirage.MaterialData;
using System;
using System.Numerics;

namespace HEIO.NET.Internal
{
    public static class PythonHelpers
    {
        public static MaterialParameter<Vector4> CreateFloatParameter(Vector4 value)
        {
            return new()
            {
                Value = value
            };
        }

        public static MaterialParameter<bool> CreateBoolParameter(bool value)
        {
            return new()
            {
                Value = value
            };
        }

        public static Matrix4x4 CreateRotationMatrix(Vector3 rotation)
        {
            float sX = MathF.Sin(rotation.X);
            float cX = MathF.Cos(rotation.X);

            float sY = MathF.Sin(rotation.Y);
            float cY = MathF.Cos(rotation.Y);

            float sZ = MathF.Sin(rotation.Z);
            float cZ = MathF.Cos(rotation.Z);

            // equal to matX * matY * matZ
            return new()
            {
                M11 = cZ * cY,
                M12 = sZ * cY,
                M13 = -sY,

                M21 = cZ * sY * sX - sZ * cX,
                M22 = sZ * sY * sX + cZ * cX,
                M23 = cY * sX,

                M31 = cZ * sY * cX + sZ * sX,
                M32 = sZ * sY * cX - cZ * sX,
                M33 = cY * cX,

                M44 = 1
            };
        }

        public static Vector3 ToEuler(Matrix4x4 matrix)
        {
            const double threshold = 16 * 1.192092896e-07;
            double cy = double.Hypot(matrix.M11, matrix.M12);

            if(cy > threshold)
            {
                return new(
                    MathF.Atan2(matrix.M23, matrix.M33),
                    MathF.Atan2(-matrix.M13, (float)cy),
                    MathF.Atan2(matrix.M12, matrix.M11)
                );

            }
            else
            {
                return new(
                    MathF.Atan2(-matrix.M32, matrix.M22),
                    MathF.Atan2(-matrix.M13, (float)cy),
                    0f
                );
            }
        }
    }
}
