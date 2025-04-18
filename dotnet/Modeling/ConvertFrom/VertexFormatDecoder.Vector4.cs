using Amicitia.IO.Binary;
using System;
using System.Numerics;

namespace HEIO.NET.Modeling.ConvertFrom
{
    internal static partial class VertexFormatDecoder
    {
        private static Vector4 DecodeFloat4(BinaryObjectReader reader)
        {
            return new(
                reader.ReadSingle(),
                reader.ReadSingle(),
                reader.ReadSingle(),
                reader.ReadSingle()
            );
        }

        private static Vector4 DecodeInt4(BinaryObjectReader reader)
        {
            return new(
                reader.ReadInt32(),
                reader.ReadInt32(),
                reader.ReadInt32(),
                reader.ReadInt32()
            );
        }

        private static Vector4 DecodeInt4Norm(BinaryObjectReader reader)
        {
            return new(
                reader.ReadInt32() / (float)int.MaxValue,
                reader.ReadInt32() / (float)int.MaxValue,
                reader.ReadInt32() / (float)int.MaxValue,
                reader.ReadInt32() / (float)int.MaxValue
            );
        }

        private static Vector4 DecodeUint4(BinaryObjectReader reader)
        {
            return new(
                reader.ReadUInt32(),
                reader.ReadUInt32(),
                reader.ReadUInt32(),
                reader.ReadUInt32()
            );
        }

        private static Vector4 DecodeUint4Norm(BinaryObjectReader reader)
        {
            return new(
                reader.ReadUInt32() / (float)uint.MaxValue,
                reader.ReadUInt32() / (float)uint.MaxValue,
                reader.ReadUInt32() / (float)uint.MaxValue,
                reader.ReadUInt32() / (float)uint.MaxValue
            );
        }

        private static Vector4 DecodeUByte4(BinaryObjectReader reader)
        {
            return new(
                reader.ReadByte(),
                reader.ReadByte(),
                reader.ReadByte(),
                reader.ReadByte()
            );
        }

        private static Vector4 DecodeByte4(BinaryObjectReader reader)
        {
            return new(
                unchecked((sbyte)reader.ReadSByte()),
                unchecked((sbyte)reader.ReadSByte()),
                unchecked((sbyte)reader.ReadSByte()),
                unchecked((sbyte)reader.ReadSByte())
            );
        }

        private static Vector4 DecodeUByte4Norm(BinaryObjectReader reader)
        {
            return new(
                reader.ReadByte() / (float)byte.MaxValue,
                reader.ReadByte() / (float)byte.MaxValue,
                reader.ReadByte() / (float)byte.MaxValue,
                reader.ReadByte() / (float)byte.MaxValue
            );
        }

        private static Vector4 DecodeByte4Norm(BinaryObjectReader reader)
        {
            return new(
                unchecked((sbyte)reader.ReadSByte()) / (float)sbyte.MaxValue,
                unchecked((sbyte)reader.ReadSByte()) / (float)sbyte.MaxValue,
                unchecked((sbyte)reader.ReadSByte()) / (float)sbyte.MaxValue,
                unchecked((sbyte)reader.ReadSByte()) / (float)sbyte.MaxValue
            );
        }

        private static Vector4 DecodeShort4(BinaryObjectReader reader)
        {
            return new(
                reader.ReadInt16(),
                reader.ReadInt16(),
                reader.ReadInt16(),
                reader.ReadInt16()
            );
        }

        private static Vector4 DecodeShort4Norm(BinaryObjectReader reader)
        {
            return new(
                reader.ReadInt16() / (float)short.MaxValue,
                reader.ReadInt16() / (float)short.MaxValue,
                reader.ReadInt16() / (float)short.MaxValue,
                reader.ReadInt16() / (float)short.MaxValue
            );
        }

        private static Vector4 DecodeUShort4(BinaryObjectReader reader)
        {
            return new(
                reader.ReadUInt16(),
                reader.ReadUInt16(),
                reader.ReadUInt16(),
                reader.ReadUInt16()
            );
        }

        private static Vector4 DecodeUShort4Norm(BinaryObjectReader reader)
        {
            return new(
                reader.ReadUInt16() / (float)ushort.MaxValue,
                reader.ReadUInt16() / (float)ushort.MaxValue,
                reader.ReadUInt16() / (float)ushort.MaxValue,
                reader.ReadUInt16() / (float)ushort.MaxValue
            );
        }

        private static Vector4 DecodeUDec4(BinaryObjectReader reader)
        {
            uint value = reader.ReadUInt32();
            return new(
                (value) & 0x3FF,
                (value >> 10) & 0x3FF,
                (value >> 20) & 0x3FF,
                value >> 30
            );
        }

        private static Vector4 DecodeDec4(BinaryObjectReader reader)
        {
            uint value = reader.ReadUInt32();
            return new(
                ToSigned10(value),
                ToSigned10(value >> 10),
                ToSigned10(value >> 20),
                ToSigned2(value >> 30)
            );
        }

        private static Vector4 DecodeUDec4Norm(BinaryObjectReader reader)
        {
            uint value = reader.ReadUInt32();
            return new(
                ((value) & 0x3FF) / 1023f,
                ((value >> 10) & 0x3FF) / 1023f,
                ((value >> 20) & 0x3FF) / 1023f,
                (value >> 30) / 3f
            );
        }

        private static Vector4 DecodeDec4Norm(BinaryObjectReader reader)
        {
            uint value = reader.ReadUInt32();
            return new(
                ToSigned10(value) / 511f,
                ToSigned10(value >> 10) / 511f,
                ToSigned10(value >> 20) / 511f,
                ToSigned2(value >> 30)
            );
        }

        private static Vector4 DecodeFloat16_4(BinaryObjectReader reader)
        {
            return new(
                (float)BitConverter.UInt16BitsToHalf(reader.ReadUInt16()),
                (float)BitConverter.UInt16BitsToHalf(reader.ReadUInt16()),
                (float)BitConverter.UInt16BitsToHalf(reader.ReadUInt16()),
                (float)BitConverter.UInt16BitsToHalf(reader.ReadUInt16())
            );
        }


    }
}
