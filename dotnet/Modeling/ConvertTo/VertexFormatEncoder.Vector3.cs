using Amicitia.IO.Binary;
using System.Numerics;

namespace HEIO.NET.Modeling.ConvertTo
{
    internal static partial class VertexFormatEncoder
	{
		private static void EncodeFloat3(BinaryObjectWriter writer, Vector3 value)
        {
            writer.WriteSingle(value.X);
            writer.WriteSingle(value.Y);
            writer.WriteSingle(value.Z);
        }

		private static void EncodeUDec3(BinaryObjectWriter writer, Vector3 value)
		{
            writer.WriteUInt32(
                (((uint)value.X) & 0x1FF)
                | ((((uint)value.Y) & 0x1FF) << 10)
                | ((((uint)value.Z) & 0x1FF) << 20)
            );
        }

		private static void EncodeDec3(BinaryObjectWriter writer, Vector3 value)
		{
            writer.WriteUInt32(
                FromSigned10((int)value.X)
                | (FromSigned10((int)value.Y) << 10)
                | (FromSigned10((int)value.Z) << 20)
            );
        }

		private static void EncodeUDec3Norm(BinaryObjectWriter writer, Vector3 value)
		{
            writer.WriteUInt32(
                ((uint)(float.Clamp(value.X, 0, 1) * 0x3FF))
                | (((uint)(float.Clamp(value.Y, 0, 1) * 0x3FF)) << 10)
                | (((uint)(float.Clamp(value.Z, 0, 1) * 0x3FF)) << 20)
            );
        }

		private static void EncodeDec3Norm(BinaryObjectWriter writer, Vector3 value)
		{
            writer.WriteUInt32(
                FromSigned10((int)(float.Clamp(value.X, -1, 1) * 0x1FF))
                | (FromSigned10((int)(float.Clamp(value.Y, -1, 1) * 0x1FF)) << 10)
                | (FromSigned10((int)(float.Clamp(value.Z, -1, 1) * 0x1FF)) << 20)
            );
        }

		private static void EncodeUHend3(BinaryObjectWriter writer, Vector3 value)
		{
            writer.WriteUInt32(
                (((uint)value.X) & 0x7FF)
                | ((((uint)value.Y) & 0x7FF) << 11)
                | (((uint)value.Z) << 22)
            );
		}

		private static void EncodeHend3(BinaryObjectWriter writer, Vector3 value)
		{
            writer.WriteUInt32(
                FromSigned11((int)value.X)
                | (FromSigned11((int)value.Y) << 11)
                | (FromSigned10((int)value.Z) << 22)
            );
		}

		private static void EncodeUhend3Norm(BinaryObjectWriter writer, Vector3 value)
		{
            writer.WriteUInt32(
                ((uint)(float.Clamp(value.X, 0, 1) * 0x7FF))
                | (((uint)(float.Clamp(value.Y, 0, 1) * 0x7FF)) << 11)
                | (((uint)(float.Clamp(value.Z, 0, 1) * 0x3FF)) << 22)
            );
		}

		private static void EncodeHend3Norm(BinaryObjectWriter writer, Vector3 value)
		{
            writer.WriteUInt32(
                FromSigned11((int)(float.Clamp(value.X, -1, 1) * 0x3FF))
                | (FromSigned11((int)(float.Clamp(value.Y, -1, 1) * 0x3FF)) << 11)
                | (FromSigned10((int)(float.Clamp(value.Z, -1, 1) * 0x1FF)) << 22)
            );
		}

        private static void EncodeUDHen3(BinaryObjectWriter writer, Vector3 value)
        {
            writer.WriteUInt32(
                (((uint)value.X) & 0x1FF)
                | ((((uint)value.Y) & 0x7FF) << 10)
                | (((uint)value.Z) << 21)
            );
        }

        private static void EncodeDHen3(BinaryObjectWriter writer, Vector3 value)
        {
            writer.WriteUInt32(
                FromSigned10((int)value.X)
                | (FromSigned11((int)value.Y) << 10)
                | (FromSigned11((int)value.Z) << 21)
            );
        }

        private static void EncodeUDhen3Norm(BinaryObjectWriter writer, Vector3 value)
        {
            writer.WriteUInt32(
                ((uint)(float.Clamp(value.X, 0, 1) * 0x3FF))
                | (((uint)(float.Clamp(value.Y, 0, 1) * 0x7FF)) << 10)
                | (((uint)(float.Clamp(value.Z, 0, 1) * 0x7FF)) << 21)
            );
        }

        private static void EncodeDHen3Norm(BinaryObjectWriter writer, Vector3 value)
        {
            writer.WriteUInt32(
                FromSigned10((int)(float.Clamp(value.X, -1, 1) * 0x1FF))
                | (FromSigned11((int)(float.Clamp(value.Y, -1, 1) * 0x3FF)) << 10)
                | (FromSigned11((int)(float.Clamp(value.Z, -1, 1) * 0x3FF)) << 21)
            );
        }

	}
}
