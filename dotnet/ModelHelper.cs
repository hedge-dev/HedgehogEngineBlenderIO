using SharpNeedle.Framework.HedgehogEngine.Mirage;
using SharpNeedle.Framework.HedgehogEngine.Bullet;
using SharpNeedle.Framework.HedgehogEngine.Needle.Archive;
using SharpNeedle.IO;
using SharpNeedle.Resource;
using System.Collections.Generic;
using System.Linq;
using System;

namespace HEIO.NET
{
    public static class ModelHelper
    {
        public static ModelSet LoadModelFile<T>(IFile file) where T : ModelBase, new()
        {
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

                return new(
                    models,
                    archive.DataBlocks.OfType<LODInfoBlock>().First()
                );
            }
            catch
            {
                T model = new();
                model.Read(file);

                return new([model], null);
            }
        }

        public static ModelSet[] LoadModelFiles<T>(string[] filepaths, bool includeLoD, out ResolveInfo resolveInfo) where T : ModelBase, new()
        {
            List<ModelSet> result = [];
            List<(ModelBase, IFile)> modelFiles = [];

            foreach(string filepath in filepaths)
            {
                IFile file = FileSystem.Instance.Open(filepath)!;
                ModelSet modelSet = LoadModelFile<T>(file);

                if(includeLoD || modelSet.LODInfo == null)
                {
                    result.Add(modelSet);
                    modelFiles.AddRange(modelSet.Models.Select(x => ((ModelBase)x, file)));
                }
                else
                {
                    result.Add(new([modelSet.Models[0]], null));
                    modelFiles.Add((modelSet.Models[0], file));
                }

            }

            DependencyResolverManager dependencyManager = new();
            resolveInfo = dependencyManager.ResolveDependencies(modelFiles, ResolveModelMaterials);

            return [.. result];
        }

        public static BulletMesh[] LoadBulletMeshFiles(string[] filepaths)
        {
            BulletMesh[] result = new BulletMesh[filepaths.Length];

            for(int i = 0; i < filepaths.Length; i++)
            {
                BulletMesh mesh = new();
                IFile file = FileSystem.Instance.Open(filepaths[i])!;
                mesh.Read(file);
                result[i] = mesh;
            }

            return result;
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

        public static Material[] GetMaterials(ModelSet[] models)
        {
            return models
                .SelectMany(x => x.Models)
                .SelectMany(x => x.Groups.Concat((x as Model)?.Morphs?.Select(x => x.Meshgroup!) ?? []))
                .SelectMany(x => x)
                .Where(x => x.Material.IsValid())
                .Select(x => x.Material.Resource!)
                .Distinct()
                .ToArray();
        }
    
        public static NeedleArchive CreateLODArchive(ModelBase[] models, byte[] lodCascades, float[] lodUnknowns)
        {
            NeedleArchive result = new()
            {
                OffsetMode = NeedleArchvieDataOffsetMode.SelfRelative
            };

            LODInfoBlock lodBlock = new()
            {
                Unknown1 = 4
            };
            result.DataBlocks.Add(lodBlock);

            (ModelBase model, byte lodCascade, float lodUnknown)[] items = new (ModelBase model, byte lodCascade, float lodUnknown)[models.Length];
            for(int i = 0; i < items.Length; i++)
            {
                items[i] = (models[i], lodCascades[i], lodUnknowns[i]);
            }

            Array.Sort(items, (a, b) => a.lodCascade.CompareTo(b.lodCascade));

            if(items[^1].lodCascade != 31)
            {
                lodBlock.Unknown1 |= 0x80;
            }

            foreach((ModelBase model, byte lodCascade, float lodUnknown) in items)
            {
                if(lodCascade > 31)
                {
                    throw new ArgumentException($"Invalid LOD cascade level {lodCascades} for model {models[0].Name}!", nameof(lodCascades));
                }

                lodBlock.Items.Add(new()
                {
                    CascadeFlag = 1 << lodCascade,
                    Unknown2 = lodUnknown,
                    CascadeLevel = lodCascade
                });

                result.DataBlocks.Add(new ModelBlock()
                {
                    Resource = model
                });
            }


            return result;
        }
    }
}
