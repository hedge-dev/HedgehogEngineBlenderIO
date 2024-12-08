﻿using SharpNeedle.Framework.HedgehogEngine.Mirage;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace HEIO.NET.VertexUtils
{
    public class GPUModel
    {
        public GPUVertex[] Vertices { get; }

        public int[] VertexSetSizes { get; }

        public int TexcoordSets { get; }

        public int ColorSets { get; }

        public bool UseByteColors { get; }

        public int[] Triangles { get; }

        public int[] TriangleSetSizes { get; }

        public Material[] SetMaterials { get; }

        public GPUModel(GPUVertex[] vertices, int[] vertexSetSizes, int texcoordSets, int colorSets, bool useByteColors, int[] triangles, int[] triangleSetSizes, Material[] setMaterials)
        {
            Vertices = vertices;
            VertexSetSizes = vertexSetSizes;
            TexcoordSets = texcoordSets;
            ColorSets = colorSets;
            UseByteColors = useByteColors;
            Triangles = triangles;
            TriangleSetSizes = triangleSetSizes;
            SetMaterials = setMaterials;
        }

        public static GPUModel ReadModelData(ModelBase model)
        {
            List<GPUVertex> vertices = [];
            List<int> vertexSetSizes = [];
            List<int> triangles = [];
            List<int> triangleSetSizes = [];
            List<Material?> materials = [];

            bool useTriangleList = false;

            if(model.Root?.FindNode("Topology") is SampleChunkNode topology)
            {
                useTriangleList = topology.Value == 3;
            }

            (VertexType type, byte usageIndex)[] types = model.Groups.SelectMany(x => x).SelectMany(x => x.Elements).Select(x => (x.Type, x.UsageIndex)).Distinct().ToArray();

            int GetSetNum(VertexType type)
            {
                return types.Any(x => x.type == type) ? types.Where(x => x.type == type).Max(x => x.usageIndex) + 1 : 0;
            }

            int texcoordSets = GetSetNum(VertexType.TexCoord);
            int colorSets = GetSetNum(VertexType.Color);
            bool useByteColors = colorSets > 0 && model.Groups
                    .SelectMany(x => x)
                    .SelectMany(x => x.Elements)
                    .Where(x => x.Type == VertexType.Color)
                    .Select(x => x.Format)
                    .All(x => x is VertexFormat.D3dColor
                        or VertexFormat.UByte4
                        or VertexFormat.UByte4Norm
                        or VertexFormat.Byte4
                        or VertexFormat.Byte4Norm);

            foreach(MeshGroup meshGroup in model.Groups)
            {
                foreach(Mesh mesh in meshGroup)
                {
                    IEnumerable<ushort> indices = useTriangleList
                        ? FlipTriangles(mesh.Faces)
                        : ExpandStrip(mesh.Faces);

                    int triangleIndexOffset = vertices.Count;
                    int prevLength = triangles.Count;
                    triangles.AddRange(indices.Select(x => x + triangleIndexOffset));

                    int triangleCount = (triangles.Count - prevLength) / 3;
                    triangleSetSizes.Add(triangleCount);
                    materials.Add(mesh.Material.Resource);

                    GPUVertex[] vertexData = GPUVertex.ReadVertexData(mesh, texcoordSets, colorSets, useByteColors);
                    vertices.AddRange(vertexData);
                    vertexSetSizes.Add(vertexData.Length);
                }
            }

            return new(
                [.. vertices],
                [.. vertexSetSizes],
                texcoordSets,
                colorSets,
                useByteColors,
                [.. triangles],
                [.. triangleSetSizes],
                [.. materials]);
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
            bool rev = true;

            for(int i = 2; i < indices.Length; i++, rev = !rev)
            {
                ushort i1 = indices[i - 2];
                ushort i2 = indices[i - 1];
                ushort i3 = indices[i];

                if(i1 == i2 || i2 == i3 || i3 == i1)
                {
                    continue;
                }

                if(rev)
                {
                    yield return i2;
                    yield return i1;
                    yield return i3;
                }
                else
                {
                    yield return i1;
                    yield return i2;
                    yield return i3;
                }
            }
        }
    }
}
