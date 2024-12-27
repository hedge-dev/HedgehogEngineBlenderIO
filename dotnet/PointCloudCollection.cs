using SharpNeedle.Framework.HedgehogEngine.Mirage;
using SharpNeedle.Framework.SonicTeam;
using SharpNeedle.IO;
using SharpNeedle.Resource;
using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Numerics;

namespace HEIO.NET
{
    public class PointCloudCollection
    {
        private static readonly string[] _modelFileExtensions = [".terrain-model", ".model"];
        private static readonly string[] _collisionFileExtensions = [".bcmesh"];
        private static readonly string[] _lightFileExtensions = [".light"];

        public readonly struct Point
        {
            public string InstanceName { get; }

            public int ResourceIndex { get; }

            public Vector3 Position { get; }

            public Vector3 Rotation { get; }

            public Vector3 Scale { get; }


            public Point(string instanceName, int resourceIndex, Vector3 position, Vector3 rotation, Vector3 scale)
            {
                InstanceName = instanceName;
                ResourceIndex = resourceIndex;
                Position = position;
                Rotation = rotation;
                Scale = scale;
            }
        }

        public readonly struct Collection
        {
            public string Name { get; }

            public Point[] Points { get; }

            public Collection(string name, Point[] points)
            {
                Name = name;
                Points = points;
            }
        }


        public ModelBase[][] Models { get; }

        public Collection[] ModelCollections { get; }


        public PointCloudCollection(ModelBase[][] models, Collection[] modelCollections)
        {
            Models = models;
            ModelCollections = modelCollections;
        }


        public static PointCloudCollection LoadPointClouds(string[] filepaths, out ResolveInfo resolveInfo)
        {
            DependencyResolverManager dependencyManager = new();
            List<PointCloud> pointClouds = [];

            foreach(string filepath in filepaths)
            {
                IFile file = FileSystem.Instance.Open(filepath)!;
                IResourceManager manager = dependencyManager.GetResourceManager(file.Parent);

                pointClouds.Add(manager.Open<PointCloud>(file, false));
            }

            List<(PointCloud, Dictionary<string, IFile>)> modelClouds = [];
            List<(PointCloud, Dictionary<string, IFile>)> btmeshClouds = [];
            List<(PointCloud, Dictionary<string, IFile>)> lightClouds = [];

            ResolveInfo pointCloudInfo = dependencyManager.ResolveDependencies(
                pointClouds.Select(x => (x, x.BaseFile!)),
                (resolver, pointcloud, file, unresolved) =>
                {
                    string pcExtension = Path.GetExtension(file.Name);

                    string[] fileExtensions = pcExtension switch
                    {
                        ".pcmodel" => _modelFileExtensions,
                        ".pccol" => _collisionFileExtensions,
                        ".pcrt" => _lightFileExtensions,
                        _ => throw new InvalidOperationException("Invalid point collection file extension!"),
                    };

                    Dictionary<string, IFile> resolvedFiles = [];

                    foreach(string resource in pointcloud.Instances.Select(x => x.ResourceName!).Distinct())
                    {
                        bool resolved = false;

                        foreach(string fileExtension in fileExtensions)
                        {
                            string filename = resource + fileExtension;
                            
                            if(resolver.GetFile(filename) is IFile resourceFile)
                            {
                                resolvedFiles[resource] = resourceFile;
                                resolved = true;
                                break;
                            }
                        }

                        if(!resolved)
                        {
                            unresolved.Add(resource);
                        }
                    }

                    switch(pcExtension)
                    {
                        case ".pcmodel":
                            modelClouds.Add((pointcloud, resolvedFiles));
                            break;
                        case ".pccol":
                            btmeshClouds.Add((pointcloud, resolvedFiles));
                            break;
                        case ".pcrt":
                            lightClouds.Add((pointcloud, resolvedFiles));
                            break;
                    }
                });


            (Collection[] modelCollections, IFile[] modelFiles) = ToCollections(modelClouds);
            ModelBase[][] models = new ModelBase[modelFiles.Length][];

            for(int i = 0; i < models.Length; i++)
            {
                IFile file = modelFiles[i];

                if(Path.GetExtension(file.Name) == ".model")
                {
                    models[i] = ModelHelper.LoadModelFile<Model>(file, dependencyManager);
                }
                else
                {
                    models[i] = ModelHelper.LoadModelFile<TerrainModel>(file, dependencyManager);
                }
            }

            ResolveInfo terrainResolveInfo = dependencyManager.ResolveDependencies(
                Enumerable.Range(0, models.Length)
                    .Select(x => (models[x][0], modelFiles[x])),
                ModelHelper.ResolveModelMaterials);


            resolveInfo = ResolveInfo.Combine(pointCloudInfo, terrainResolveInfo);

            return new(
                models.Select<ModelBase[], ModelBase[]>(x => [x[0]]).ToArray(),
                modelCollections
            );
        }

        private static (Collection[], IFile[]) ToCollections(List<(PointCloud, Dictionary<string, IFile>)> clouds)
        {
            Dictionary<IFile, int> fileIndexMap = [];
            List<Collection> collections = [];

            foreach((PointCloud pointcloud, Dictionary<string, IFile> fileMap) in clouds)
            {
                Dictionary<string, int> resourceMap = [];

                foreach(KeyValuePair<string, IFile> file in fileMap)
                {
                    if(!fileIndexMap.TryGetValue(file.Value, out int index))
                    {
                        index = fileIndexMap.Count;
                        fileIndexMap[file.Value] = index;
                    }

                    resourceMap[file.Key] = index;
                }

                Point[] points = new Point[pointcloud.Instances.Count];
                for(int i = 0; i < points.Length; i++)
                {
                    PointCloud.InstanceData pcPoint = pointcloud.Instances[i];

                    if(!resourceMap.TryGetValue(pcPoint.ResourceName!, out int index))
                    {
                        index = -1;
                    }

                    points[i] = new(
                        pcPoint.Name!,
                        index,
                        pcPoint.Position,
                        pcPoint.Rotation,
                        pcPoint.Scale
                    );
                }

                collections.Add(new(pointcloud.Name, points));
            }

            IFile[] files = new IFile[fileIndexMap.Count];
            foreach(KeyValuePair<IFile, int> file in fileIndexMap)
            {
                files[file.Value] = file.Key;
            }

            return ([.. collections], files);
        }
    }
}
