using SharpNeedle.Framework.HedgehogEngine.Mirage.MaterialData;
using SharpNeedle.Framework.HedgehogEngine.Mirage.ModelData;
using SharpNeedle.Resource;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Numerics;
using System.Text.Json.Serialization;

namespace HEIO.NET.Internal.Modeling
{
    public class MeshDataSetInfo
    {
        public bool UseByteColors { get; }

        public bool Enable8Weights { get; }

        public bool EnableMultiTangent { get; }

        public ResourceReference<Material> Material { get; internal set; }

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

        public void ResolveDependencies(IResourceResolver resolver)
        {
            if (Material.IsValid())
            {
                return;
            }

            string resource = $"{Material.Name}.material";
            Material = resolver.Open<Material>(resource)
                ?? throw new ResourceResolveException("Failed to resolve Material", [resource]);
        }
    }

    public class MeshDataGroupInfo
    {
        public string Name { get; }
        public int Size { get; internal set; }

        public MeshDataGroupInfo(string name, int size)
        {
            Name = name;
            Size = size;
        }
    }

    public class MeshData
    {
        public string Name { get; set; }

        public IList<Vertex> Vertices { get; set; }

        public IList<int> TriangleIndices { get; set; }

        public IList<Vector3>? PolygonNormals { get; set; }

        public IList<UVDirection>? PolygonUVDirections { get; set; }

        public IList<UVDirection>? PolygonUVDirections2 { get; set; }

        public IList<IList<Vector2>> TextureCoordinates { get; set; }

        public IList<IList<Vector4>> Colors { get; set; }


        public IList<MeshDataSetInfo> MeshSets { get; set; }

        public IList<MeshDataGroupInfo> Groups { get; set; }

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
            PolygonUVDirections = polygonDirections ? [] : null;
            TextureCoordinates = [];
            Colors = [];
            MeshSets = [];
            Groups = [];
            MorphNames = null;
        }

        public MeshData(
            string name,
            Vertex[] vertices,
            int[] triangleIndices,
            Vector3[]? polygonNormals,
            UVDirection[]? polygonUVDirections,
            UVDirection[]? polygonUVDirections2,
            Vector2[][] textureCoordinates,
            Vector4[][] colors,
            MeshDataSetInfo[] meshSets,
            MeshDataGroupInfo[] groups,
            string[]? morphNames)
        {
            Name = name;
            Vertices = vertices;
            TriangleIndices = triangleIndices;
            PolygonNormals = polygonNormals;
            PolygonUVDirections = polygonUVDirections;
            PolygonUVDirections2 = polygonUVDirections2;
            TextureCoordinates = textureCoordinates;
            Colors = colors;
            MeshSets = meshSets;
            Groups = groups;
            MorphNames = morphNames;
        }

        public static MeshData FromHEMorph(ModelBase model, MorphModel morph, MeshImportSettings settings)
        {
            Topology topology = model.Root?.FindNode("Topology")?.Value == 3
                ? Topology.TriangleList
                : Topology.TriangleStrips;

            ConvertFrom.GPUMeshConverter converter = new(
                "Morph",
                topology,
                settings,
                morph.Targets.Count
            );

            converter.ResultData.Groups.Add(new(
                morph.MeshGroup!.Name ?? string.Empty, 
                morph.MeshGroup!.Count
            ));

            for(int i = 0; i < morph.MeshGroup.Count; i++)
            {
                converter.AddMesh(morph.MeshGroup[i], i == morph.MeshGroup.Count - 1);
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

        public static MeshData[] FromHEMeshGroups(ModelBase model, MeshImportSettings settings)
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
                    settings,
                    0
                );

                converter.ResultData.Groups.Add(new(group.Name ?? string.Empty, group.Count));

                foreach(Mesh mesh in group)
                {
                    converter.AddMesh(mesh);

                    if(settings.VertexMergeMode == VertexMergeMode.SubMesh)
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

        public static MeshData FromHEModel(ModelBase model, MeshImportSettings settings)
        {
            Topology topology = model.Root?.FindNode("Topology")?.Value == 3
                ? Topology.TriangleList
                : Topology.TriangleStrips;

            ConvertFrom.GPUMeshConverter converter = new(
                model.Name,
                topology,
                settings,
                0
            );

            foreach(MeshGroup group in model.Groups)
            {
                converter.ResultData.Groups.Add(new(group.Name ?? string.Empty, group.Count));

                foreach(Mesh mesh in group)
                {
                    converter.AddMesh(mesh);

                    if(settings.VertexMergeMode == VertexMergeMode.SubMesh)
                    {
                        converter.ProcessData();
                    }
                }

                if(settings.VertexMergeMode == VertexMergeMode.SubMeshGroup)
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

        public void ResolveDependencies(IResourceResolver resolver)
        {
            List<ResourceResolveException> exceptions = [];

            foreach (MeshDataSetInfo meshSet in MeshSets)
            {
                try
                {
                    meshSet.ResolveDependencies(resolver);
                }
                catch (ResourceResolveException exc)
                {
                    exceptions.Add(exc);
                }
            }

            if (exceptions.Count > 0)
            {
                throw new ResourceResolveException(
                    $"Failed to resolve dependencies of {exceptions.Count} mesh sets",
                    [.. exceptions.SelectMany(x => x.GetRecursiveResources())]
                );
            }
        }
    }
}
