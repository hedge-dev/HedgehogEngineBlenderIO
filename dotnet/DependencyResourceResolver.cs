using SharpNeedle.IO;
using SharpNeedle.Resource;

namespace HEIO.NET
{
    public readonly struct DependencyResourceResolver : IResourceResolver
    {
        private readonly DirectoryResourceResolver _directoryResolver;
        private readonly DependencyResourceResolver[]? _dependencyResolvers;


        public DependencyResourceResolver(DirectoryResourceResolver directoryResolver) : this()
        {
            _directoryResolver = directoryResolver;
        }

        public DependencyResourceResolver(DirectoryResourceResolver directoryResolver, DependencyResourceResolver[]? dependencyResolvers)
        {
            _directoryResolver = directoryResolver;
            _dependencyResolvers = dependencyResolvers;
        }


        public readonly TRes? Open<TRes>(string fileName, bool resolveDependencies = true) where TRes : IResource, new()
        {
            if(_directoryResolver.Open<TRes>(fileName, false) is TRes resource)
            {
                if(resolveDependencies)
                {
                    resource.ResolveDependencies(this);
                }

                return resource;
            }

            if(_dependencyResolvers != null)
            {
                foreach(DependencyResourceResolver resolver in _dependencyResolvers)
                {
                    if(resolver.Open<TRes>(fileName, resolveDependencies) is TRes depResource)
                    {
                        return depResource;
                    }
                }
            }

            return default;
        }

        public readonly IFile? GetFile(string filename)
        {
            if(_directoryResolver.GetFile(filename) is IFile result)
            {
                return result;
            }

            if(_dependencyResolvers != null)
            {
                foreach(DependencyResourceResolver resolver in _dependencyResolvers)
                {
                    if(resolver.GetFile(filename) is IFile depResult)
                    {
                        return depResult;
                    }
                }
            }

            return null;
        }   
    }
}
