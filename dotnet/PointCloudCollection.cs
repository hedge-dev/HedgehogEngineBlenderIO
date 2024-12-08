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


        public TerrainModel[][] TerrainModels { get; }

        public Collection[] TerrainCollections { get; }


        public PointCloudCollection(TerrainModel[][] terrainModels, Collection[] terrainPoints)
        {
            TerrainModels = terrainModels;
            TerrainCollections = terrainPoints;
        }


        public static PointCloudCollection LoadPointClouds(string[] filepaths, out ResolveInfo resolveInfo)
        {
            DependencyResourceManager dependencyManager = new();
            List<PointCloud> pointClouds = [];

            foreach(string filepath in filepaths)
            {
                IFile file = FileSystem.Instance.Open(filepath)!;
                ResourceManager manager = dependencyManager.GetResourceManagerForDirectory(file.Parent);

                pointClouds.Add(manager.Open<PointCloud>(file, false));
            }

            List<(PointCloud, Dictionary<string, IFile>)> terrainClouds = [];
            List<(PointCloud, Dictionary<string, IFile>)> btmeshClouds = [];
            List<(PointCloud, Dictionary<string, IFile>)> lightClouds = [];

            ResolveInfo pointCloudInfo = dependencyManager.ResolveDependencies(
                pointClouds.Select(x => (x, x.BaseFile!)),
                (resolvers, pointcloud, file, unresolved) =>
                {
                    string fileExtension = Path.GetExtension(file.Name) switch
                    {
                        ".pcmodel" => ".terrain-model",
                        ".pccol" => ".btmesh",
                        ".pcrt" => ".light",
                        _ => throw new InvalidOperationException("Invalid point collection file extension!"),
                    };

                    Dictionary<string, IFile> resolvedFiles = [];

                    foreach(string resource in pointcloud.Instances.Select(x => x.ResourceName!).Distinct())
                    {
                        string filename = resource + fileExtension;
                        bool resolved = false;

                        foreach(IResourceResolver resolver in resolvers)
                        {
                            if(resolver.GetFile(filename) is IFile resourceFile)
                            {
                                resolvedFiles[resource] = resourceFile;
                                resolved = true;
                                break;
                            }
                        }

                        if(!resolved)
                        {
                            unresolved.Add(filename);
                        }
                    }

                    switch(fileExtension)
                    {
                        case ".terrain-model":
                            terrainClouds.Add((pointcloud, resolvedFiles));
                            break;
                        case ".btmesh":
                            btmeshClouds.Add((pointcloud, resolvedFiles));
                            break;
                        case ".light":
                            lightClouds.Add((pointcloud, resolvedFiles));
                            break;
                    }
                });


            (Collection[] terrainCollections, IFile[] terrainFiles) = ToCollections(terrainClouds);
            TerrainModel[][] terrainModels = new TerrainModel[terrainFiles.Length][];

            for(int i = 0; i < terrainModels.Length; i++)
            {
                IFile file = terrainFiles[i];
                terrainModels[i] = ModelHelper.LoadTerrainModel(file, dependencyManager);
            }

            ResolveInfo terrainResolveInfo = dependencyManager.ResolveDependencies(
                Enumerable.Range(0, terrainModels.Length)
                    .Select(x => (terrainModels[x][0], terrainFiles[x])),
                ModelHelper.ResolveModelMaterials);


            resolveInfo = ResolveInfo.Combine(pointCloudInfo, terrainResolveInfo);

            return new(
                terrainModels.Select<TerrainModel[], TerrainModel[]>(x => [x[0]]).ToArray(),
                terrainCollections
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
