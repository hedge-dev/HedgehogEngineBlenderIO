using SharpNeedle.Framework.HedgehogEngine.Mirage;
using SharpNeedle.Resource;
using System.Collections.Generic;
using System.Numerics;
using System.Text.Json.Serialization;

namespace HEIO.NET.Modeling
{
    public class MeshData
    {
        public string Name { get; set; }

        public IList<Vertex> Vertices { get; set; }

        public IList<int> TriangleIndices { get; set; }

        public IList<Vector3>? PolygonNormals { get; set; }

        public IList<Vector3>? PolygonTangents { get; set; }

        public IList<IList<Vector2>> TextureCoordinates { get; set; }

        public IList<IList<Vector4>> Colors { get; set; }

        public bool UseByteColors { get; set; }


        public IList<ResourceReference<Material>> SetMaterials { get; set; }

        public IList<MeshSlot> SetSlots { get; set; }

        public IList<int> SetSizes { get; set; }


        public IList<string> GroupNames { get; set; }

        public IList<int> GroupSizes { get; set; }

        [JsonConstructor]
        internal MeshData() : this(string.Empty, false) { }

        public MeshData(string name, bool polygonDirections)
        {
            Name = name;
            Vertices = [];
            TriangleIndices = [];
            PolygonNormals = polygonDirections ? [] : null;
            PolygonTangents = polygonDirections ? [] : null;
            TextureCoordinates = [];
            Colors = [];
            SetMaterials = [];
            SetSlots = [];
            SetSizes = [];
            GroupNames = [];
            GroupSizes = [];
        }

        public MeshData(
            string name,
            Vertex[] vertices,
            int[] triangleIndices,
            Vector3[]? polygonNormals,
            Vector3[]? polygonTangents,
            Vector2[][] textureCoordinates,
            Vector4[][] colors,
            bool useByteColors,
            ResourceReference<Material>[] setMaterials,
            MeshSlot[] setSlots,
            int[] setSizes,
            string[] groupNames,
            int[] groupSizes)
        {
            Name = name;
            Vertices = vertices;
            TriangleIndices = triangleIndices;
            PolygonNormals = polygonNormals;
            PolygonTangents = polygonTangents;
            TextureCoordinates = textureCoordinates;
            Colors = colors;
            UseByteColors = useByteColors;
            SetMaterials = setMaterials;
            SetSlots = setSlots;
            SetSizes = setSizes;
            GroupNames = groupNames;
            GroupSizes = groupSizes;
        }

        public static MeshData FromHEMorph(ModelBase model, MorphModel morph, VertexMergeMode vertexMergeMode, float mergeDistance, bool mergeSplitEdges)
        {
            Topology topology = model.Root?.FindNode("Topology")?.Value == 3
                ? Topology.TriangleList
                : Topology.TriangleStrips;

            ConvertFrom.GPUMeshConverter converter = new(
                morph.Name,
                topology,
                vertexMergeMode != VertexMergeMode.None,
                mergeDistance,
                mergeSplitEdges,
                morph.Targets.Count
            );

            converter.AddGroupInfo(morph.Meshgroup!.Name ?? string.Empty, morph.Meshgroup!.Count);

            for(int i = 0; i < morph.Meshgroup.Count; i++)
            {
                converter.AddMesh(morph.Meshgroup[i], i == morph.Meshgroup.Count - 1);
            }

            for(int i = 0; i < morph.Targets.Count; i++)
            {
                converter.AddMorphPositions(morph.Targets[i].Positions, i, 0);
            }

            converter.ProcessData();

            if(model is Model armatureModel)
            {
                converter.NormalizeBindPositions(armatureModel);
            }

            return converter.ResultData;
        }

        public static MeshData[] FromHEMeshGroups(ModelBase model, VertexMergeMode vertexMergeMode, float mergeDistance, bool mergeSplitEdges)
        {
            Topology topology = model.Root?.FindNode("Topology")?.Value == 3
                ? Topology.TriangleList
                : Topology.TriangleStrips;

            List<MeshData> results = [];

            foreach(MeshGroup group in model.Groups)
            {
                string meshname = model.Name;
                if(!string.IsNullOrWhiteSpace(group.Name))
                {
                    meshname += "_" + group.Name;
                }

                ConvertFrom.GPUMeshConverter converter = new(
                    meshname,
                    topology,
                    vertexMergeMode != VertexMergeMode.None,
                    mergeDistance,
                    mergeSplitEdges,
                    0
                );

                converter.AddGroupInfo(group.Name ?? string.Empty, group.Count);

                foreach(Mesh mesh in group)
                {
                    converter.AddMesh(mesh);

                    if(vertexMergeMode == VertexMergeMode.SubMesh)
                    {
                        converter.ProcessData();
                    }
                }

                converter.ProcessData();

                if(model is Model armatureModel)
                {
                    converter.NormalizeBindPositions(armatureModel);
                }

                results.Add(converter.ResultData);
            }

            return [.. results];
        }

        public static MeshData FromHEModel(ModelBase model, VertexMergeMode vertexMergeMode, float mergeDistance, bool mergeSplitEdges)
        {
            Topology topology = model.Root?.FindNode("Topology")?.Value == 3
                ? Topology.TriangleList
                : Topology.TriangleStrips;

            ConvertFrom.GPUMeshConverter converter = new(
                model.Name,
                topology,
                vertexMergeMode != VertexMergeMode.None,
                mergeDistance,
                mergeSplitEdges,
                0
            );

            foreach(MeshGroup group in model.Groups)
            {
                converter.AddGroupInfo(group.Name ?? string.Empty, group.Count);

                foreach(Mesh mesh in group)
                {
                    converter.AddMesh(mesh);

                    if(vertexMergeMode == VertexMergeMode.SubMesh)
                    {
                        converter.ProcessData();
                    }
                }

                if(vertexMergeMode == VertexMergeMode.SubMeshGroup)
                {
                    converter.ProcessData();
                }
            }

            converter.ProcessData();

            if(model is Model armatureModel)
            {
                converter.NormalizeBindPositions(armatureModel);
            }

            return converter.ResultData;
        }

    }
}
