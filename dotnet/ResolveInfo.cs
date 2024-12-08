using System.Collections.Generic;

namespace HEIO.NET
{
    public readonly struct ResolveInfo
    {
        public string[] UnresolvedFiles { get; }

        public string[] MissingDependencies { get; }

        public string[] PackedDependencies { get; }

        public ResolveInfo()
        {
            UnresolvedFiles = [];
            MissingDependencies = [];
            PackedDependencies = [];
        }

        public ResolveInfo(string[] unresolvedFiles, string[] missingDependencies, string[] packedDependencies)
        {
            UnresolvedFiles = unresolvedFiles;
            MissingDependencies = missingDependencies;
            PackedDependencies = packedDependencies;
        }

        public static ResolveInfo Combine(params ResolveInfo[] infos)
        {
            HashSet<string> unresolvedFiles = [];
            HashSet<string> missingDependencies = [];
            HashSet<string> packedDependencies = [];

            foreach(ResolveInfo info in infos)
            {
                unresolvedFiles.UnionWith(info.UnresolvedFiles);
                missingDependencies.UnionWith(info.MissingDependencies);
                packedDependencies.UnionWith(info.PackedDependencies);
            }

            return new([.. unresolvedFiles], [.. missingDependencies], [.. packedDependencies]);
        }
    }
}
