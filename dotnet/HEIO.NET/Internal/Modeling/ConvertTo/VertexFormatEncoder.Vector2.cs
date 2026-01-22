using Amicitia.IO.Binary;
using System;
using System.Numerics;

namespace HEIO.NET.Internal.Modeling.ConvertTo
{
    internal static partial class VertexFormatEncoder
    {
        private static void EncodeFloat2(BinaryObjectWriter writer, Vector2 value)
        {
            writer.WriteSingle(value.X);
            writer.WriteSingle(value.Y);
        }

        private static void EncodeInt2(BinaryObjectWriter writer, Vector2 value)
        {
            writer.WriteInt32((int)value.X);
            writer.WriteInt32((int)value.Y);
        }

        private static void EncodeUint2(BinaryObjectWriter writer, Vector2 value)
        {
            writer.WriteUInt32((uint)value.X);
            writer.WriteUInt32((uint)value.Y);
        }

        private static void EncodeInt2Norm(BinaryObjectWriter writer, Vector2 value)
        {
            writer.WriteInt32((int)(float.Clamp(value.X, -1, 1) * int.MaxValue));
            writer.WriteInt32((int)(float.Clamp(value.Y, -1, 1) * int.MaxValue));
        }

        private static void EncodeUint2Norm(BinaryObjectWriter writer, Vector2 value)
        {
            writer.WriteUInt32((uint)(float.Clamp(value.X, 0, 1) * uint.MaxValue));
            writer.WriteUInt32((uint)(float.Clamp(value.Y, 0, 1) * uint.MaxValue));
        }

        private static void EncodeShort2(BinaryObjectWriter writer, Vector2 value)
        {
            writer.WriteInt16((short)value.X);
            writer.WriteInt16((short)value.Y);
        }

        private static void EncodeUShort2(BinaryObjectWriter writer, Vector2 value)
        {
            writer.WriteUInt16((ushort)value.X);
            writer.WriteUInt16((ushort)value.Y);
        }

        private static void EncodeShort2Norm(BinaryObjectWriter writer, Vector2 value)
        {
            writer.WriteInt16((short)(float.Clamp(value.X, -1, 1) * short.MaxValue));
            writer.WriteInt16((short)(float.Clamp(value.Y, -1, 1) * short.MaxValue));
        }

        private static void EncodeUShort2Norm(BinaryObjectWriter writer, Vector2 value)
        {
            writer.WriteUInt16((ushort)(float.Clamp(value.X, 0, 1) * ushort.MaxValue));
            writer.WriteUInt16((ushort)(float.Clamp(value.Y, 0, 1) * ushort.MaxValue));
        }

        private static void EncodeFloat16_2(BinaryObjectWriter writer, Vector2 value)
        {
            writer.WriteUInt16(BitConverter.HalfToUInt16Bits((Half)value.X));
            writer.WriteUInt16(BitConverter.HalfToUInt16Bits((Half)value.Y));
        }
    }
}
