using Amicitia.IO.Binary;
using SharpNeedle.Structs;

namespace HEIO.NET.VertexUtils
{
    public static partial class VertexFormatDecoder
    {
        private static Vector4Int IntDecodeUint4(BinaryObjectReader reader)
        {
            return new(
                (int)reader.ReadUInt32(),
                (int)reader.ReadUInt32(),
                (int)reader.ReadUInt32(),
                (int)reader.ReadUInt32()
            );
        }

        private static Vector4Int IntDecodeInt4(BinaryObjectReader reader)
        {
            return new(
                reader.ReadInt32(),
                reader.ReadInt32(),
                reader.ReadInt32(),
                reader.ReadInt32()
            );
        }

        private static Vector4Int IntDecodeUByte4(BinaryObjectReader reader)
        {
            return new(
                reader.ReadByte(),
                reader.ReadByte(),
                reader.ReadByte(),
                reader.ReadByte()
            );
        }

        private static Vector4Int IntDecodeByte4(BinaryObjectReader reader)
        {
            return new(
                unchecked((sbyte)reader.ReadSByte()),
                unchecked((sbyte)reader.ReadSByte()),
                unchecked((sbyte)reader.ReadSByte()),
                unchecked((sbyte)reader.ReadSByte())
            );
        }

        private static Vector4Int IntDecodeShort4(BinaryObjectReader reader)
        {
            return new(
                reader.ReadInt16(),
                reader.ReadInt16(),
                reader.ReadInt16(),
                reader.ReadInt16()
            );
        }

        private static Vector4Int IntDecodeUshort4(BinaryObjectReader reader)
        {
            return new(
                reader.ReadUInt16(),
                reader.ReadUInt16(),
                reader.ReadUInt16(),
                reader.ReadUInt16()
            );
        }

    }
}
