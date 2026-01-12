using Amicitia.IO.Binary;
using Amicitia.IO.Streams;
using HEIO.NET.Internal.Modeling;
using SharpNeedle.Framework.HedgehogEngine.Mirage;
using SharpNeedle.Framework.HedgehogEngine.Mirage.MaterialData;
using SharpNeedle.Framework.HedgehogEngine.Mirage.ModelData;
using SharpNeedle.Framework.HedgehogEngine.Needle.Archive;
using SharpNeedle.IO;
using SharpNeedle.Resource;
using System;
using System.Collections.Generic;
using System.Linq;

namespace HEIO.NET.Internal
{
    public readonly struct MeshDataSet
    {
        public string Name { get; }
        public Type OriginalType { get; }
        public MeshData[] MeshData { get; }
        public Model.Node[]? Nodes { get; }
        public SampleChunkNode? SampleChunkNodeRoot { get; }

        public MeshDataSet(string name, Type originalType, MeshData[] meshData, Model.Node[]? nodes, SampleChunkNode? sampleChunkNodeRoot)
        {
            Name = name;
            OriginalType = originalType;
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

                meshDataSets[i] = new(baseModel.Name, baseModel.GetType(), meshes, nodes, baseModel.Root);
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

        public static ModelSet ReadModelFile<T>(IFile file, MeshImportSettings settings) where T : ModelBase, new()
        {
            string? signature = null;
            using (BinaryObjectReader reader = new(file.Open(), StreamOwnership.Transfer, Endianness.Big))
            {
                try
                {
                    signature = reader.ReadString(StringBinaryFormat.FixedLength, 6);
                }
                catch { }
            }

            T[] models;
            LODInfoBlock? lodInfo = null;

            if (signature == NeedleArchive.Signature)
            {
                NeedleArchive archive = new()
                {
                    OffsetMode = NeedleArchiveDataOffsetMode.SelfRelative
                };

                archive.Read(file);
                models = archive.DataBlocks.OfType<ModelBlock>().Select(x => (T)x.Resource!).ToArray();

                foreach (T model in models)
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
                T model = new();
                model.Read(file);
                models = [model];
            }

            return FromModels(models, lodInfo, settings);
        }

        public static ModelSet[] ReadModelFiles<T>(string[] filepaths, bool includeLoD, MeshImportSettings settings, out ResolveInfo resolveInfo) where T : ModelBase, new()
        {
            List<ModelSet> result = [];
            List<(MeshDataSet, IFile)> modelFiles = [];

            foreach (string filepath in filepaths)
            {
                IFile file = FileSystem.Instance.Open(filepath)!;
                ModelSet modelSet = ReadModelFile<T>(file, settings);

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

            DependencyResolverManager dependencyManager = new();
            resolveInfo = dependencyManager.ResolveDependencies(modelFiles, (x, r) => x.ResolveDependencies(r));

            return [.. result];
        }
    }
}
