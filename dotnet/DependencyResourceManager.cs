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
        private readonly Dictionary<string, IFile> _foundPacs = [];

        public IResourceResolver[] CollectResolvers(IDirectory directory, out string[] missing, out string[] pacs)
        {
            List<string> absoluteDependencies = [];

            ResolveDirectoryDependencies(directory, absoluteDependencies);

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
                    missingList.Append(dependency);
                }
            }

            missing = [.. missingList];
            pacs = [.. pacsList];

            return [
                new DirectoryResourceResolver(directory, GetResourceManagerForDirectory(directory)),
                ..absoluteDependencies.Select(x => _dependencyResolvers[x]).OfType<IResourceResolver>()
            ];
        }

        private void ResolveDirectoryDependencies(IDirectory directory, List<string> absoluteDependencies)
        {
            IFile? dependenciesFile = directory.GetFile("!DEPENDENCIES.txt");
            if(dependenciesFile == null)
            {
                return;
            }

            string[] dependencies = ReadDependencyLines(dependenciesFile);
            foreach(string dependency in dependencies)
            {
                if(absoluteDependencies.Contains(dependency))
                {
                    continue;
                }

                absoluteDependencies.Add(dependency);

                if(_dependencyResolvers.ContainsKey(dependency))
                {
                    continue;
                }

                FindDependencyDirectories(directory, dependency, out IDirectory? dependencyDirectory, out IFile? pacFile);

                if(dependencyDirectory != null)
                {
                    _dependencyResolvers[dependency] = new DirectoryResourceResolver(dependencyDirectory, GetResourceManagerForDirectory(dependencyDirectory));
                    ResolveDirectoryDependencies(directory, absoluteDependencies);
                }
                else
                {
                    _dependencyResolvers[dependency] = null;
                }

                if(pacFile != null)
                {
                    _foundPacs[dependency] = pacFile;
                }
            }
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
