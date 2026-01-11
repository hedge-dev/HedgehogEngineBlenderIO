using HEIO.NET.Internal.Modeling;
using SharpNeedle.Framework.HedgehogEngine.Mirage.MaterialData;
using SharpNeedle.Framework.HedgehogEngine.Mirage.ModelData;
using SharpNeedle.Framework.HedgehogEngine.Needle.Archive;
using SharpNeedle.IO;
using System;
using System.Collections.Generic;
using System.Linq;

namespace HEIO.NET.Internal
{
    public readonly struct ModelSet
    {
        public MeshData[][] MeshDataSets { get; }
        public LODInfoBlock? LODInfo { get; }

        public ModelSet(MeshData[][] meshDataSets, LODInfoBlock? lodInfo)
        {
            MeshDataSets = meshDataSets;
            LODInfo = lodInfo;
        }

        private static ModelSet FromModels(ModelBase[] models, LODInfoBlock? lodInfo, MeshImportSettings settings)
        {
            MeshData[][] meshData = new MeshData[models.Length][];

            for(int i = 0; i < models.Length; i++)
            {
                ModelBase baseModel = models[i];
                MeshData[] meshes;

                if(baseModel is TerrainModel terrainModel)
                {
                    meshes = [MeshData.FromHEModel(terrainModel, settings)];
                }
                else if(baseModel is Model model)
                {
                    meshes = MeshData.FromHEMeshGroups(model, settings);

                    if(model.Morphs != null)
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

                meshData[i] = meshes;
            }

            return new(meshData, lodInfo);
        }

        public static Material[] GetMaterials(ModelSet[] models)
        {
            return [
                .. models
                    .SelectMany(x => x.MeshDataSets)
                    .SelectMany(x => x)
                    .SelectMany(x => x.MeshSets)
                    .Where(x => x.Material.IsValid())
                    .Select(x => x.Material.Resource!)
                    .Distinct()
            ];
        }

        public static ModelSet ReadModelFile<T>(IFile file, MeshImportSettings settings) where T : ModelBase, new()
        {
            T[] models;
            LODInfoBlock? lodInfo = null;

            try
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
            catch
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
            List<(MeshData[], IFile)> modelFiles = [];

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
            resolveInfo = dependencyManager.ResolveDependencies(modelFiles, MeshData.ResolveManyDependencies);

            return [.. result];
        }
    }
}
