using Amicitia.IO.Binary;
using System;
using System.Numerics;

namespace HEIO.NET.Modeling.ConvertFrom
{
    internal static partial class VertexFormatDecoder
    {
        private static Vector2 DecodeFloat2(BinaryObjectReader reader)
        {
            return new(
                reader.ReadSingle(),
                reader.ReadSingle()
            );
        }

        private static Vector2 DecodeInt2(BinaryObjectReader reader)
        {
            return new(
                reader.ReadInt32(),
                reader.ReadInt32()
            );
        }

        private static Vector2 DecodeUint2(BinaryObjectReader reader)
        {
            return new(
                reader.ReadUInt32(),
                reader.ReadUInt32()
            );
        }

        private static Vector2 DecodeInt2Norm(BinaryObjectReader reader)
        {
            return new(
                reader.ReadInt32() / (float)int.MaxValue,
                reader.ReadInt32() / (float)int.MaxValue
            );
        }

        private static Vector2 DecodeUint2Norm(BinaryObjectReader reader)
        {
            return new(
                reader.ReadUInt32() / (float)uint.MaxValue,
                reader.ReadUInt32() / (float)uint.MaxValue
            );
        }

        private static Vector2 DecodeShort2(BinaryObjectReader reader)
        {
            return new(
                reader.ReadInt16(),
                reader.ReadInt16()
            );
        }

        private static Vector2 DecodeUShort2(BinaryObjectReader reader)
        {
            return new(
                reader.ReadUInt16(),
                reader.ReadUInt16()
            );
        }

        private static Vector2 DecodeShort2Norm(BinaryObjectReader reader)
        {
            return new(
                reader.ReadInt16() / (float)short.MaxValue,
                reader.ReadInt16() / (float)short.MaxValue
            );
        }

        private static Vector2 DecodeUShort2Norm(BinaryObjectReader reader)
        {
            return new(
                reader.ReadUInt16() / (float)ushort.MaxValue,
                reader.ReadUInt16() / (float)ushort.MaxValue
            );
        }

        private static Vector2 DecodeFloat16_2(BinaryObjectReader reader)
        {
            return new(
                (float)BitConverter.UInt16BitsToHalf(reader.ReadUInt16()),
                (float)BitConverter.UInt16BitsToHalf(reader.ReadUInt16())
            );
        }
    }
}
