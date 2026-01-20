using Amicitia.IO.Binary;
using SharpNeedle.Structs;

namespace HEIO.NET.Modeling.ConvertTo
{
    internal static partial class VertexFormatEncoder
    {
        private static void IntEncodeUint4(BinaryObjectWriter writer, Vector4Int value)
        {
            writer.WriteInt32(value.X);
            writer.WriteInt32(value.Y);
            writer.WriteInt32(value.Z);
            writer.WriteInt32(value.W);
        }

        private static void IntEncodeInt4(BinaryObjectWriter writer, Vector4Int value)
        {
            writer.WriteInt32(value.X);
            writer.WriteInt32(value.Y);
            writer.WriteInt32(value.Z);
            writer.WriteInt32(value.W);
        }

        private static void IntEncodeUByte4(BinaryObjectWriter writer, Vector4Int value)
        {
            writer.WriteByte((byte)value.X);
            writer.WriteByte((byte)value.Y);
            writer.WriteByte((byte)value.Z);
            writer.WriteByte((byte)value.W);
        }

        private static void IntEncodeByte4(BinaryObjectWriter writer, Vector4Int value)
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

        private static void IntEncodeShort4(BinaryObjectWriter writer, Vector4Int value)
        {
            writer.WriteInt16((short)value.X);
            writer.WriteInt16((short)value.Y);
            writer.WriteInt16((short)value.Z);
            writer.WriteInt16((short)value.W);
        }

        private static void IntEncodeUshort4(BinaryObjectWriter writer, Vector4Int value)
        {
            writer.WriteUInt16((ushort)value.X);
            writer.WriteUInt16((ushort)value.Y);
            writer.WriteUInt16((ushort)value.Z);
            writer.WriteUInt16((ushort)value.W);
        }
    }
}
