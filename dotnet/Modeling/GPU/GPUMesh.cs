﻿using SharpNeedle.Framework.HedgehogEngine.Mirage;
using SharpNeedle.Resource;
using System.Collections.Generic;

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

        public Topology Topology { get; }

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
    }
}
