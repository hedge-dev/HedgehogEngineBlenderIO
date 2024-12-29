using SharpNeedle.Framework.HedgehogEngine.Mirage;
using SharpNeedle.Resource;
using System.Linq;

namespace HEIO.NET.VertexUtils
{
    public class GPUMesh
    {
        public GPUVertex[] Vertices { get; }

        public int TexcoordSets { get; }

        public int ColorSets { get; }

        public bool UseByteColors { get; }

        public int[] Triangles { get; }

        public short[] BoneIndices { get; }

        public ResourceReference<Material> Material { get; }

        public MeshSlot Slot { get; }


        public GPUMesh(GPUVertex[] vertices, int texcoordSets, int colorSets, bool useByteColors, int[] triangles, short[] boneIndices, ResourceReference<Material> material, MeshSlot slot)
        {
            Vertices = vertices;
            TexcoordSets = texcoordSets;
            ColorSets = colorSets;
            UseByteColors = useByteColors;
            Triangles = triangles;
            BoneIndices = boneIndices;
            Material = material;
            Slot = slot;
        }


        public static GPUMesh ReadFromMesh(Mesh mesh, Topology topology)
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
                ? PolygonUtilities.FlipTriangles(mesh.Faces)
                : PolygonUtilities.ExpandStrip(mesh.Faces)];

            GPUVertex[] vertices = GPUVertex.ReadVertexData(mesh, texcoordSets, colorSets, weightCount, useByteColors);

            return new(
                vertices,
                texcoordSets,
                colorSets,
                useByteColors,
                triangles,
                mesh.BoneIndices,
                mesh.Material,
                mesh.Slot);
        }
    }
}
