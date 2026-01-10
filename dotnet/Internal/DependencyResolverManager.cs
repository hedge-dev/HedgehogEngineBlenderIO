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
        private class ResolverInfo
        {
            public IDirectory Directory { get; }
            public List<ResolverInfo> Dependencies { get; }
            public HashSet<string> MissingDependencies { get; }
            public Dictionary<string, IFile> PackedDependencies { get; }

            public ResolverInfo(IDirectory directory)
            {
                Directory = directory;
                Dependencies = [];
                MissingDependencies = [];
                PackedDependencies = [];
            }
        }

        private readonly Dictionary<IDirectory, ResourceManager> _resourceManagers = [];
        private readonly Dictionary<IDirectory, ResolverInfo> _resolvers = [];

        public int MaxDependencyDepth { get; set; } = 4;

        public ResolveInfo ResolveDependencies<T>(IEnumerable<(T, IFile)> data) where T : ResourceBase
        {
            return ResolveDependencies(data, (resolver, resource, file, unresolved) =>
            {
                try
                {
                    resource.ResolveDependencies(resolver);
                }
                catch(ResourceResolveException exc)
                {
                    foreach(string missingResource in exc.GetRecursiveResources())
                    {
                        unresolved.Add(missingResource);
                    }
                }
            });
        }

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
                IResourceResolver resolver = GetResourceResolver(directory, out ResolveInfo resolveInfo);

                missingDependencies.UnionWith(resolveInfo.MissingDependencies);
                dependencyPacFiles.UnionWith(resolveInfo.PackedDependencies);

                foreach((T item, IFile file) in directoryData)
                {
                    resolveFunc(resolver, item, file, unresolved);
                }
            }

            return new([.. unresolved], [.. missingDependencies], [.. dependencyPacFiles], [], []);
        }

        private ResolverInfo GetResolverInfo(IDirectory directory)
        {
            if(_resolvers.TryGetValue(directory, out ResolverInfo? result))
            {
                return result;
            }

            result = new(directory);
            _resolvers[directory] = result;

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
                            result.PackedDependencies[dependency] = pacFile;
                        }
                        else
                        {
                            result.MissingDependencies.Add(dependency);
                        }

                        continue;
                    }
                    else
                    {
                        result.Dependencies.Add(GetResolverInfo(dependencyDirectory));
                    }
                }
            }

            return result;
        }

        public IResourceResolver GetResourceResolver(IDirectory directory, out ResolveInfo resolveInfo)
        {
            ResolverInfo rootResolver = GetResolverInfo(directory);

            HashSet<ResolverInfo> alreadyIterated = [];
            AggregateResourceResolver result = [];
            Stack<ResolverInfo> stack = [];
            stack.Push(rootResolver);

            HashSet<string> missingDependencies = [];
            HashSet<string> dependencyPacFiles = [];

            while(stack.TryPop(out ResolverInfo? resolver))
            {
                if(alreadyIterated.Contains(resolver))
                {
                    continue;
                }

                alreadyIterated.Add(resolver);

                result.Add(new DirectoryResourceResolver(resolver.Directory, GetResourceManager(resolver.Directory)));

                foreach(ResolverInfo dependency in resolver.Dependencies.Reverse<ResolverInfo>())
                {
                    stack.Push(dependency);
                }

                missingDependencies.UnionWith(resolver.MissingDependencies);
                dependencyPacFiles.UnionWith(resolver.PackedDependencies.Values.Select(x => x.Path));
            }

            resolveInfo = new([], [.. missingDependencies], [.. dependencyPacFiles], [], []);

            return result;
        }

        public IResourceManager GetResourceManager(IDirectory directory)
        {
            if(!_resourceManagers.TryGetValue(directory, out ResourceManager? result))
            {
                result = new();
                _resourceManagers[directory] = result;
            }

            return result;
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
