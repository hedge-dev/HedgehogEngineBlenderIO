using Amicitia.IO.Binary;
using Amicitia.IO.Streams;
using HEIO.NET.Internal.Modeling;
using HEIO.NET.Internal.Modeling.GPU;
using HEIO.NET.Modeling.ConvertFrom;
using SharpNeedle.Framework.HedgehogEngine.Mirage.ModelData;
using SharpNeedle.Structs;
using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Numerics;

namespace HEIO.NET.Internal.Modeling.ConvertFrom
{
    internal static class MeshConverter
    {
        public static GPUMesh ConvertToGPUMesh(Mesh mesh, Topology topology)
        {
            int GetSetNum(VertexType type)
            {
                return mesh.Elements.Any(x => x.Type == type) ? mesh.Elements.Where(x => x.Type == type).Max(x => x.UsageIndex) + 1 : 0;
            }

            int texcoordSets = GetSetNum(VertexType.TexCoord);
            int colorSets = GetSetNum(VertexType.Color);
            int weightCount = GetSetNum(VertexType.BlendIndices) * 4;

            bool useByteColors = colorSets > 0 && mesh.Elements
                    .Where(x => x.Type == VertexType.Color)
                    .All(x => x.Format is VertexFormat.D3dColor
                        or VertexFormat.UByte4
                        or VertexFormat.UByte4Norm
                        or VertexFormat.Byte4
                        or VertexFormat.Byte4Norm);

            int[] triangles = [.. topology == Topology.TriangleList
                ? FlipTriangles(mesh.Faces)
                : ExpandStrip(mesh.Faces)];

            GPUVertex[] vertices = ReadVertexData(mesh, texcoordSets, colorSets, weightCount, useByteColors);

            bool blendIndex16 = mesh.Elements.Any(x => x.Type == VertexType.BlendIndices && x.Format == VertexFormat.Ushort4);
            bool multiTangent = mesh.Elements.Any(x => x.Type == VertexType.Tangent && x.UsageIndex == 1);

            return new(
                vertices,
                texcoordSets,
                colorSets,
                useByteColors,
                blendIndex16,
                multiTangent,
                Topology.TriangleList,
                triangles,
                mesh.BoneIndices,
                mesh.Material,
                mesh.Slot);
        }

        private static IEnumerable<ushort> FlipTriangles(ushort[] indices)
        {
            for(int i = 0; i < indices.Length; i += 3)
            {
                yield return indices[i + 1];
                yield return indices[i];
                yield return indices[i + 2];
            }
        }

        private static IEnumerable<ushort> ExpandStrip(ushort[] indices)
        {
            bool rev = false;
            ushort a = indices[0];
            ushort b = indices[1];

            for(int i = 2; i < indices.Length; i++)
            {
                ushort c = indices[i];

                if(c == ushort.MaxValue)
                {
                    if(i + 3 >= indices.Length)
                    {
                        break;
                    }

                    a = indices[++i];
                    b = indices[++i];
                    rev = false;
                    continue;
                }

                rev = !rev;

                if(a != b && b != c && c != a)
                {
                    if(rev)
                    {
                        yield return b;
                        yield return a;
                        yield return c;
                    }
                    else
                    {
                        yield return a;
                        yield return b;
                        yield return c;
                    }
                }

                a = b;
                b = c;
            }
        }

        private static GPUVertex[] ReadVertexData(Mesh mesh, int texcoordSets, int colorSets, int weightCount, bool useByteColors)
        {
            using MemoryStream stream = new(mesh.Vertices);
            using BinaryObjectReader reader = new(stream, StreamOwnership.Retain, Endianness.Little);

            (int, VertexReadCallback)[] readCallbacks = GetVertexReadCallbacks(mesh.Elements);
            GPUVertex[] result = new GPUVertex[mesh.VertexCount];

            for(uint i = 0, o = 0; i < mesh.VertexCount; i++, o += mesh.VertexSize)
            {
                GPUVertex vertex = new(texcoordSets, colorSets, weightCount);

                foreach((int offset, VertexReadCallback callback) in readCallbacks)
                {
                    reader.Seek(o + offset, SeekOrigin.Begin);
                    callback(reader, ref vertex);
                }

                result[i] = vertex;
            }

            if(weightCount > 0)
            {
                foreach(GPUVertex vertex in result)
                {
                    float firstWeight = 1.0f;

                    for(int i = 1; i < vertex.Weights.Length; i++)
                    {
                        firstWeight -= vertex.Weights[i].Weight;
                    }

                    vertex.Weights[0].Weight = firstWeight;
                }
            }

            return result;
        }


        private delegate void VertexReadCallback(BinaryObjectReader reader, ref GPUVertex vertex);

        private static (int, VertexReadCallback)[] GetVertexReadCallbacks(IEnumerable<VertexElement> elements)
        {
            List<(int, VertexReadCallback)> result = [];

            foreach(VertexElement element in elements)
            {
                int usageIndex = element.UsageIndex;
                int weightIndexOffset = usageIndex * 4;
                VertexReadCallback? callback = null;

                switch(element.Type)
                {
                    case VertexType.Position:
                    case VertexType.Normal:
                        if(element.UsageIndex != 0)
                        {
                            continue;
                        }

                        Func<BinaryObjectReader, Vector3> vec3Reader = VertexFormatDecoder.GetVector3Decoder(element.Format);

                        if(element.Type == VertexType.Position)
                        {
                            callback = (reader, ref vtx) => vtx.Position = vec3Reader(reader);
                        }
                        else if(element.Type == VertexType.Normal)
                        {
                            callback = (reader, ref vtx) => vtx.Normal = Vector3.Normalize(vec3Reader(reader));
                        }

                        break;
                    case VertexType.Tangent:
                    case VertexType.Binormal:
                        if(element.UsageIndex > 1)
                        {
                            continue;
                        }

                        Func<BinaryObjectReader, Vector3> vec3Reader2 = VertexFormatDecoder.GetVector3Decoder(element.Format);

                        if(element.UsageIndex == 0)
                        {
                            if(element.Type == VertexType.Tangent)
                            {
                                callback = (reader, ref vtx) => vtx.UVDirection = new(Vector3.Normalize(vec3Reader2(reader)), vtx.UVDirection.Binormal);
                            }
                            else
                            {
                                callback = (reader, ref vtx) => vtx.UVDirection = new(vtx.UVDirection.Tangent, Vector3.Normalize(vec3Reader2(reader)));
                            }
                        }
                        else
                        {
                            if(element.Type == VertexType.Tangent)
                            {
                                callback = (reader, ref vtx) => vtx.UVDirection2 = new(Vector3.Normalize(vec3Reader2(reader)), vtx.UVDirection2.Binormal);
                            }
                            else
                            {
                                callback = (reader, ref vtx) => vtx.UVDirection2 = new(vtx.UVDirection2.Tangent, Vector3.Normalize(vec3Reader2(reader)));
                            }
                        }

                        break;
                    case VertexType.BlendIndices:
                        Func<BinaryObjectReader, Vector4Int> vec4intReader = VertexFormatDecoder.GetVector4IntDecoder(element.Format);

                        callback = (reader, ref vtx) =>
                        {
                            Vector4Int indices = vec4intReader(reader);

                            if(element.Format == VertexFormat.Ushort4)
                            {
                                (indices.W, indices.X) = (indices.X, indices.W);
                                (indices.Z, indices.Y) = (indices.Y, indices.Z);
                            }

                            vtx.Weights[weightIndexOffset].Index = unchecked((short)indices.W);
                            vtx.Weights[weightIndexOffset + 1].Index = unchecked((short)indices.Z);
                            vtx.Weights[weightIndexOffset + 2].Index = unchecked((short)indices.Y);
                            vtx.Weights[weightIndexOffset + 3].Index = unchecked((short)indices.X);
                        };
                        break;

                    case VertexType.BlendWeight:
                        Func<BinaryObjectReader, Vector4> weightReader = VertexFormatDecoder.GetVector4Decoder(element.Format);

                        callback = (reader, ref vtx) =>
                        {
                            Vector4 weights = weightReader(reader);

                            vtx.Weights[weightIndexOffset].Weight = weights.W;
                            vtx.Weights[weightIndexOffset + 1].Weight = weights.Z;
                            vtx.Weights[weightIndexOffset + 2].Weight = weights.Y;
                            vtx.Weights[weightIndexOffset + 3].Weight = weights.X;
                        };
                        break;

                    case VertexType.TexCoord:
                        Func<BinaryObjectReader, Vector2> vec2Reader = VertexFormatDecoder.GetVector2Decoder(element.Format);
                        callback = (reader, ref vtx) => vtx.TextureCoordinates[usageIndex] = vec2Reader(reader);
                        break;

                    case VertexType.Color:
                        Func<BinaryObjectReader, Vector4> vec4Reader = VertexFormatDecoder.GetVector4Decoder(element.Format);
                        callback = (reader, ref vtx) => vtx.Colors![usageIndex] = vec4Reader(reader);
                        break;
                }

                if(callback != null)
                {
                    result.Add((element.Offset, callback));
                }
            }

            return [.. result];
        }

    }
}
