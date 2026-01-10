using SharpNeedle.Framework.HedgehogEngine.Mirage.ModelData;

namespace HEIO.NET.Internal.Modeling.ConvertTo
{
    internal readonly struct VertexFormatSetup
    {
        public readonly VertexFormat normal;
        public readonly VertexFormat texcoord;

        public VertexFormatSetup(
            VertexFormat normal,
            VertexFormat texcoord)
        {
            this.normal = normal;
            this.texcoord = texcoord;
        }
    }

    internal static class VertexFormatSetups
    {
        public static readonly VertexFormatSetup _full = new(
            VertexFormat.Float3,
            VertexFormat.Float2
        );

        public static readonly VertexFormatSetup _he1Optimized = new(
            VertexFormat.Hend3Norm,
            VertexFormat.Float16_2
        );

        public static readonly VertexFormatSetup _he2Optimized = new(
            VertexFormat.Dec3Norm,
            VertexFormat.Float16_2
        );
    }
}
