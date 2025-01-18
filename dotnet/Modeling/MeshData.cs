using SharpNeedle.Framework.HedgehogEngine.Mirage;
using SharpNeedle.Resource;
using System.Collections.Generic;
using System.Linq;
using System.Numerics;
using System.Text.Json.Serialization;

namespace HEIO.NET.Modeling
{
    public class MeshDataSetInfo
    {
        public bool UseByteColors { get; }

        public bool Enable8Weights { get; }

        public bool EnableMultiTangent { get; }

        public ResourceReference<Material> Material { get; }

        public MeshSlot Slot { get; }

        public int Size { get; internal set; }

        public MeshDataSetInfo(bool useByteColors, bool enable8Weights, bool enableMultiTangent, ResourceReference<Material> material, MeshSlot slot, int size)
        {
            UseByteColors = useByteColors;
            Enable8Weights = enable8Weights;
            EnableMultiTangent = enableMultiTangent;
            Material = material;
            Slot = slot;
            Size = size;
        }
    }

    public class MeshData
    {
        public string Name { get; set; }

        public IList<Vertex> Vertices { get; set; }

        public IList<int> TriangleIndices { get; set; }

        public IList<Vector3>? PolygonNormals { get; set; }

        public IList<Vector3>? PolygonTangents { get; set; }

        public IList<Vector3>? PolygonTangents2 { get; set; }

        public IList<IList<Vector2>> TextureCoordinates { get; set; }

        public IList<IList<Vector4>> Colors { get; set; }


        public IList<MeshDataSetInfo> MeshSets { get; set; }

        public IList<string> GroupNames { get; set; }

        /// <summary>
        /// Number of sets in each group
        /// </summary>
        public IList<int> GroupSetCounts { get; set; }

        public IList<string>? MorphNames { get; set; }

        public bool UseByteColors => MeshSets.All(x => x.UseByteColors);


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
            MeshSets = [];
            GroupNames = [];
            GroupSetCounts = [];
            MorphNames = null;
        }

        public MeshData(
            string name,
            Vertex[] vertices,
            int[] triangleIndices,
            Vector3[]? polygonNormals,
            Vector3[]? polygonTangents,
            Vector3[]? polygonTangents2,
            Vector2[][] textureCoordinates,
            Vector4[][] colors,
            MeshDataSetInfo[] meshSets,
            string[] groupNames,
            int[] groupSizes,
            string[]? morphNames)
        {
            Name = name;
            Vertices = vertices;
            TriangleIndices = triangleIndices;
            PolygonNormals = polygonNormals;
            PolygonTangents = polygonTangents;
            PolygonTangents2 = polygonTangents2;
            TextureCoordinates = textureCoordinates;
            Colors = colors;
            MeshSets = meshSets;
            GroupNames = groupNames;
            GroupSetCounts = groupSizes;
            MorphNames = morphNames;
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

            converter.ResultData.MorphNames = [];
            for(int i = 0; i < morph.Targets.Count; i++)
            {
                converter.ResultData.MorphNames.Add(morph.Targets[i].Name ?? "Shape_" + i);
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
