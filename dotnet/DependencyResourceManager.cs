using SharpNeedle.IO;
using SharpNeedle.Resource;
using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace HEIO.NET
{
    public class DependencyResourceManager
    {
        private readonly Dictionary<string, ResourceManager> _directoryResourceManagers = [];
        private readonly Dictionary<string, IResourceResolver?> _dependencyResolvers = [];
        private readonly Dictionary<string, string[]> _absoluteDependencies = [];
        private readonly Dictionary<string, IFile> _foundPacs = [];

        public ResolveInfo ResolveDependencies<T>(IEnumerable<(T, IFile)> data, Action<IResourceResolver[], T, IFile, HashSet<string>> resolveFunc)
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
                IResourceResolver[] resolvers = CollectResolvers(directory, out string[] missing, out string[] pacs);

                missingDependencies.UnionWith(missing);
                dependencyPacFiles.UnionWith(pacs);

                foreach((T item, IFile file) in directoryData)
                {
                    resolveFunc(resolvers, item, file, unresolved);
                }
            }

            return new([.. unresolved], [.. missingDependencies], [.. dependencyPacFiles]);
        }

        public IResourceResolver[] CollectResolvers(IDirectory directory, out string[] missing, out string[] pacs)
        {
            string[] absoluteDependencies = ResolveDirectoryDependencies(directory);

            List<string> missingList = [];
            List<string> pacsList = [];

            foreach(string dependency in absoluteDependencies)
            {
                if(_dependencyResolvers[dependency] != null)
                {
                    continue;
                }

                if(_foundPacs.TryGetValue(dependency, out IFile? file))
                {
                    pacsList.Add(file.Path);
                }
                else
                {
                    missingList.Add(dependency);
                }
            }

            missing = [.. missingList];
            pacs = [.. pacsList];

            return [
                new DirectoryResourceResolver(directory, GetResourceManagerForDirectory(directory)),
                ..absoluteDependencies.Select(x => _dependencyResolvers[x]).OfType<IResourceResolver>()
            ];
        }

        private string[] ResolveDirectoryDependencies(IDirectory directory)
        {
            IFile? dependenciesFile = directory.GetFile("!DEPENDENCIES.txt");
            if(dependenciesFile == null)
            {
                return [];
            }

            List<string> result = [];

            string[] dependencies = ReadDependencyLines(dependenciesFile);
            foreach(string dependency in dependencies)
            {
                if(result.Contains(dependency))
                {
                    continue;
                }

                result.Add(dependency);

                if(_dependencyResolvers.ContainsKey(dependency))
                {
                    result.AddRange(_absoluteDependencies[dependency]);
                    continue;
                }

                FindDependencyDirectories(directory, dependency, out IDirectory? dependencyDirectory, out IFile? pacFile);

                if(dependencyDirectory != null)
                {
                    _dependencyResolvers[dependency] = new DirectoryResourceResolver(dependencyDirectory, GetResourceManagerForDirectory(dependencyDirectory));
                    string[] absoluteDependencies = ResolveDirectoryDependencies(dependencyDirectory);
                    _absoluteDependencies[dependency] = absoluteDependencies;
                    result.AddRange(absoluteDependencies);
                }
                else
                {
                    _dependencyResolvers[dependency] = null;
                    _absoluteDependencies[dependency] = [];
                }

                if(pacFile != null)
                {
                    _foundPacs[dependency] = pacFile;
                }
            }

            return [.. result];
        }

        public ResourceManager GetResourceManagerForDirectory(IDirectory directory)
        {
            if(!_directoryResourceManagers.TryGetValue(directory.Path, out ResourceManager? resourceManager))
            {
                resourceManager = new();
                _directoryResourceManagers[directory.Path] = resourceManager;
            }

            return resourceManager;
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

        private static void FindDependencyDirectories(IDirectory start, string dependency, out IDirectory? directory, out IFile? pacFile)
        {
            string relativePath = dependency.Replace('\\', Path.DirectorySeparatorChar);
            string pacPath = relativePath + ".pac";

            directory = null;
            pacFile = null;

            IDirectory? current = start.Parent;
            for(int i = 0; current != null && i < 4; i++, current = current.Parent)
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
    
    }
}
