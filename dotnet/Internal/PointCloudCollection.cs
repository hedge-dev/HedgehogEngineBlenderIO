using HEIO.NET.Internal.Modeling;
using SharpNeedle.Framework.HedgehogEngine.Bullet;
using SharpNeedle.Framework.HedgehogEngine.Mirage.ModelData;
using SharpNeedle.Framework.SonicTeam;
using SharpNeedle.IO;
using SharpNeedle.Resource;
using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Numerics;

namespace HEIO.NET.Internal
{
    public class PointCloudCollection
    {
        private static readonly string[] _modelFileExtensions = [".terrain-model", ".model"];
        private static readonly string[] _collisionFileExtensions = [".btmesh", "_col.btmesh"];
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


        public ModelSet[] Models { get; }

        public Collection[] ModelCollections { get; }

        public BulletMesh[] CollisionMeshes { get; }

        public Collection[] CollisionMeshCollections { get; }


        public PointCloudCollection(ModelSet[] models, Collection[] modelCollections, BulletMesh[] collisionMeshes, Collection[] collisionMeshCollections)
        {
            Models = models;
            ModelCollections = modelCollections;
            CollisionMeshes = collisionMeshes;
            CollisionMeshCollections = collisionMeshCollections;
        }


        public static PointCloudCollection LoadPointClouds(string[] filepaths, bool includeLoD, MeshImportSettings settings, out ResolveInfo resolveInfo)
        {
            DependencyResolverManager dependencyManager = new();
            List<PointCloud> pointClouds = [];

            foreach(string filepath in filepaths)
            {
                IFile file = FileSystem.Instance.Open(filepath)!;
                IResourceManager resolver = dependencyManager.GetResourceManager(file.Parent);

                pointClouds.Add(resolver.Open<PointCloud>(file, false));
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


            (Collection[] modelCollections, IFile[] modelSetFiles) = ToCollections(modelClouds);
            ModelSet[] modelSets = new ModelSet[modelSetFiles.Length];
            List<(MeshDataSet, IFile)> modelFiles = [];

            for(int i = 0; i < modelSets.Length; i++)
            {
                IFile file = modelSetFiles[i];
                ModelSet modelSet;

                if(Path.GetExtension(file.Name) == ".model")
                {
                    modelSet = ModelSet.ReadModelFile<Model>(file, settings);
                }
                else
                {
                    modelSet = ModelSet.ReadModelFile<TerrainModel>(file, settings);
                }

                if(includeLoD || modelSet.LODInfo == null)
                {
                    modelSets[i] = modelSet;
                    modelFiles.AddRange(modelSet.MeshDataSets.Select(x => (x, file)));
                }
                else
                {
                    modelSets[i] = new([modelSet.MeshDataSets[0]], null);
                    modelFiles.Add((modelSet.MeshDataSets[0], file));
                }
            }

            ResolveInfo terrainResolveInfo = dependencyManager.ResolveDependencies(modelFiles, (x, r) => x.ResolveDependencies(r));
            resolveInfo = ResolveInfo.Combine(pointCloudInfo, terrainResolveInfo);


            (Collection[] collisionMeshCollections, IFile[] bulletMeshFiles) = ToCollections(btmeshClouds);
            BulletMesh[] bulletMeshes = new BulletMesh[bulletMeshFiles.Length];

            for(int i = 0; i < bulletMeshes.Length; i++)
            {
                IFile file = bulletMeshFiles[i];
                BulletMesh mesh = new();
                mesh.Read(file);
                bulletMeshes[i] = mesh;
            }

            return new(modelSets, modelCollections, bulletMeshes, collisionMeshCollections);
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
