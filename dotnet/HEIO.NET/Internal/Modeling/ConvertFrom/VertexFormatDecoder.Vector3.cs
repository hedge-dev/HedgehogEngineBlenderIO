using Amicitia.IO.Binary;
using System.Numerics;

namespace HEIO.NET.Internal.Modeling.ConvertFrom
{
    internal static partial class VertexFormatDecoder
    {
        private static Vector3 DecodeFloat3(BinaryObjectReader reader)
        {
            return new(
                reader.ReadSingle(),
                reader.ReadSingle(),
                reader.ReadSingle()
            );
        }

        private static Vector3 DecodeUDec3(BinaryObjectReader reader)
        {
            uint value = reader.ReadUInt32();
            return new(
                (value) & 0x3FF,
                (value >> 10) & 0x3FF,
                (value >> 20) & 0x3FF
            );
        }

        private static Vector3 DecodeDec3(BinaryObjectReader reader)
        {
            uint value = reader.ReadUInt32();
            return new(
                ToSigned10(value),
                ToSigned10(value >> 10),
                ToSigned10(value >> 20)
            );
        }

        private static Vector3 DecodeUDec3Norm(BinaryObjectReader reader)
        {
            uint value = reader.ReadUInt32();
            return new(
                ((value) & 0x3FF) / 1023f,
                ((value >> 10) & 0x3FF) / 1023f,
                ((value >> 20) & 0x3FF) / 1023f
            );
        }

        private static Vector3 DecodeDec3Norm(BinaryObjectReader reader)
        {
            uint value = reader.ReadUInt32();
            return new(
                ToSigned10(value) / 511f,
                ToSigned10(value >> 10) / 511f,
                ToSigned10(value >> 20) / 511f
            );
        }

        private static Vector3 DecodeUHend3(BinaryObjectReader reader)
        {
            uint value = reader.ReadUInt32();
            return new(
                (value) & 0x7FF,
                (value >> 11) & 0x7FF,
                value >> 22
            );
        }

        private static Vector3 DecodeHend3(BinaryObjectReader reader)
        {
            uint value = reader.ReadUInt32();
            return new(
                ToSigned11(value),
                ToSigned11(value >> 11),
                ToSigned10(value >> 22)
            );
        }

        private static Vector3 DecodeUhend3Norm(BinaryObjectReader reader)
        {
            uint value = reader.ReadUInt32();
            return new(
                ((value) & 0x7FF) / 2047f,
                ((value >> 11) & 0x7FF) / 2047f,
                (value >> 22) / 1023f
            );
        }

        private static Vector3 DecodeHend3Norm(BinaryObjectReader reader)
        {
            uint value = reader.ReadUInt32();
            return new(
                ToSigned11(value) / 1023f,
                ToSigned11(value >> 11) / 1023f,
                ToSigned10(value >> 22) / 511f
            );
        }

        private static Vector3 DecodeUDHen3(BinaryObjectReader reader)
        {
            uint value = reader.ReadUInt32();
            return new(
                (value) & 0x3FF,
                (value >> 10) & 0x7FF,
                value >> 21
            );
        }

        private static Vector3 DecodeDHen3(BinaryObjectReader reader)
        {
            uint value = reader.ReadUInt32();
            return new(
                ToSigned10(value),
                ToSigned11(value >> 10),
                ToSigned11(value >> 21)
            );
        }

        private static Vector3 DecodeUDhen3Norm(BinaryObjectReader reader)
        {
            uint value = reader.ReadUInt32();
            return new(
                ((value) & 0x3FF) / 1023f,
                ((value >> 10) & 0x7FF) / 2047f,
                (value >> 21) / 2047f
            );
        }

        private static Vector3 DecodeDHen3Norm(BinaryObjectReader reader)
        {
            uint value = reader.ReadUInt32();
            return new(
                ToSigned10(value) / 511f,
                ToSigned11(value >> 10) / 1023f,
                ToSigned11(value >> 21) / 1023f
            );
        }

    }
}
