using SharpNeedle.Framework.HedgehogEngine.Mirage;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace HEIO.NET.Modeling.ConvertTo
{
    internal readonly struct VertexFormatSetup
    {
        public readonly VertexFormat position;
        public readonly VertexFormat normal;
        public readonly VertexFormat texcoord;
        public readonly VertexFormat byteColor;
        public readonly VertexFormat floatColor;
        public readonly VertexFormat blendIndices;
        public readonly VertexFormat blendWeights;

        public VertexFormatSetup(
            VertexFormat position, 
            VertexFormat normal, 
            VertexFormat texcoord, 
            VertexFormat byteColor, 
            VertexFormat floatColor, 
            VertexFormat blendIndices,
            VertexFormat blendWeights)
        {
            this.position = position;
            this.normal = normal;
            this.texcoord = texcoord;
            this.byteColor = byteColor;
            this.floatColor = floatColor;
            this.blendIndices = blendIndices;
            this.blendWeights = blendWeights;
        }
    }

    internal static class VertexFormatSetups
    {
        public static readonly VertexFormatSetup _full = new(
            VertexFormat.Float3,
            VertexFormat.Float3,
            VertexFormat.Float2,
            VertexFormat.UByte4Norm,
            VertexFormat.Float4,
            VertexFormat.UByte4,
            VertexFormat.UByte4Norm
        );

        public static readonly VertexFormatSetup _optimized = new(
            VertexFormat.Float3,
            VertexFormat.Dec3Norm,
            VertexFormat.Float16_2,
            VertexFormat.UByte4Norm,
            VertexFormat.Float4,
            VertexFormat.UByte4,
            VertexFormat.UByte4Norm
        );

        public static readonly VertexFormatSetup _fullV6 = new(
            VertexFormat.Float3,
            VertexFormat.Float3,
            VertexFormat.Float2,
            VertexFormat.UByte4Norm,
            VertexFormat.Float4,
            VertexFormat.Ushort4,
            VertexFormat.UByte4Norm
        );

        public static readonly VertexFormatSetup _optimizedV6 = new(
            VertexFormat.Float3,
            VertexFormat.Dec3Norm,
            VertexFormat.Float16_2,
            VertexFormat.UByte4Norm,
            VertexFormat.Float4,
            VertexFormat.Ushort4,
            VertexFormat.UByte4Norm
        );
    }
}
