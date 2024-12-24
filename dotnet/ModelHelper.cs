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
        internal static T[] LoadModelFile<T>(IFile file, DependencyResourceManager dependencyManager) where T : ModelBase, new()
        {
            ResourceManager manager = dependencyManager.GetResourceManagerForDirectory(file.Parent);
            T[] models;

            try
            {
                NeedleArchive archive = new()
                {
                    OffsetMode = NeedleArchvieDataOffsetMode.SelfRelative
                };

                archive.Read(file);
                models = archive.DataBlocks.OfType<ModelBlock>().Select(x => (T)x.Resource!).ToArray();
            }
            catch
            {
                models = [manager.Open<T>(file, false)];
            }

            return models;
        }

        public static T[][] LoadModelFiles<T>(string[] filepaths, out ResolveInfo resolveInfo) where T : ModelBase, new()
        {
            DependencyResourceManager dependencyManager = new();

            List<T[]> result = [];
            List<(ModelBase, IFile)> modelFiles = [];

            foreach(string filepath in filepaths)
            {
                IFile file = FileSystem.Instance.Open(filepath)!;
                T[] models = LoadModelFile<T>(file, dependencyManager);

                result.Add([models[0]]);
                modelFiles.Add((models[0], file));
            }

            resolveInfo = dependencyManager.ResolveDependencies(modelFiles, ResolveModelMaterials);

            return [.. result];
        }


        internal static void ResolveModelMaterials(IResourceResolver[] resolvers, ModelBase model, IFile file, HashSet<string> unresolved)
        {
            foreach(MeshGroup group in model.Groups)
            {
                foreach(Mesh mesh in group)
                {
                    if(mesh.Material.IsValid())
                    {
                        continue;
                    }

                    string filename = $"{mesh.Material.Name}.material";
                    bool resolved = false;

                    foreach(IResourceResolver resolver in resolvers)
                    {
                        try
                        {
                            mesh.Material = resolver.Open<Material>(filename)
                                ?? throw new InvalidDataException($"Material file \"{filename}\" failed to be read!");

                            resolved = true;
                            break;
                        }
                        catch(FileNotFoundException)
                        {

                        }
                    }

                    if(!resolved)
                    {
                        unresolved.Add(filename);
                    }
                }
            }
        }

        public static Material[] GetMaterials(ModelBase[][] models)
        {
            return models
                .SelectMany(x => x)
                .SelectMany(x => x.Groups)
                .SelectMany(x => x)
                .Where(x => x.Material.IsValid())
                .Select(x => x.Material.Resource!)
                .Distinct()
                .ToArray();
        }
    }
}
