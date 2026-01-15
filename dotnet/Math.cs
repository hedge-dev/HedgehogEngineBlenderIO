using System;
using System.Numerics;
using System.Runtime.InteropServices;

namespace HEIO.NET
{
    public static class Math
    {
        [UnmanagedCallersOnly(EntryPoint = "matrix_decompose")]
        public static unsafe void MatrixDecompose(Matrix4x4 matrix, Vector3* position, Quaternion* rotation, Vector3* scale)
        {
            try
            {
                Matrix4x4.Decompose(matrix, out *scale, out *rotation, out *position);
            }
            catch (Exception exception)
            {
                ErrorHandler.HandleError(exception);
                return;
            }
        }

        [UnmanagedCallersOnly(EntryPoint = "matrix_create_translation")]
        public static Matrix4x4 CreateTranslationMatrix(Vector3 position)
        {
            try
            {
                return Matrix4x4.CreateTranslation(position);
            }
            catch (Exception exception)
            {
                ErrorHandler.HandleError(exception);
                return default;
            }
        }

        [UnmanagedCallersOnly(EntryPoint = "matrix_create_rotation")]
        public static Matrix4x4 CreateRotationMatrix(Vector3 eulerRotation)
        {
            try
            {
                float sX = MathF.Sin(eulerRotation.X);
                float cX = MathF.Cos(eulerRotation.X);

                float sY = MathF.Sin(eulerRotation.Y);
                float cY = MathF.Cos(eulerRotation.Y);

                float sZ = MathF.Sin(eulerRotation.Z);
                float cZ = MathF.Cos(eulerRotation.Z);

                // equal to matX * matY * matZ
                return new()
                {
                    M11 = cZ * cY,
                    M12 = sZ * cY,
                    M13 = -sY,

                    M21 = (cZ * sY * sX) - (sZ * cX),
                    M22 = (sZ * sY * sX) + (cZ * cX),
                    M23 = cY * sX,

                    M31 = (cZ * sY * cX) + (sZ * sX),
                    M32 = (sZ * sY * cX) - (cZ * sX),
                    M33 = cY * cX,

                    M44 = 1
                };
            }
            catch (Exception exception)
            {
                ErrorHandler.HandleError(exception);
                return default;
            }
        }

        [UnmanagedCallersOnly(EntryPoint = "matrix_create_scale")]
        public static Matrix4x4 CreateScaleMatrix(Vector3 scale)
        {
            try
            {
                return Matrix4x4.CreateScale(scale);
            }
            catch (Exception exception)
            {
                ErrorHandler.HandleError(exception);
                return default;
            }
        }

        [UnmanagedCallersOnly(EntryPoint = "matrix_multiply")]
        public static Matrix4x4 MultiplyMatrix(Matrix4x4 a, Matrix4x4 b)
        {
            try
            {
                return a * b;
            }
            catch (Exception exception)
            {
                ErrorHandler.HandleError(exception);
                return default;
            }
        }

        [UnmanagedCallersOnly(EntryPoint = "quaternion_create_from_rotation_matrix")]
        public static Quaternion CreateFromRotationMatrix(Matrix4x4 matrix)
        {
            try
            {
                return Quaternion.CreateFromRotationMatrix(matrix);
            }
            catch (Exception exception)
            {
                ErrorHandler.HandleError(exception);
                return default;
            }
        }

        [UnmanagedCallersOnly(EntryPoint = "matrix_invert")]
        public static Matrix4x4 InvertMatrix(Matrix4x4 matrix)
        {
            try
            {
                if (Matrix4x4.Invert(matrix, out Matrix4x4 result))
                {
                    return result;
                }
                else
                {
                    return Matrix4x4.Identity;
                }
            }
            catch (Exception exception)
            {
                ErrorHandler.HandleError(exception);
                return default;
            }
        }

        [UnmanagedCallersOnly(EntryPoint = "matrix_create_from_quaternion")]
        public static Matrix4x4 CreateMatrixFromQuaternion(Quaternion quaternion)
        {
            try
            {
                return Matrix4x4.CreateFromQuaternion(quaternion);
            }
            catch (Exception exception)
            {
                ErrorHandler.HandleError(exception);
                return default;
            }
        }
    }
}
