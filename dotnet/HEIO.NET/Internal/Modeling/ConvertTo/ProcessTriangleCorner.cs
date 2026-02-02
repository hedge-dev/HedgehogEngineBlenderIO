using HEIO.NET.Internal.Modeling.GPU;
using J113D.Common;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Numerics;

namespace HEIO.NET.Internal.Modeling.ConvertTo
{
    internal readonly struct ProcessTriangleCorner
    {
        public readonly int vertexIndex;
        public readonly Vector3? normal;
        public readonly UVDirection uvDirection;
        public readonly UVDirection uvDirection2;
        public readonly Vector2[] textureCoordinates;
        public readonly Vector4[] colors;

        public ProcessTriangleCorner(int vertexIndex, Vector3? normal, UVDirection uvDirection, UVDirection uvDirection2, Vector2[] textureCoordinates, Vector4[] colors)
        {
            this.vertexIndex = vertexIndex;
            this.normal = normal;
            this.uvDirection = uvDirection;
            this.uvDirection2 = uvDirection2;
            this.textureCoordinates = textureCoordinates;
            this.colors = colors;
        }

        public static ProcessTriangleCorner EvalProcessTriangles(int vertexIndex, MeshData data, int faceIndex, int texcoordSets, int colorSets, bool multiTangent)
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
                data.PolygonNormals?[faceIndex],
                uvDirection,
                multiTangent && data.PolygonUVDirections2 != null ? data.PolygonUVDirections2[faceIndex] : uvDirection,
                textureCoordinates,
                colors
            );
        }

        public static GPUVertex[] EvaluateGPUData(Vertex[] vertices, ProcessTriangleCorner[] triangles, int weightSets, out int[] faceIndices, out HashSet<short> usedBones)
        {
            int weightCount = weightSets * 4;

            usedBones = [];
            GPUVertex[] rawVertices = new GPUVertex[triangles.Length];
            int texcoordSets = triangles[0].textureCoordinates.Length;
            int colorSets = triangles[0].colors.Length;

            for(int i = 0; i < triangles.Length; i++)
            {
                ProcessTriangleCorner corner = triangles[i];
                Vertex vertex = vertices[corner.vertexIndex];

                GPUVertex gpuVertex = new(vertex.MorphPositions?.Length, texcoordSets, colorSets, weightCount)
                {
                    Position = vertex.Position,
                    Normal = corner.normal ?? vertex.Normal,
                    UVDirection = corner.uvDirection,
                    UVDirection2 = corner.uvDirection2,
                };

                if(vertex.MorphPositions != null)
                {
                    Array.Copy(vertex.MorphPositions, gpuVertex.MorphPositions!, vertex.MorphPositions.Length);
                }

                Array.Copy(corner.textureCoordinates, gpuVertex.TextureCoordinates, texcoordSets);
                Array.Copy(corner.colors, gpuVertex.Colors, colorSets);

                if(weightCount != 0)
                {
                    TransferWeights(vertex.Weights, gpuVertex.Weights, usedBones);
                }

                rawVertices[i] = gpuVertex;
            }

            EqualityComparer<GPUVertex> comparer = GPUVertex.GetMergeComparer(0.001f, rawVertices[0].MorphPositions != null);

            if(rawVertices.TryCreateDistinctMapSSP(x => x.Position.GetPositionSSP(), 0.001f, comparer, out DistinctMap<GPUVertex> verticesMap))
            {
                faceIndices = verticesMap.Map!;
                return verticesMap.ValueArray;
            }
            else
            {
                faceIndices = [.. Enumerable.Range(0, rawVertices.Length)];
                return rawVertices;
            }
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
