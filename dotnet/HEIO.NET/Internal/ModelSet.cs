using Amicitia.IO.Binary;
using Amicitia.IO.Streams;
using HEIO.NET.Internal.Json;
using HEIO.NET.Internal.Modeling;
using SharpNeedle.Framework.HedgehogEngine.Mirage;
using SharpNeedle.Framework.HedgehogEngine.Mirage.MaterialData;
using SharpNeedle.Framework.HedgehogEngine.Mirage.ModelData;
using SharpNeedle.Framework.HedgehogEngine.Needle.Archive;
using SharpNeedle.IO;
using SharpNeedle.Resource;
using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Text.Json;
using System.Text.Json.Serialization;

namespace HEIO.NET.Internal
{
    public readonly struct MeshDataSet
    {
        public string Name { get; }
        public MeshData[] MeshData { get; }
        public Model.Node[]? Nodes { get; }
        public SampleChunkNode? SampleChunkNodeRoot { get; }

        [JsonConstructor]
        public MeshDataSet(string name, MeshData[] meshData, Model.Node[]? nodes, SampleChunkNode? sampleChunkNodeRoot)
        {
            Name = name;
            MeshData = meshData;
            Nodes = nodes;
            SampleChunkNodeRoot = sampleChunkNodeRoot;
        }

        public void ResolveDependencies(IResourceResolver resolver)
        {
            List<ResourceResolveException> exceptions = [];

            foreach (MeshData meshData in MeshData)
            {
                try
                {
                    meshData.ResolveDependencies(resolver);
                }
                catch (ResourceResolveException exc)
                {
                    exceptions.Add(exc);
                }
            }

            if (exceptions.Count > 0)
            {
                throw new ResourceResolveException(
                    $"Failed to resolve dependencies of {exceptions.Count} meshes",
                    [.. exceptions.SelectMany(x => x.GetRecursiveResources())]
                );
            }
        }

        public static ModelBase[] CompileMeshData(MeshDataSet[] compileData, ModelVersionMode versionMode, Topology topology, bool compressedVertexData, int multithreading)
        {
            return Modeling.ConvertTo.ModelConverter.CompileMeshData(
                compileData,
                versionMode,
                topology,
                compressedVertexData,
                multithreading
            );
        }


        public void SaveToJson(string directory)
        {
            string json = JsonSerializer.Serialize(this, SourceGenerationContext.Default.MeshDataSet);
            File.WriteAllText(Path.Combine(directory, Name + ".json"), json);
        }

        public static MeshDataSet FromJson(string json)
        {
            return JsonSerializer.Deserialize(json, SourceGenerationContext.Default.MeshDataSet);
        }
    }

    public readonly struct ModelSet
    {
        public MeshDataSet[] MeshDataSets { get; }
        public LODInfoBlock? LODInfo { get; }

        public ModelSet(MeshDataSet[] meshDataSets, LODInfoBlock? lodInfo)
        {
            MeshDataSets = meshDataSets;
            LODInfo = lodInfo;
        }

        private static ModelSet FromModels(ModelBase[] models, LODInfoBlock? lodInfo, MeshImportSettings settings)
        {
            MeshDataSet[] meshDataSets = new MeshDataSet[models.Length];

            for (int i = 0; i < models.Length; i++)
            {
                ModelBase baseModel = models[i];
                MeshData[] meshes;
                Model.Node[]? nodes = null;

                if (baseModel is TerrainModel terrainModel)
                {
                    meshes = [MeshData.FromHEModel(terrainModel, settings)];
                }
                else if (baseModel is Model model)
                {
                    meshes = MeshData.FromHEMeshGroups(model, settings);
                    nodes = [.. model.Nodes];

                    if (model.Morphs != null)
                    {
                        meshes = [
                            ..meshes,
                            ..model.Morphs.Select(x => MeshData.FromHEMorph(model, x, settings))
                        ];
                    }
                }
                else
                {
                    throw new NotSupportedException($"Model type \"{baseModel.GetType()}\" not supported!");
                }

                meshDataSets[i] = new(baseModel.Name, meshes, nodes, baseModel.Root);
            }

            return new(meshDataSets, lodInfo);
        }

        public static Material[] GetMaterials(ModelSet[] models)
        {
            return [
                .. models
                    .SelectMany(x => x.MeshDataSets)
                    .SelectMany(x => x.MeshData)
                    .SelectMany(x => x.MeshSets)
                    .Where(x => x.Material.IsValid())
                    .Select(x => x.Material.Resource!)
                    .Distinct()
            ];
        }

        public static ModelSet ReadModelFile(IFile file, MeshImportSettings settings)
        {
            Console.WriteLine("Reading model file " + file.Name);

            string? signature = null;
            using (BinaryObjectReader reader = new(file.Open(), StreamOwnership.Transfer, Endianness.Big))
            {
                try
                {
                    signature = reader.ReadString(StringBinaryFormat.FixedLength, 6);
                }
                catch { }
            }

            ModelBase[] models;
            LODInfoBlock? lodInfo = null;

            if (signature == NeedleArchive.Signature)
            {
                NeedleArchive archive = new()
                {
                    OffsetMode = NeedleArchiveDataOffsetMode.SelfRelative
                };

                archive.Read(file);
                models = archive.DataBlocks.OfType<ModelBlock>().Select(x => x.Resource!).ToArray();

                foreach (ModelBase model in models)
                {
                    if (string.IsNullOrWhiteSpace(model.Name))
                    {
                        model.Name = archive.Name;
                    }
                }

                lodInfo = archive.DataBlocks.OfType<LODInfoBlock>().First();
            }
            else
            {
                ModelBase model;

                if(Path.GetExtension(file.Name) == ".terrain-model")
                {
                    model = new TerrainModel();
                }
                else
                {
                    model = new Model();
                }

                model.Read(file);
                models = [model];
            }

            return FromModels(models, lodInfo, settings);
        }

        public static ModelSet[] ReadModelFiles(IFile[] files, bool includeLoD, MeshImportSettings settings, DependencyResolverManager? dependencyManager, out ResolveInfo resolveInfo)
        {
            List<ModelSet> result = [];
            List<(MeshDataSet, IFile)> modelFiles = [];

            foreach (IFile file in files)
            {
                ModelSet modelSet = ReadModelFile(file, settings);

                if (includeLoD || modelSet.LODInfo == null)
                {
                    result.Add(modelSet);
                    modelFiles.AddRange(modelSet.MeshDataSets.Select(x => (x, file)));
                }
                else
                {
                    result.Add(new([modelSet.MeshDataSets[0]], null));
                    modelFiles.Add((modelSet.MeshDataSets[0], file));
                }

            }

            dependencyManager ??= new();
            resolveInfo = dependencyManager.ResolveDependencies(modelFiles, (x, r) => x.ResolveDependencies(r));

            return [.. result];
        }

        public static ModelSet[] ReadModelFiles(string[] filepaths, bool includeLoD, MeshImportSettings settings, out ResolveInfo resolveInfo)
        {
            return ReadModelFiles(
                filepaths.Select(x => FileSystem.Instance.Open(x)!).ToArray(),
                includeLoD,
                settings,
                null,
                out resolveInfo
            );
        }

    }
}
