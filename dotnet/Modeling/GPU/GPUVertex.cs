using System;
using System.Numerics;

namespace HEIO.NET.Modeling.GPU
{
    internal struct GPUVertex
    {
        public Vector3 Position { get; set; }

        public Vector3 Normal { get; set; }

        public Vector3 Tangent { get; set; }

        public Vector3 Tangent2 { get; set; }

        public Vector2[] TextureCoordinates { get; set; }

        public Vector4[] Colors { get; set; }

        public VertexWeight[] Weights { get; set; }


        public GPUVertex(int texcoordSets, int colorSets, int weightCount)
        {
            Position = default;
            Normal = default;
            Tangent = default;
            Tangent2 = default;

            TextureCoordinates = new Vector2[texcoordSets];
            Colors = new Vector4[colorSets];
            Weights = new VertexWeight[weightCount];

            Array.Fill(Colors, new(1));
            Array.Fill(Weights, new(-1, 0));
        }

        public GPUVertex Copy()
        {
            Vector2[] textureCoordinates = new Vector2[TextureCoordinates.Length];
            Vector4[] colors = new Vector4[Colors.Length];
            VertexWeight[] weights = new VertexWeight[Weights.Length];

            Array.Copy(TextureCoordinates, textureCoordinates, textureCoordinates.Length);
            Array.Copy(Colors, colors, colors.Length);
            Array.Copy(Weights, weights, weights.Length);

            return new()
            {
                Position = Position,
                Normal = Normal,
                Tangent = Tangent,
                Tangent2 = Tangent2,
                TextureCoordinates = textureCoordinates,
                Colors = colors,
                Weights = weights,
            };
        }
    }
}
