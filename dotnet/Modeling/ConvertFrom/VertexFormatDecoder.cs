using Amicitia.IO.Binary;
using SharpNeedle.Framework.HedgehogEngine.Mirage;
using SharpNeedle.Structs;
using System;
using System.IO;
using System.Numerics;
using System.Runtime.CompilerServices;

namespace HEIO.NET.Modeling.ConvertFrom
{
    internal static partial class VertexFormatDecoder
    {
        public static int GetFormatComponentCount(VertexFormat format)
        {
            switch(format)
            {
                case VertexFormat.Float1:
                case VertexFormat.Int1:
                case VertexFormat.Uint1:
                case VertexFormat.Int1Norm:
                case VertexFormat.Uint1Norm:
                    return 1;
                case VertexFormat.Float2:
                case VertexFormat.Float16_2:
                case VertexFormat.Int2:
                case VertexFormat.Uint2:
                case VertexFormat.Int2Norm:
                case VertexFormat.Uint2Norm:
                case VertexFormat.Short2:
                case VertexFormat.Ushort2:
                case VertexFormat.Short2Norm:
                case VertexFormat.Ushort2Norm:
                    return 2;
                case VertexFormat.Float3:
                case VertexFormat.UDec3:
                case VertexFormat.Dec3:
                case VertexFormat.UDec3Norm:
                case VertexFormat.Dec3Norm:
                case VertexFormat.UHend3:
                case VertexFormat.Hend3:
                case VertexFormat.Uhend3Norm:
                case VertexFormat.Hend3Norm:
                case VertexFormat.Udhen3:
                case VertexFormat.Dhen3:
                case VertexFormat.Udhen3Norm:
                case VertexFormat.Dhen3Norm:
                    return 3;
                case VertexFormat.Float4:
                case VertexFormat.Float16_4:
                case VertexFormat.UDec4:
                case VertexFormat.Dec4:
                case VertexFormat.UDec4Norm:
                case VertexFormat.Dec4Norm:
                case VertexFormat.Int4:
                case VertexFormat.Uint4:
                case VertexFormat.Int4Norm:
                case VertexFormat.Uint4Norm:
                case VertexFormat.Short4:
                case VertexFormat.Ushort4:
                case VertexFormat.Short4Norm:
                case VertexFormat.Ushort4Norm:
                case VertexFormat.D3dColor:
                case VertexFormat.UByte4:
                case VertexFormat.Byte4:
                case VertexFormat.UByte4Norm:
                case VertexFormat.Byte4Norm:
                    return 4;
                default:
                    throw new ArgumentException($"Invalid format: {format}");
            }
        }

        public static int GetFormatByteSize(VertexFormat format)
        {
            switch(format)
            {
                case VertexFormat.Float1:
                case VertexFormat.Int1:
                case VertexFormat.Uint1:
                case VertexFormat.Int1Norm:
                case VertexFormat.Uint1Norm:
                case VertexFormat.Float16_2:
                case VertexFormat.Short2:
                case VertexFormat.Ushort2:
                case VertexFormat.Short2Norm:
                case VertexFormat.Ushort2Norm:
                case VertexFormat.UDec3:
                case VertexFormat.Dec3:
                case VertexFormat.UDec3Norm:
                case VertexFormat.Dec3Norm:
                case VertexFormat.UHend3:
                case VertexFormat.Hend3:
                case VertexFormat.Uhend3Norm:
                case VertexFormat.Hend3Norm:
                case VertexFormat.Udhen3:
                case VertexFormat.Dhen3:
                case VertexFormat.Udhen3Norm:
                case VertexFormat.Dhen3Norm:
                case VertexFormat.UDec4:
                case VertexFormat.Dec4:
                case VertexFormat.UDec4Norm:
                case VertexFormat.Dec4Norm:
                case VertexFormat.UByte4:
                case VertexFormat.Byte4:
                case VertexFormat.UByte4Norm:
                case VertexFormat.Byte4Norm:
                case VertexFormat.D3dColor:
                    return 4;
                case VertexFormat.Float2:
                case VertexFormat.Int2:
                case VertexFormat.Uint2:
                case VertexFormat.Int2Norm:
                case VertexFormat.Uint2Norm:
                case VertexFormat.Float16_4:
                case VertexFormat.Short4:
                case VertexFormat.Ushort4:
                case VertexFormat.Short4Norm:
                case VertexFormat.Ushort4Norm:
                    return 8;
                case VertexFormat.Float3:
                    return 12;
                case VertexFormat.Float4:
                case VertexFormat.Int4:
                case VertexFormat.Uint4:
                case VertexFormat.Int4Norm:
                case VertexFormat.Uint4Norm:
                    return 16;
                default:
                    throw new ArgumentException($"Invalid format: {format}");
            }
        }


        public static Func<BinaryObjectReader, float> GetSingleDecoder(VertexFormat format)
        {
            return format switch
            {
                VertexFormat.Float1 => DecodeFloat1,
                VertexFormat.Int1 => DecodeInt1,
                VertexFormat.Uint1 => DecodeUInt1,
                VertexFormat.Int1Norm => DecodeInt1Norm,
                VertexFormat.Uint1Norm => DecodeUInt1Norm,
                _ => throw new InvalidDataException($"Format \"{format}\" not a single!"),
            };
        }

        public static Func<BinaryObjectReader, Vector2> GetVector2Decoder(VertexFormat format)
        {
            return format switch
            {
                VertexFormat.Float2 => DecodeFloat2,
                VertexFormat.Int2 => DecodeInt2,
                VertexFormat.Uint2 => DecodeUint2,
                VertexFormat.Int2Norm => DecodeInt2Norm,
                VertexFormat.Uint2Norm => DecodeUint2Norm,
                VertexFormat.Short2 => DecodeShort2,
                VertexFormat.Ushort2 => DecodeUShort2,
                VertexFormat.Short2Norm => DecodeShort2Norm,
                VertexFormat.Ushort2Norm => DecodeUShort2Norm,
                VertexFormat.Float16_2 => DecodeFloat16_2,
                _ => throw new InvalidDataException($"Format \"{format}\" not a 2 component vector!"),
            };
        }

        public static Func<BinaryObjectReader, Vector3> GetVector3Decoder(VertexFormat format)
        {
            return format switch
            {
                VertexFormat.Float3 => DecodeFloat3,
                VertexFormat.UDec3 => DecodeUDec3,
                VertexFormat.Dec3 => DecodeDec3,
                VertexFormat.UDec3Norm => DecodeUDec3Norm,
                VertexFormat.Dec3Norm => DecodeDec3Norm,
                VertexFormat.UHend3 => DecodeUHend3,
                VertexFormat.Hend3 => DecodeHend3,
                VertexFormat.Uhend3Norm => DecodeUhend3Norm,
                VertexFormat.Hend3Norm => DecodeHend3Norm,
                VertexFormat.Udhen3 => DecodeUDHen3,
                VertexFormat.Dhen3 => DecodeDHen3,
                VertexFormat.Udhen3Norm => DecodeUDhen3Norm,
                VertexFormat.Dhen3Norm => DecodeDHen3Norm,

                _ => throw new InvalidDataException($"Format \"{format}\" not a 3 component vector!"),
            };
        }

        public static Func<BinaryObjectReader, Vector4> GetVector4Decoder(VertexFormat format)
        {
            return format switch
            {
                VertexFormat.Float4 => DecodeFloat4,
                VertexFormat.Uint4 => DecodeUint4,
                VertexFormat.Int4 => DecodeInt4,
                VertexFormat.Int4Norm => DecodeInt4Norm,
                VertexFormat.Uint4Norm => DecodeUint4Norm,
                VertexFormat.UByte4 => DecodeUByte4,
                VertexFormat.Byte4 => DecodeByte4,
                VertexFormat.UByte4Norm => DecodeUByte4Norm,
                VertexFormat.Byte4Norm => DecodeByte4Norm,
                VertexFormat.Short4 => DecodeShort4,
                VertexFormat.Ushort4 => DecodeUShort4,
                VertexFormat.Short4Norm => DecodeShort4Norm,
                VertexFormat.Ushort4Norm => DecodeUShort4Norm,
                VertexFormat.Float16_4 => DecodeFloat16_4,
                VertexFormat.D3dColor => DecodeUByte4,
                VertexFormat.UDec4 => DecodeUDec4,
                VertexFormat.Dec4 => DecodeDec4,
                VertexFormat.UDec4Norm => DecodeUDec4Norm,
                VertexFormat.Dec4Norm => DecodeDec4Norm,
                _ => throw new InvalidDataException($"Format \"{format}\" not a 4 component vector!"),
            };
        }

        public static Func<BinaryObjectReader, Vector4Int> GetVector4IntDecoder(VertexFormat format)
        {
            return format switch
            {
                VertexFormat.Uint4 => IntDecodeUint4,
                VertexFormat.Int4 => IntDecodeInt4,
                VertexFormat.Uint4Norm => IntDecodeUint4,
                VertexFormat.Int4Norm => IntDecodeInt4,
                VertexFormat.UByte4 => IntDecodeUByte4,
                VertexFormat.Byte4 => IntDecodeByte4,
                VertexFormat.UByte4Norm => IntDecodeUByte4,
                VertexFormat.Byte4Norm => IntDecodeByte4,
                VertexFormat.Short4 => IntDecodeShort4,
                VertexFormat.Ushort4 => IntDecodeUshort4,
                VertexFormat.Short4Norm => IntDecodeShort4,
                VertexFormat.Ushort4Norm => IntDecodeUshort4,
                VertexFormat.D3dColor => IntDecodeUByte4,
                _ => throw new InvalidDataException($"Format \"{format}\" not an integer 4 component vector!"),
            };
        }


        [MethodImpl(MethodImplOptions.AggressiveInlining)]
        private static int ToSigned2(uint value)
        {
            return (value & 0x2) != 0
                ? unchecked((int)(~0x1 | value))
                : (int)(value & 0x1);
        }


        [MethodImpl(MethodImplOptions.AggressiveInlining)]
        private static int ToSigned10(uint value)
        {
            return (value & 0x200) != 0
                ? unchecked((int)(~0x1FF | value))
                : (int)(value & 0x1FF);
        }

        [MethodImpl(MethodImplOptions.AggressiveInlining)]
        private static int ToSigned11(uint value)
        {
            return (value & 0x400) != 0
                ? unchecked((int)(~0x3FF | value))
                : (int)(value & 0x3FF);
        }
    }
}
