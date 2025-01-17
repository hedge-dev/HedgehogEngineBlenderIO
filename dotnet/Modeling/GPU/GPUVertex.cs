using System;
using System.Numerics;

namespace HEIO.NET.Modeling.GPU
{
    internal struct GPUVertex
    {
        public Vector3 Position { get; set; }

        public Vector3 Normal { get; set; }

        public Vector3 Tangent { get; set; }

        public Vector2[] TextureCoordinates { get; set; }

        public Vector4[] Colors { get; set; }

        public VertexWeight[] Weights { get; set; }

        public bool UseByteColors { get; set; }


        public GPUVertex(int texcoordSets, int colorSets, int weightCount, bool useByteColors)
        {
            Position = default;
            Normal = default;
            Tangent = default;

            TextureCoordinates = new Vector2[texcoordSets];
            Colors = new Vector4[colorSets];
            Weights = new VertexWeight[weightCount];

            Array.Fill(Colors, new(1));
            Array.Fill(Weights, new(-1, 0));

            UseByteColors = useByteColors;
        }
    }
}
