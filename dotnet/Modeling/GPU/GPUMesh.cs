using SharpNeedle.Framework.HedgehogEngine.Mirage.MaterialData;
using SharpNeedle.Framework.HedgehogEngine.Mirage.ModelData;
using SharpNeedle.Resource;
using System.Collections.Generic;
using System.Linq;

namespace HEIO.NET.Modeling.GPU
{
    internal class GPUMesh
    {
        public IList<GPUVertex> Vertices { get; }

        public int TexcoordSets { get; }

        public int ColorSets { get; }

        public bool UseByteColors { get; }

        public bool BlendIndex16 { get; set; }

        public bool MultiTangent { get; }

        public Topology Topology { get; private set; }

        public IList<int> Triangles { get; }

        public IList<short> BoneIndices { get; }

        public ResourceReference<Material> Material { get; }

        public MeshSlot Slot { get; }


        public GPUMesh(int texcoordSets, int colorSets, bool useByteColors, bool blendIndex16, bool multiTangent, Topology topology, ResourceReference<Material> material, MeshSlot slot)
        {
            Vertices = [];
            TexcoordSets = texcoordSets;
            ColorSets = colorSets;
            UseByteColors = useByteColors;
            BlendIndex16 = blendIndex16;
            MultiTangent = multiTangent;
            Topology = topology;
            Triangles = [];
            BoneIndices = [];
            Material = material;
            Slot = slot;
        }

        public GPUMesh(GPUVertex[] vertices, int texcoordSets, int colorSets, bool useByteColors, bool blendIndex16, bool multiTangent, Topology topology, int[] triangles, short[] boneIndices, ResourceReference<Material> material, MeshSlot slot)
        {
            Vertices = vertices;
            TexcoordSets = texcoordSets;
            ColorSets = colorSets;
            UseByteColors = useByteColors;
            BlendIndex16 = blendIndex16;
            MultiTangent = multiTangent;
            Topology = topology;
            Triangles = triangles;
            BoneIndices = boneIndices;
            Material = material;
            Slot = slot;
        }

        public void ToStrips()
        {
            if(Topology == Topology.TriangleStrips)
            {
                return;
            }

            int[][] strips = J113D.Strippify.TriangleStrippifier.Global.Strippify([.. Triangles]);
            List<int> triangles = (List<int>)Triangles;
            triangles.Clear();

            for(int i = 0; i < strips.Length; i++)
            {
                triangles.AddRange(strips[i]);

                if(i < strips.Length - 1)
                {
                    triangles.Add(ushort.MaxValue);
                }
            }

            Topology = Topology.TriangleStrips;
        }

        public void EvaluateBoneIndices(HashSet<short> usedBones)
        {
            if(usedBones.Count == 0)
            {
                return;
            }

            ((List<short>)BoneIndices).AddRange(usedBones.Order());

            if(usedBones.Max() <= BoneIndices.Count - 1)
            {
                return;
            }

            short[] boneMap = new short[usedBones.Max() + 2];
            boneMap[0] = -1;
            for(short i = 0; i < BoneIndices.Count; i++)
            {
                boneMap[BoneIndices[i] + 1] = i;
            }

            for(int i = 0; i < Vertices.Count; i++)
            {
                VertexWeight[] weights = Vertices[i].Weights;
                for(int j = 0; j < weights.Length; j++)
                {
                    weights[j].Index = boneMap[weights[j].Index + 1];
                }
            }
        }
    }
}
