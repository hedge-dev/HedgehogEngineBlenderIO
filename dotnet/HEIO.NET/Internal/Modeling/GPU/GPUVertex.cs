using HEIO.NET.External.Structs;
using System;
using System.Collections.Generic;
using System.Numerics;

namespace HEIO.NET.Internal.Modeling.GPU
{
    internal struct GPUVertex
    {
        private static readonly float _colorThreshold = new Vector4(2 / 255f).LengthSquared();

        public Vector3 Position { get; set; }

        public Vector3[]? MorphPositions { get; set; }

        public Vector3 Normal { get; set; }

        public UVDirection UVDirection { get; set; }

        public UVDirection UVDirection2 { get; set; }

        public Vector2[] TextureCoordinates { get; set; }

        public Vector4[] Colors { get; set; }

        public VertexWeight[] Weights { get; set; }


        public GPUVertex(int? morphPositions, int texcoordSets, int colorSets, int weightCount)
        {
            MorphPositions = morphPositions.HasValue ? new Vector3[morphPositions.Value] : null;
            TextureCoordinates = new Vector2[texcoordSets];
            Colors = new Vector4[colorSets];
            Weights = new VertexWeight[weightCount];
            MorphPositions = null;

            Array.Fill(Colors, new(1));
            Array.Fill(Weights, new(-1, 0));
        }

        public GPUVertex Copy()
        {
            Vector3[]? morphPositions = MorphPositions == null ? null : new Vector3[MorphPositions.Length];
            Vector2[] textureCoordinates = new Vector2[TextureCoordinates.Length];
            Vector4[] colors = new Vector4[Colors.Length];
            VertexWeight[] weights = new VertexWeight[Weights.Length];

            if(morphPositions != null)
            {
                Array.Copy(MorphPositions!, morphPositions, morphPositions.Length);
            }

            Array.Copy(TextureCoordinates, textureCoordinates, textureCoordinates.Length);
            Array.Copy(Colors, colors, colors.Length);
            Array.Copy(Weights, weights, weights.Length);

            return new()
            {
                Position = Position,
                MorphPositions = morphPositions,
                Normal = Normal,
                UVDirection = UVDirection,
                UVDirection2 = UVDirection2,
                TextureCoordinates = textureCoordinates,
                Colors = colors,
                Weights = weights,
            };
        }

        public static EqualityComparer<GPUVertex> GetMergeComparer(float mergeDistance, bool compareMorphs)
        {
            static bool CompareOthers(GPUVertex a, GPUVertex b)
            {
                if(!VertexWeight.CompareEquality(a.Weights, b.Weights)
                || !UVDirection.AreNormalsEqual(a.Normal, b.Normal)
                || !UVDirection.AreNormalsEqual(a.UVDirection.Tangent, b.UVDirection.Tangent)
                || !UVDirection.AreNormalsEqual(a.UVDirection.Binormal, b.UVDirection.Binormal)
                || !UVDirection.AreNormalsEqual(a.UVDirection2.Tangent, b.UVDirection2.Tangent)
                || !UVDirection.AreNormalsEqual(a.UVDirection2.Binormal, b.UVDirection2.Binormal))
                {
                    return false;
                }

                const float texcoordDistanceCheck = (float)(0.001 * 0.001);
                for (int i = 0; i < a.TextureCoordinates.Length; i++)
                {
                    if (Vector2.DistanceSquared(a.TextureCoordinates[i], b.TextureCoordinates[i]) > texcoordDistanceCheck)
                    {
                        return false;
                    }
                }

                for (int i = 0; i < a.Colors.Length; i++)
                {
                    if (Vector4.DistanceSquared(a.Colors[i], b.Colors[i]) > _colorThreshold)
                    {
                        return false;
                    }
                }

                return true;
            }

            float mergeDistanceSquared = mergeDistance * mergeDistance;

            if (compareMorphs)
            {
                return EqualityComparer<GPUVertex>.Create((a, b) =>
                    Vector3.DistanceSquared(a.Position, b.Position) < mergeDistanceSquared
                    && VectorUtils.CompareArrayDistances(a.MorphPositions!, b.MorphPositions!, mergeDistanceSquared)
                    && CompareOthers(a, b)
                );
            }
            else
            {
                return EqualityComparer<GPUVertex>.Create((a, b) =>
                    Vector3.DistanceSquared(a.Position, b.Position) < mergeDistanceSquared
                    && CompareOthers(a, b)
                );
            }

        }
    }
}
