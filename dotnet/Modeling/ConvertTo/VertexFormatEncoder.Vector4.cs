using Amicitia.IO.Binary;
using System;
using System.Numerics;

namespace HEIO.NET.Modeling.ConvertTo
{
    internal static partial class VertexFormatEncoder
    {
        private static void EncodeFloat4(BinaryObjectWriter writer, Vector4 value)
        {
            writer.WriteSingle(value.X);
            writer.WriteSingle(value.Y);
            writer.WriteSingle(value.Z);
            writer.WriteSingle(value.W);
        }

        private static void EncodeInt4(BinaryObjectWriter writer, Vector4 value)
        {
            writer.WriteInt32((int)value.X);
            writer.WriteInt32((int)value.Y);
            writer.WriteInt32((int)value.Z);
            writer.WriteInt32((int)value.W);
        }

        private static void EncodeInt4Norm(BinaryObjectWriter writer, Vector4 value)
        {
            writer.WriteInt32((int)(float.Clamp(value.X, -1, 1) * int.MaxValue));
            writer.WriteInt32((int)(float.Clamp(value.Y, -1, 1) * int.MaxValue));
            writer.WriteInt32((int)(float.Clamp(value.Z, -1, 1) * int.MaxValue));
            writer.WriteInt32((int)(float.Clamp(value.W, -1, 1) * int.MaxValue));
        }

        private static void EncodeUint4(BinaryObjectWriter writer, Vector4 value)
        {
            writer.WriteUInt32((uint)value.X);
            writer.WriteUInt32((uint)value.Y);
            writer.WriteUInt32((uint)value.Z);
            writer.WriteUInt32((uint)value.W);
        }

        private static void EncodeUint4Norm(BinaryObjectWriter writer, Vector4 value)
        {
            writer.WriteUInt32((uint)(float.Clamp(value.X, 0, 1) * uint.MaxValue));
            writer.WriteUInt32((uint)(float.Clamp(value.Y, 0, 1) * uint.MaxValue));
            writer.WriteUInt32((uint)(float.Clamp(value.Z, 0, 1) * uint.MaxValue));
            writer.WriteUInt32((uint)(float.Clamp(value.W, 0, 1) * uint.MaxValue));
        }

        private static void EncodeUByte4(BinaryObjectWriter writer, Vector4 value)
        {
            writer.WriteByte((byte)value.X);
            writer.WriteByte((byte)value.Y);
            writer.WriteByte((byte)value.Z);
            writer.WriteByte((byte)value.W);
        }

        private static void EncodeByte4(BinaryObjectWriter writer, Vector4 value)
        {
            sbyte x = (sbyte)value.X;
            sbyte y = (sbyte)value.Y;
            sbyte z = (sbyte)value.Z;
            sbyte w = (sbyte)value.W;

            writer.WriteByte(unchecked((byte)x));
            writer.WriteByte(unchecked((byte)y));
            writer.WriteByte(unchecked((byte)z));
            writer.WriteByte(unchecked((byte)w));
        }

        private static void EncodeUByte4Norm(BinaryObjectWriter writer, Vector4 value)
        {
            writer.WriteByte((byte)(float.Clamp(value.X, 0, 1) * byte.MaxValue));
            writer.WriteByte((byte)(float.Clamp(value.Y, 0, 1) * byte.MaxValue));
            writer.WriteByte((byte)(float.Clamp(value.Z, 0, 1) * byte.MaxValue));
            writer.WriteByte((byte)(float.Clamp(value.W, 0, 1) * byte.MaxValue));
        }

        private static void EncodeByte4Norm(BinaryObjectWriter writer, Vector4 value)
        {
            sbyte x = (sbyte)(float.Clamp(value.X, -1, 1) * sbyte.MaxValue);
            sbyte y = (sbyte)(float.Clamp(value.Y, -1, 1) * sbyte.MaxValue);
            sbyte z = (sbyte)(float.Clamp(value.Z, -1, 1) * sbyte.MaxValue);
            sbyte w = (sbyte)(float.Clamp(value.W, -1, 1) * sbyte.MaxValue);

            writer.WriteByte(unchecked((byte)x));
            writer.WriteByte(unchecked((byte)y));
            writer.WriteByte(unchecked((byte)z));
            writer.WriteByte(unchecked((byte)w));
        }

        private static void EncodeShort4(BinaryObjectWriter writer, Vector4 value)
        {
            writer.WriteInt16((short)value.X);
            writer.WriteInt16((short)value.Y);
            writer.WriteInt16((short)value.Z);
            writer.WriteInt16((short)value.W);
        }

        private static void EncodeShort4Norm(BinaryObjectWriter writer, Vector4 value)
        {
            writer.WriteInt16((short)(float.Clamp(value.X, -1, 1) * short.MaxValue));
            writer.WriteInt16((short)(float.Clamp(value.Y, -1, 1) * short.MaxValue));
            writer.WriteInt16((short)(float.Clamp(value.Z, -1, 1) * short.MaxValue));
            writer.WriteInt16((short)(float.Clamp(value.W, -1, 1) * short.MaxValue));
        }

        private static void EncodeUShort4(BinaryObjectWriter writer, Vector4 value)
        {
            writer.WriteUInt16((ushort)value.X);
            writer.WriteUInt16((ushort)value.Y);
            writer.WriteUInt16((ushort)value.Z);
            writer.WriteUInt16((ushort)value.W);
        }

        private static void EncodeUShort4Norm(BinaryObjectWriter writer, Vector4 value)
        {
            writer.WriteUInt16((ushort)(float.Clamp(value.X, 0, 1) * ushort.MaxValue));
            writer.WriteUInt16((ushort)(float.Clamp(value.Y, 0, 1) * ushort.MaxValue));
            writer.WriteUInt16((ushort)(float.Clamp(value.Z, 0, 1) * ushort.MaxValue));
            writer.WriteUInt16((ushort)(float.Clamp(value.W, 0, 1) * ushort.MaxValue));
        }

        private static void EncodeUDec4(BinaryObjectWriter writer, Vector4 value)
        {
            writer.WriteUInt32(
                (((uint)value.X) & 0x1FF)
                | ((((uint)value.Y) & 0x1FF) << 10)
                | ((((uint)value.Z) & 0x1FF) << 20)
                | (((uint)value.W) << 30)
            );
        }

        private static void EncodeDec4(BinaryObjectWriter writer, Vector4 value)
        {
            writer.WriteUInt32(
                FromSigned10((int)value.X)
                | (FromSigned10((int)value.Y) << 10)
                | (FromSigned10((int)value.Z) << 20)
                | (FromSigned2((int)value.W) << 30)
            );
        }

        private static void EncodeUDec4Norm(BinaryObjectWriter writer, Vector4 value)
        {
            writer.WriteUInt32(
                ((uint)(float.Clamp(value.X, 0, 1) * 0x3FF))
                | (((uint)(float.Clamp(value.Y, 0, 1) * 0x3FF)) << 10)
                | (((uint)(float.Clamp(value.Z, 0, 1) * 0x3FF)) << 20)
                | (((uint)(float.Clamp(value.W, 0, 1) * 0x3)) << 30)
            );
        }

        private static void EncodeDec4Norm(BinaryObjectWriter writer, Vector4 value)
        {
            writer.WriteUInt32(
                FromSigned10((int)(float.Clamp(value.X, -1, 1) * 0x1FF))
                | (FromSigned10((int)(float.Clamp(value.Y, -1, 1) * 0x1FF)) << 10)
                | (FromSigned10((int)(float.Clamp(value.Z, -1, 1) * 0x1FF)) << 20)
                | (FromSigned2((int)float.Clamp(value.W, -1, 1)) << 30)
            );
        }

        private static void EncodeFloat16_4(BinaryObjectWriter writer, Vector4 value)
        {
            writer.WriteUInt16(BitConverter.HalfToUInt16Bits((Half)value.X));
            writer.WriteUInt16(BitConverter.HalfToUInt16Bits((Half)value.Y));
            writer.WriteUInt16(BitConverter.HalfToUInt16Bits((Half)value.Z));
            writer.WriteUInt16(BitConverter.HalfToUInt16Bits((Half)value.W));
        }


    }
}
