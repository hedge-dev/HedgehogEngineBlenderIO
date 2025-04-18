using SharpNeedle.Framework.HedgehogEngine.Bullet;
using SharpNeedle.Framework.HedgehogEngine.Mirage.MaterialData;
using SharpNeedle.Framework.HedgehogEngine.Mirage.ModelData;
using SharpNeedle.Framework.HedgehogEngine.Needle.Archive;
using SharpNeedle.IO;
using System;
using System.Collections.Generic;
using System.Linq;

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
                    OffsetMode = NeedleArchiveDataOffsetMode.SelfRelative
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
            resolveInfo = dependencyManager.ResolveDependencies(modelFiles);

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

        public static Material[] GetMaterials(ModelSet[] models)
        {
            return models
                .SelectMany(x => x.Models)
                .SelectMany(x => x.Groups.Concat((x as Model)?.Morphs?.Select(x => x.MeshGroup!) ?? []))
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
                OffsetMode = NeedleArchiveDataOffsetMode.SelfRelative
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
