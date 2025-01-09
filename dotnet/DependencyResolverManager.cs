using SharpNeedle.IO;
using SharpNeedle.Resource;
using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;

namespace HEIO.NET
{
    public class DependencyResolverManager
    {
        public readonly struct ResolverInfo
        {
            public DependencyResourceResolver Resolver { get; }
            public string[] MissingDependencies { get; }
            public (string dependency, IFile file)[] PackedDependencies { get; }

            public ResolverInfo(DependencyResourceResolver resolver, string[] missingDependencies, (string, IFile)[] packedDependencies)
            {
                Resolver = resolver;
                MissingDependencies = missingDependencies;
                PackedDependencies = packedDependencies;
            }
        }

        private readonly Dictionary<IDirectory, DirectoryResourceResolver> _directoryResolvers = [];
        private readonly Dictionary<IDirectory, ResolverInfo> _resolvers = [];

        public int MaxDependencyDepth { get; set; } = 4;

        public ResolveInfo ResolveDependencies<T>(IEnumerable<(T, IFile)> data, Action<IResourceResolver, T, IFile, HashSet<string>> resolveFunc)
        {
            Dictionary<string, (IDirectory, List<(T, IFile)>)> directories = [];

            foreach((T item, IFile file) in data)
            {
                IDirectory parent = file.Parent;

                if(!directories.TryGetValue(parent.Path, out (IDirectory, List<(T, IFile)>) directory))
                {
                    directory = (parent, []);
                    directories[parent.Path] = directory;
                }

                directory.Item2.Add((item, file));
            }

            HashSet<string> unresolved = [];
            HashSet<string> missingDependencies = [];
            HashSet<string> dependencyPacFiles = [];

            foreach((IDirectory directory, List<(T, IFile)> directoryData) in directories.Values)
            {
                ResolverInfo resolver = GetResolver(directory);

                missingDependencies.UnionWith(resolver.MissingDependencies);
                dependencyPacFiles.UnionWith(resolver.PackedDependencies.Select(x => x.file.Path));

                foreach((T item, IFile file) in directoryData)
                {
                    resolveFunc(resolver.Resolver, item, file, unresolved);
                }
            }

            return new([.. unresolved], [.. missingDependencies], [.. dependencyPacFiles], [], []);
        }

        public ResolverInfo GetResolver(IDirectory directory)
        {
            if(_resolvers.TryGetValue(directory, out ResolverInfo result))
            {
                return result;
            }

            List<DependencyResourceResolver> dependencyResolvers = [];
            HashSet<string> missingDependencies = [];
            Dictionary<string, IFile> packedDependencies= [];


            if(directory.GetFile("!DEPENDENCIES.txt") is IFile dependenciesFile)
            {
                string[] dependencies = ReadDependencyLines(dependenciesFile);
                foreach(string dependency in dependencies)
                {
                    FindDependencyDirectories(directory, dependency, out IDirectory? dependencyDirectory, out IFile? pacFile);

                    if(dependencyDirectory == null)
                    {
                        if(pacFile != null)
                        {
                            packedDependencies[dependency] = pacFile;
                        }
                        else
                        {
                            missingDependencies.Add(dependency);
                        }

                        continue;
                    }
                    else
                    {
                        ResolverInfo dependencyResolverInfo = GetResolver(dependencyDirectory);

                        dependencyResolvers.Add(dependencyResolverInfo.Resolver);
                        missingDependencies.UnionWith(dependencyResolverInfo.MissingDependencies);

                        foreach((string, IFile) packedDependency in dependencyResolverInfo.PackedDependencies)
                        {
                            packedDependencies[packedDependency.Item1] = packedDependency.Item2;
                        }
                    }
                }
            }

            if(!_directoryResolvers.TryGetValue(directory, out DirectoryResourceResolver dirResolver))
            {
                dirResolver = new(directory, new ResourceManager());
                _directoryResolvers[directory] = dirResolver;
            }

            DependencyResourceResolver resolver = new(
                dirResolver,
                dependencyResolvers.Count == 0 ? null : [.. dependencyResolvers]
            );

            result = new(
                resolver, 
                [.. missingDependencies],
                [.. packedDependencies.Select(x => (x.Key, x.Value))]
            );

            _resolvers[directory] = result;
            return result;
        }

        public IResourceManager GetResourceManager(IDirectory directory)
        {
            if(!_directoryResolvers.TryGetValue(directory, out DirectoryResourceResolver dirResolver))
            {
                dirResolver = new(directory, new ResourceManager());
                _directoryResolvers[directory] = dirResolver;
            }

            return dirResolver.Manager!;
        }

        public void ResetResolvers()
        {
            _resolvers.Clear();
        }

        private void FindDependencyDirectories(IDirectory start, string dependency, out IDirectory? directory, out IFile? pacFile)
        {
            string relativePath = dependency.Replace('\\', Path.DirectorySeparatorChar);
            string pacPath = relativePath + ".pac";

            directory = null;
            pacFile = null;

            IDirectory? current = start.Parent;
            for(int i = 0; current != null && i < MaxDependencyDepth; i++, current = current.Parent)
            {
                if(current.GetDirectory(relativePath) is IDirectory resultDirectory)
                {
                    directory = resultDirectory;
                    return;
                }

                if(current.GetFile(pacPath) is IFile resultFile)
                {
                    pacFile = resultFile;
                    return;
                }
            }
        }
    

        private static string[] ReadDependencyLines(IFile file)
        {
            using Stream stream = file.Open(FileAccess.Read);
            using StreamReader reader = new(stream);

            List<string> result = [];
            while(reader.ReadLine() is string line)
            {
                if(!string.IsNullOrWhiteSpace(line))
                {
                    result.Add(line);
                }
            }

            return [.. result];
        }
    }
}
