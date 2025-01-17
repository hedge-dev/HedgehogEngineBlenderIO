using System;
using System.Numerics;

namespace HEIO.NET.Modeling.ConvertTo
{
    internal readonly struct TriangleData
    {
        public readonly MeshData data;
        public readonly int offset;
        public readonly int size;

        public TriangleData(MeshData data, int offset, int size)
        {
            this.data = data;
            this.offset = offset;
            this.size = size;
        }
    }

    internal readonly struct ProcessTriangleCorner : IEquatable<ProcessTriangleCorner>
    {
        private static readonly float _colorThreshold = new Vector4(2 / 255f).LengthSquared();

        public readonly int vertexIndex;
        public readonly Vector3 tangent;
        public readonly Vector2[] textureCoordinates;
        public readonly Vector4[] colors;

        public ProcessTriangleCorner(int vertexIndex, Vector3 tangent, Vector2[] textureCoordinates, Vector4[] colors)
        {
            this.vertexIndex = vertexIndex;
            this.tangent = tangent;
            this.textureCoordinates = textureCoordinates;
            this.colors = colors;
        }

        public bool Equals(ProcessTriangleCorner other)
        {
            if(vertexIndex != other.vertexIndex || Vector3.Dot(tangent, other.tangent) < 0.995f)
            {
                return false;
            }

            const float texcoordDistanceCheck = (float)(0.001 * 0.001);

            for(int i = 0; i < textureCoordinates.Length; i++)
            {
                if(Vector2.DistanceSquared(textureCoordinates[i], other.textureCoordinates[i]) > texcoordDistanceCheck)
                {
                    return false;
                }
            }

            for(int i = 0; i < colors.Length; i++)
            {
                if(Vector4.DistanceSquared(colors[i], other.colors[i]) > _colorThreshold)
                {
                    return false;
                }
            }

            return true;
        }
    }
}
