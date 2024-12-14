using Amicitia.IO.Binary;
using Amicitia.IO.Streams;
using SharpNeedle.Framework.HedgehogEngine.Mirage;
using SharpNeedle.Structs;
using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Numerics;

namespace HEIO.NET.VertexUtils
{
    public struct GPUVertex
    {
        public Vector3 Position { get; set; }

        public Vector3 Normal { get; set; }

        public Vector3 Tangent { get; set; }

        public Vector2[] TextureCoordinates { get; set; }

        public Vector4[] Colors { get; set; }
        
        public bool UseByteColors { get; set; }

        public GPUVertex(int texcoordSets, int colorSets, bool useByteColors)
        {
            Position = default;
            Normal = default;
            Tangent = default;
            TextureCoordinates = new Vector2[texcoordSets];
            Colors = new Vector4[colorSets];
            Array.Fill(Colors, new(1));
            UseByteColors = useByteColors;
        }


        private delegate void VertexReadCallback(BinaryObjectReader reader, ref GPUVertex vertex);

        private static (int, VertexReadCallback)[] GetVertexReadCallbacks(IEnumerable<VertexElement> elements, bool useByteColors)
        {
            List<(int, VertexReadCallback)> result = [];

            foreach(VertexElement element in elements)
            {
                int usageIndex = element.UsageIndex;
                VertexReadCallback? callback = null;

                switch(element.Type)
                {
                    case VertexType.Position:
                    case VertexType.Normal:
                    case VertexType.Tangent:
                        if(element.UsageIndex != 0)
                        {
                            continue;
                        }

                        Func<BinaryObjectReader, Vector3> vec3Reader = VertexFormatDecoder.GetVector3Decoder(element.Format);

                        if(element.Type == VertexType.Position)
                        {
                            callback = (BinaryObjectReader reader, ref GPUVertex vtx) => vtx.Position = vec3Reader(reader);
                        }
                        else if(element.Type == VertexType.Normal)
                        {
                            callback = (BinaryObjectReader reader, ref GPUVertex vtx) => vtx.Normal = vec3Reader(reader);
                        }
                        else if(element.Type == VertexType.Tangent)
                        {
                            callback = (BinaryObjectReader reader, ref GPUVertex vtx) => vtx.Tangent = vec3Reader(reader);
                        }

                        break;

                    case VertexType.TexCoord:
                        Func<BinaryObjectReader, Vector2> vec2Reader = VertexFormatDecoder.GetVector2Decoder(element.Format);
                        callback = (BinaryObjectReader reader, ref GPUVertex vtx) => vtx.TextureCoordinates[usageIndex] = vec2Reader(reader);
                        break;

                    case VertexType.Color:
                        Func<BinaryObjectReader, Vector4> vec4Reader = VertexFormatDecoder.GetVector4Decoder(element.Format);
                        callback = (BinaryObjectReader reader, ref GPUVertex vtx) => vtx.Colors![usageIndex] = vec4Reader(reader);
                        break;
                }
            
                if(callback != null)
                {
                    result.Add((element.Offset, callback));
                }
            }

            return [.. result];
        }

        public static GPUVertex[] ReadVertexData(Mesh mesh, int texcoordSets, int colorSets, bool useByteColors)
        {
            using MemoryStream stream = new(mesh.Vertices);
            using BinaryObjectReader reader = new(stream, StreamOwnership.Retain, Endianness.Little);

            (int, VertexReadCallback)[] readCallbacks = GetVertexReadCallbacks(mesh.Elements, useByteColors);
            GPUVertex[] result = new GPUVertex[mesh.VertexCount];

            for(uint i = 0, o = 0; i < mesh.VertexCount; i++, o += mesh.VertexSize)
            {
                GPUVertex vertex = new(texcoordSets, colorSets, useByteColors);

                foreach((int offset, VertexReadCallback callback) in readCallbacks)
                {
                    reader.Seek(o + offset, SeekOrigin.Begin);
                    callback(reader, ref vertex);
                }
                
                result[i] = vertex; 
            }

            return result;
        }

    }
}
