using Amicitia.IO.Binary;
using Amicitia.IO.Streams;
using HEIO.NET.Modeling;
using HEIO.NET.Modeling.GPU;
using SharpNeedle.Framework.HedgehogEngine.Mirage.ModelData;
using SharpNeedle.Structs;
using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Numerics;

namespace HEIO.NET.Modeling.ConvertTo
{
    internal static class MeshConverter
    {
        public static Mesh ConvertToMesh(GPUMesh gpuMesh, ModelVersionMode versionMode, bool optimizedVertexData)
        {
            List<VertexElement> elements = EvaluateVertexElements(
                gpuMesh,
                gpuMesh.Vertices[0].Weights.Length / 4,
                versionMode,
                optimizedVertexData,
                out ushort vertexSize);

            return new()
            {
                Faces = gpuMesh.Triangles.Select(x => (ushort)x).ToArray(),
                BoneIndices = [.. gpuMesh.BoneIndices],
                Slot = gpuMesh.Slot,
                Material = gpuMesh.Material,
                VertexCount = (uint)gpuMesh.Vertices.Count,
                Elements = elements,
                VertexSize = vertexSize,
                Vertices = GetVertexData(gpuMesh.Vertices, elements, vertexSize)
            };
        }

        private static List<VertexElement> EvaluateVertexElements(GPUMesh gpuMesh, int weightSets, ModelVersionMode versionMode, bool optimizedVertexData, out ushort vertexSize)
        {
            VertexFormatSetup formatSetup = !optimizedVertexData
                ? VertexFormatSetups._full
                : versionMode == ModelVersionMode.HE2
                ? VertexFormatSetups._he2Optimized
                : VertexFormatSetups._he1Optimized;

            List<(VertexType, VertexFormat, byte)> info = [
                (VertexType.Position, VertexFormat.Float3, 0),
                (VertexType.Normal, formatSetup.normal, 0),
                (VertexType.Tangent, formatSetup.normal, 0),
                (VertexType.Binormal, formatSetup.normal, 0),
            ];

            if(gpuMesh.MultiTangent)
            {
                info.Add((VertexType.Tangent, formatSetup.normal, 1));
                info.Add((VertexType.Binormal, formatSetup.normal, 1));
            }

            for(byte i = 0; i < gpuMesh.TexcoordSets; i++)
            {
                info.Add((VertexType.TexCoord, formatSetup.texcoord, i));
            }

            for(byte i = 0; i < gpuMesh.ColorSets; i++)
            {
                info.Add((VertexType.Color, gpuMesh.UseByteColors ? VertexFormat.UByte4Norm : VertexFormat.Float4, i));
            }

            for(byte i = 0; i < weightSets; i++)
            {
                info.Add((VertexType.BlendIndices, gpuMesh.BlendIndex16 ? VertexFormat.Ushort4 : VertexFormat.UByte4, i));
            }

            for(byte i = 0; i < weightSets; i++)
            {
                info.Add((VertexType.BlendWeight, VertexFormat.UByte4Norm, i));
            }

            List<VertexElement> result = [];
            vertexSize = 0;

            foreach((VertexType type, VertexFormat format, byte usageIndex) in info)
            {
                result.Add(new()
                {
                    Type = type,
                    Format = format,
                    UsageIndex = usageIndex,
                    Offset = vertexSize
                });

                vertexSize += (ushort)format.GetFormatByteSize();
            }

            return result;
        }


        private static byte[] GetVertexData(IList<GPUVertex> vertices, List<VertexElement> elements, int vertexSize)
        {
            using MemoryStream stream = new(vertexSize * vertices.Count);
            using(BinaryObjectWriter writer = new(stream, StreamOwnership.Retain, Endianness.Little))
            {
                VertexWriteCallback[] writeCallbacks = GetVertexWriteCallbacks(elements);

                foreach(GPUVertex vertex in vertices)
                {
                    foreach(VertexWriteCallback writeCallback in writeCallbacks)
                    {
                        writeCallback(writer, vertex);
                    }
                }
            }

            return stream.ToArray();
        }

        private delegate void VertexWriteCallback(BinaryObjectWriter writer, GPUVertex vertex);

        private static VertexWriteCallback[] GetVertexWriteCallbacks(IEnumerable<VertexElement> elements)
        {
            List<VertexWriteCallback> result = [];

            foreach(VertexElement element in elements)
            {
                int usageIndex = element.UsageIndex;
                int weightIndexOffset = usageIndex * 4;
                VertexWriteCallback callback;

                switch(element.Type)
                {
                    case VertexType.Position:
                    case VertexType.Normal:
                        Action<BinaryObjectWriter, Vector3> vec3Writer = VertexFormatEncoder.GetVector3Encoder(element.Format);

                        if(element.UsageIndex != 0)
                        {
                            throw new InvalidOperationException($"Writing \"{element.Type}\" with usage index {element.UsageIndex} is not supported!");
                        }

                        if(element.Type == VertexType.Position)
                        {
                            callback = (writer, vtx) => vec3Writer(writer, vtx.Position);
                        }
                        else // normal
                        {
                            callback = (writer, vtx) => vec3Writer(writer, vtx.Normal);
                        }

                        break;

                    case VertexType.Tangent:
                    case VertexType.Binormal:
                        if(element.UsageIndex > 1)
                        {
                            throw new InvalidOperationException($"Writing \"{element.Type}\" with usage index {element.UsageIndex} is not supported!");
                        }

                        Action<BinaryObjectWriter, Vector3> vec3Writer2 = VertexFormatEncoder.GetVector3Encoder(element.Format);

                        if(element.UsageIndex == 0)
                        {
                            if(element.Type == VertexType.Tangent)
                            {
                                callback = (writer, vtx) => vec3Writer2(writer, vtx.UVDirection.Tangent);
                            }
                            else // bitangent
                            {
                                callback = (writer, vtx) => vec3Writer2(writer, vtx.UVDirection.Binormal);
                            }
                        }
                        else
                        {
                            if(element.Type == VertexType.Tangent)
                            {
                                callback = (writer, vtx) => vec3Writer2(writer, vtx.UVDirection2.Tangent);
                            }
                            else // bitangent
                            {
                                callback = (writer, vtx) => vec3Writer2(writer, vtx.UVDirection2.Binormal);
                            }
                        }

                        break;

                    case VertexType.BlendIndices:
                        Action<BinaryObjectWriter, Vector4Int> vec4intWriter = VertexFormatEncoder.GetVector4IntEncoder(element.Format);

                        callback = (writer, vtx) =>
                        {
                            Vector4Int indices;

                            if(element.Format == VertexFormat.Ushort4)
                            {
                                indices = new(
                                    vtx.Weights[weightIndexOffset].Index,
                                    vtx.Weights[weightIndexOffset + 1].Index,
                                    vtx.Weights[weightIndexOffset + 2].Index,
                                    vtx.Weights[weightIndexOffset + 3].Index
                                );
                            }
                            else
                            {
                                indices = new(
                                    vtx.Weights[weightIndexOffset + 3].Index,
                                    vtx.Weights[weightIndexOffset + 2].Index,
                                    vtx.Weights[weightIndexOffset + 1].Index,
                                    vtx.Weights[weightIndexOffset].Index
                                );
                            }

                            vec4intWriter(writer, indices);
                        };
                        break;

                    case VertexType.BlendWeight:
                        Action<BinaryObjectWriter, Vector4> weightWriter = VertexFormatEncoder.GetVector4Encoder(element.Format);

                        callback = (writer, vtx) =>
                        {
                            Vector4 weights = new(
                                vtx.Weights[weightIndexOffset + 3].Weight,
                                vtx.Weights[weightIndexOffset + 2].Weight,
                                vtx.Weights[weightIndexOffset + 1].Weight,
                                vtx.Weights[weightIndexOffset].Weight
                            );

                            weightWriter(writer, weights);
                        };
                        break;

                    case VertexType.TexCoord:
                        Action<BinaryObjectWriter, Vector2> vec2Writer = VertexFormatEncoder.GetVector2Encoder(element.Format);
                        callback = (writer, vtx) => vec2Writer(writer, vtx.TextureCoordinates[usageIndex]);
                        break;

                    case VertexType.Color:
                        Action<BinaryObjectWriter, Vector4> vec4Writer = VertexFormatEncoder.GetVector4Encoder(element.Format);
                        callback = (writer, vtx) => vec4Writer(writer, vtx.Colors![usageIndex]);
                        break;
                    default:
                        throw new InvalidOperationException($"Writing \"{element.Type}\" is not supported!");
                }

                result.Add(callback);
            }

            return [.. result];
        }
    }
}
