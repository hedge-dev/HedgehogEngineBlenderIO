using SharpNeedle.Framework.HedgehogEngine.Mirage;
using SharpNeedle.Framework.HedgehogEngine.Needle.Archive;
using SharpNeedle.IO;
using SharpNeedle.Resource;
using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;

namespace HEIO.NET
{
    public static class ModelHelper
    {
        internal static T[] LoadModelFile<T>(IFile file, DependencyResolverManager dependencyManager) where T : ModelBase, new()
        {
            IResourceManager manager = dependencyManager.GetResourceManager(file.Parent);
            T[] models;

            try
            {
                NeedleArchive archive = new()
                {
                    OffsetMode = NeedleArchvieDataOffsetMode.SelfRelative
                };

                archive.Read(file);
                models = archive.DataBlocks.OfType<ModelBlock>().Select(x => (T)x.Resource!).ToArray();

                foreach(T model in models)
                {
                    if(string.IsNullOrWhiteSpace(model.Name))
                    {
                        model.Name = archive.Name;
                    }
                }
            }
            catch
            {
                models = [manager.Open<T>(file, false)];
            }

            return models;
        }

        public static T[][] LoadModelFiles<T>(string[] filepaths, bool includeLoD, out ResolveInfo resolveInfo) where T : ModelBase, new()
        {
            DependencyResolverManager dependencyManager = new();

            List<T[]> result = [];
            List<(ModelBase, IFile)> modelFiles = [];

            foreach(string filepath in filepaths)
            {
                IFile file = FileSystem.Instance.Open(filepath)!;
                T[] models = LoadModelFile<T>(file, dependencyManager);

                if(includeLoD)
                {
                    result.Add(models);
                    modelFiles.AddRange(models.Select(x => ((ModelBase)x, file)));
                }
                else
                {
                    result.Add([models[0]]);
                    modelFiles.Add((models[0], file));
                }

            }

            resolveInfo = dependencyManager.ResolveDependencies(modelFiles, ResolveModelMaterials);

            return [.. result];
        }

        internal static void ResolveModelMaterials(IResourceResolver resolver, ModelBase model, IFile file, HashSet<string> unresolved)
        {
            void ResolveMeshGroup(MeshGroup group)
            {
                foreach(Mesh mesh in group)
                {
                    if(mesh.Material.IsValid())
                    {
                        continue;
                    }

                    string filename = $"{mesh.Material.Name}.material";

                    if(resolver.Open<Material>(filename) is Material material)
                    {
                        mesh.Material = material;
                    }
                    else
                    {
                        unresolved.Add(filename);
                    }
                }
            }

            foreach(MeshGroup group in model.Groups)
            {
                ResolveMeshGroup(group);
            }

            if(model is Model modelmodel && modelmodel.Morphs?.Count > 0)
            {
                foreach(MorphModel morph in modelmodel.Morphs)
                {
                    ResolveMeshGroup(morph.Meshgroup!);
                }
            }
        }

        public static Material[] GetMaterials(ModelBase[][] models)
        {
            return models
                .SelectMany(x => x)
                .SelectMany(x => x.Groups.Concat((x as Model)?.Morphs?.Select(x => x.Meshgroup!) ?? []))
                .SelectMany(x => x)
                .Where(x => x.Material.IsValid())
                .Select(x => x.Material.Resource!)
                .Distinct()
                .ToArray();
        }
    }
}
