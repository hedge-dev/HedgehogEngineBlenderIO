using Amicitia.IO.Binary;
using SharpNeedle.Framework.HedgehogEngine.Mirage;
using SharpNeedle.Structs;
using System;
using System.IO;
using System.Numerics;
using System.Runtime.CompilerServices;

namespace HEIO.NET.Modeling.ConvertTo
{
    internal static partial class VertexFormatEncoder
    {
        public static Action<BinaryObjectWriter, float> GetSingleEncoder(VertexFormat format)
        {
            return format switch
            {
                VertexFormat.Float1 => EncodeFloat1,
                VertexFormat.Int1 => EncodeInt1,
                VertexFormat.Uint1 => EncodeUInt1,
                VertexFormat.Int1Norm => EncodeInt1Norm,
                VertexFormat.Uint1Norm => EncodeUInt1Norm,
                _ => throw new InvalidDataException($"Format \"{format}\" not a single!")
            };
        }

        public static Action<BinaryObjectWriter, Vector2> GetVector2Encoder(VertexFormat format)
        {
            return format switch
            {
                VertexFormat.Float2 => EncodeFloat2,
                VertexFormat.Int2 => EncodeInt2,
                VertexFormat.Uint2 => EncodeUint2,
                VertexFormat.Int2Norm => EncodeInt2Norm,
                VertexFormat.Uint2Norm => EncodeUint2Norm,
                VertexFormat.Short2 => EncodeShort2,
                VertexFormat.Ushort2 => EncodeUShort2,
                VertexFormat.Short2Norm => EncodeShort2Norm,
                VertexFormat.Ushort2Norm => EncodeUShort2Norm,
                VertexFormat.Float16_2 => EncodeFloat16_2,
                _ => throw new InvalidDataException($"Format \"{format}\" not a 2 component vector!")
            };
        }

        public static Action<BinaryObjectWriter, Vector3> GetVector3Encoder(VertexFormat format)
        {
            return format switch
            {
                VertexFormat.Float3 => EncodeFloat3,
                VertexFormat.UDec3 => EncodeUDec3,
                VertexFormat.Dec3 => EncodeDec3,
                VertexFormat.UDec3Norm => EncodeUDec3Norm,
                VertexFormat.Dec3Norm => EncodeDec3Norm,
                VertexFormat.UHend3 => EncodeUHend3,
                VertexFormat.Hend3 => EncodeHend3,
                VertexFormat.Uhend3Norm => EncodeUhend3Norm,
                VertexFormat.Hend3Norm => EncodeHend3Norm,
                VertexFormat.Udhen3 => EncodeUDHen3,
                VertexFormat.Dhen3 => EncodeDHen3,
                VertexFormat.Udhen3Norm => EncodeUDhen3Norm,
                VertexFormat.Dhen3Norm => EncodeDHen3Norm,

                _ => throw new InvalidDataException($"Format \"{format}\" not a 3 component vector!")
            };
        }

        public static Action<BinaryObjectWriter, Vector4> GetVector4Encoder(VertexFormat format)
        {
            return format switch
            {
                VertexFormat.Float4 => EncodeFloat4,
                VertexFormat.Uint4 => EncodeUint4,
                VertexFormat.Int4 => EncodeInt4,
                VertexFormat.Int4Norm => EncodeInt4Norm,
                VertexFormat.Uint4Norm => EncodeUint4Norm,
                VertexFormat.UByte4 => EncodeUByte4,
                VertexFormat.Byte4 => EncodeByte4,
                VertexFormat.UByte4Norm => EncodeUByte4Norm,
                VertexFormat.Byte4Norm => EncodeByte4Norm,
                VertexFormat.Short4 => EncodeShort4,
                VertexFormat.Ushort4 => EncodeUShort4,
                VertexFormat.Short4Norm => EncodeShort4Norm,
                VertexFormat.Ushort4Norm => EncodeUShort4Norm,
                VertexFormat.Float16_4 => EncodeFloat16_4,
                VertexFormat.D3dColor => EncodeUByte4,
                VertexFormat.UDec4 => EncodeUDec4,
                VertexFormat.Dec4 => EncodeDec4,
                VertexFormat.UDec4Norm => EncodeUDec4Norm,
                VertexFormat.Dec4Norm => EncodeDec4Norm,
                _ => throw new InvalidDataException($"Format \"{format}\" not a 4 component vector!")
            };
        }

        public static Action<BinaryObjectWriter, Vector4Int> GetVector4IntEncoder(VertexFormat format)
        {
            return format switch
            {
                VertexFormat.Uint4 => IntEncodeUint4,
                VertexFormat.Int4 => IntEncodeInt4,
                VertexFormat.Uint4Norm => IntEncodeUint4,
                VertexFormat.Int4Norm => IntEncodeInt4,
                VertexFormat.UByte4 => IntEncodeUByte4,
                VertexFormat.Byte4 => IntEncodeByte4,
                VertexFormat.UByte4Norm => IntEncodeUByte4,
                VertexFormat.Byte4Norm => IntEncodeByte4,
                VertexFormat.Short4 => IntEncodeShort4,
                VertexFormat.Ushort4 => IntEncodeUshort4,
                VertexFormat.Short4Norm => IntEncodeShort4,
                VertexFormat.Ushort4Norm => IntEncodeUshort4,
                VertexFormat.D3dColor => IntEncodeUByte4,
                _ => throw new InvalidDataException($"Format \"{format}\" not an integer 4 component vector!")
            };
        }


        [MethodImpl(MethodImplOptions.AggressiveInlining)]
        private static uint FromSigned2(int value)
        {
            return (uint)((value & 0x1) | (value < 0 ? 0x2 : 0));
        }

        [MethodImpl(MethodImplOptions.AggressiveInlining)]
        private static uint FromSigned10(int value)
        {
            return (uint)((value & 0x1FF) | (value < 0 ? 0x200 : 0));
        }

        [MethodImpl(MethodImplOptions.AggressiveInlining)]
        private static uint FromSigned11(int value)
        {
            return (uint)((value & 0x3FF) | (value < 0 ? 0x400 : 0));
        }
    }
}
