using HEIO.NET.Internal.Modeling.GPU;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Numerics;

namespace HEIO.NET.Internal.Modeling.ConvertTo
{
    internal readonly struct ProcessTriangleCorner : IEquatable<ProcessTriangleCorner>
    {
        private static readonly float _colorThreshold = new Vector4(2 / 255f).LengthSquared();

        public readonly int vertexIndex;
        public readonly UVDirection uvDirection;
        public readonly UVDirection uvDirection2;
        public readonly Vector2[] textureCoordinates;
        public readonly Vector4[] colors;

        public ProcessTriangleCorner(int vertexIndex, UVDirection uvDirection, UVDirection uvDirection2, Vector2[] textureCoordinates, Vector4[] colors)
        {
            this.vertexIndex = vertexIndex;
            this.uvDirection = uvDirection;
            this.uvDirection2 = uvDirection2;
            this.textureCoordinates = textureCoordinates;
            this.colors = colors;
        }

        public bool Equals(ProcessTriangleCorner other)
        {
            if(vertexIndex != other.vertexIndex
                || !UVDirection.AreNormalsEqual(uvDirection.Tangent, other.uvDirection.Tangent)
                || !UVDirection.AreNormalsEqual(uvDirection.Binormal, other.uvDirection.Binormal)
                || !UVDirection.AreNormalsEqual(uvDirection2.Tangent, other.uvDirection2.Tangent)
                || !UVDirection.AreNormalsEqual(uvDirection2.Binormal, other.uvDirection2.Binormal))
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

        public static ProcessTriangleCorner EvalProcessTriangles(int vertexIndex, MeshData data, int faceIndex, int texcoordSets, int colorSets)
        {
            Vector2[] textureCoordinates = new Vector2[texcoordSets];

            int texcoordSetsMin = int.Min(data.TextureCoordinates.Count, texcoordSets);
            for(int j = 0; j < texcoordSetsMin; j++)
            {
                Vector2 uv = data.TextureCoordinates[j][faceIndex];
                textureCoordinates[j] = new(uv.X, 1 - uv.Y);
            }

            Vector4[] colors = new Vector4[colorSets];

            int colorSetsMin = int.Min(data.Colors.Count, colorSets);
            for(int j = 0; j < colorSetsMin; j++)
            {
                colors[j] = data.Colors[j][faceIndex];
            }

            for(int j = data.Colors.Count; j < colorSets; j++)
            {
                colors[j] = Vector4.One;
            }

            UVDirection uvDirection = data.PolygonUVDirections![faceIndex];

            return new(
                vertexIndex,
                uvDirection,
                data.PolygonUVDirections2?[faceIndex] ?? uvDirection,
                textureCoordinates,
                colors
            );
        }

        public static GPUVertex[] EvaluateGPUData(Vertex[] vertices, ProcessTriangleCorner[] triangles, int weightSets, out int[] faceIndices, out HashSet<short> usedBones, out int[] resultVertexIndices)
        {
            if(J113D.Common.DistinctMap.TryCreateDistinctMap(triangles, out J113D.Common.DistinctMap<ProcessTriangleCorner> cornerMap))
            {
                faceIndices = cornerMap.Map!;
            }
            else
            {
                faceIndices = [.. Enumerable.Range(0, triangles.Length)];
            }

            ProcessTriangleCorner[] distinctCorners = cornerMap.ValueArray;
            int weightCount = weightSets * 4;

            usedBones = [];
            GPUVertex[] result = new GPUVertex[distinctCorners.Length];
            resultVertexIndices = new int[result.Length];
            int texcoordSets = distinctCorners[0].textureCoordinates.Length;
            int colorSets = distinctCorners[0].colors.Length;

            for(int i = 0; i < distinctCorners.Length; i++)
            {
                ProcessTriangleCorner corner = distinctCorners[i];
                Vertex vertex = vertices[corner.vertexIndex];

                GPUVertex gpuVertex = new(texcoordSets, colorSets, weightCount)
                {
                    Position = vertex.Position,
                    Normal = vertex.Normal,
                    UVDirection = corner.uvDirection,
                    UVDirection2 = corner.uvDirection2,
                };

                for(int j = 0; j < texcoordSets; j++)
                {
                    gpuVertex.TextureCoordinates[j] = corner.textureCoordinates[j];
                }

                for(int j = 0; j < colorSets; j++)
                {
                    gpuVertex.Colors[j] = corner.colors[j];
                }

                if(weightCount != 0)
                {
                    TransferWeights(vertex.Weights, gpuVertex.Weights, usedBones);
                }

                result[i] = gpuVertex;
                resultVertexIndices[i] = corner.vertexIndex;
            }

            return result;
        }

        private static void TransferWeights(VertexWeight[] input, VertexWeight[] output, HashSet<short> usedBones)
        {
            if(input.Length == 0)
            {
                usedBones.Add(0);
                output[0] = new(0, 1);
                return;
            }

            int limit = int.Min(output.Length, input.Length);
            int j = 0;
            float sum = 0;
            foreach(VertexWeight weight in input.OrderByDescending(x => x.Weight))
            {
                usedBones.Add(weight.Index);
                output[j] = weight;
                sum += weight.Weight;

                j++;
                if(j >= limit)
                {
                    break;
                }
            }

            if(sum != 1f)
            {
                sum = 1f / sum;
                for(j = 0; j < limit; j++)
                {
                    output[j].Weight *= sum;
                }
            }
        }
    }
}
