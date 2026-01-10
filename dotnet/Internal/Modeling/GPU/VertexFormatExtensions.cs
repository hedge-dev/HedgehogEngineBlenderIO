using SharpNeedle.Framework.HedgehogEngine.Mirage.ModelData;
using System;

namespace HEIO.NET.Internal.Modeling.GPU
{
    internal static class VertexFormatExtensions
    {
        public static int GetFormatComponentCount(this VertexFormat format)
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

        public static int GetFormatByteSize(this VertexFormat format)
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
    }
}
