﻿using Amicitia.IO.Binary;
using Amicitia.IO.Streams;
using HEIO.NET.Modeling.GPU;
using SharpNeedle.Framework.HedgehogEngine.Mirage;
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
        public static Mesh ConvertToMesh(GPUMesh gpuMesh, bool optimizedVertexData)
        {
            List<VertexElement> elements = EvaluateVertexElements(
                gpuMesh, 
                gpuMesh.Vertices[0].Weights.Length / 4, 
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

        private static List<VertexElement> EvaluateVertexElements(GPUMesh gpuMesh, int weightSets, bool optimizedVertexData, out ushort vertexSize)
        {
            VertexFormatSetup formatSetup = optimizedVertexData
                ? (gpuMesh.BlendIndex16
                    ? VertexFormatSetups._optimizedV6
                    : VertexFormatSetups._optimized)
                : (gpuMesh.BlendIndex16
                    ? VertexFormatSetups._fullV6
                    : VertexFormatSetups._full);

            List<(VertexType, VertexFormat, byte)> info = [
                (VertexType.Position, formatSetup.position, 0),
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
                info.Add((VertexType.Color, gpuMesh.UseByteColors ? formatSetup.byteColor : formatSetup.floatColor, i));
            }

            for(byte i = 0; i < weightSets; i++)
            {
                info.Add((VertexType.BlendIndices, formatSetup.blendIndices, i));
            }

            for(byte i = 0; i < weightSets; i++)
            {
                info.Add((VertexType.BlendWeight, formatSetup.blendWeights, i));
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
                            callback = (BinaryObjectWriter writer, GPUVertex vtx) => vec3Writer(writer, vtx.Position);
                        }
                        else // normal
                        {
                            callback = (BinaryObjectWriter writer, GPUVertex vtx) => vec3Writer(writer, vtx.Normal);
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
                                callback = (BinaryObjectWriter writer, GPUVertex vtx) => vec3Writer2(writer, vtx.Tangent);
                            }
                            else // bitangent
                            {
                                callback = (BinaryObjectWriter writer, GPUVertex vtx) => vec3Writer2(writer, Vector3.Cross(vtx.Normal, vtx.Tangent));
                            }
                        }
                        else
                        {
                            if(element.Type == VertexType.Tangent)
                            {
                                callback = (BinaryObjectWriter writer, GPUVertex vtx) => vec3Writer2(writer, vtx.Tangent2);
                            }
                            else // bitangent
                            {
                                callback = (BinaryObjectWriter writer, GPUVertex vtx) => vec3Writer2(writer, Vector3.Cross(vtx.Normal, vtx.Tangent2));
                            }
                        }

                        break;

                    case VertexType.BlendIndices:
                        Action<BinaryObjectWriter, Vector4Int> vec4intWriter = VertexFormatEncoder.GetVector4IntEncoder(element.Format);

                        callback = (BinaryObjectWriter writer, GPUVertex vtx) =>
                        {
                            Vector4Int indices = new(
                                vtx.Weights[weightIndexOffset + 3].Index,
                                vtx.Weights[weightIndexOffset + 2].Index,
                                vtx.Weights[weightIndexOffset + 1].Index,
                                vtx.Weights[weightIndexOffset].Index
                            );

                            vec4intWriter(writer, indices);
                        };
                        break;

                    case VertexType.BlendWeight:
                        Action<BinaryObjectWriter, Vector4> weightWriter = VertexFormatEncoder.GetVector4Encoder(element.Format);

                        callback = (BinaryObjectWriter writer, GPUVertex vtx) =>
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
                        callback = (BinaryObjectWriter writer, GPUVertex vtx) => vec2Writer(writer, vtx.TextureCoordinates[usageIndex]);
                        break;

                    case VertexType.Color:
                        Action<BinaryObjectWriter, Vector4> vec4Writer = VertexFormatEncoder.GetVector4Encoder(element.Format);
                        callback = (BinaryObjectWriter writer, GPUVertex vtx) => vec4Writer(writer, vtx.Colors![usageIndex]);
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
