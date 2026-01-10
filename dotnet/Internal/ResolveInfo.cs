using System.Collections.Generic;

namespace HEIO.NET
{
    public readonly struct ResolveInfo
    {
        public string[] UnresolvedFiles { get; }

        public string[] MissingDependencies { get; }

        public string[] PackedDependencies { get; }

        public string[] UnresolvedNTSPFiles { get; }

        public string[] MissingStreamedImages { get; }

        public ResolveInfo()
        {
            UnresolvedFiles = [];
            MissingDependencies = [];
            PackedDependencies = [];
            UnresolvedNTSPFiles = [];
            MissingStreamedImages = [];
        }

        public ResolveInfo(string[] unresolvedFiles, string[] missingDependencies, string[] packedDependencies, string[] unresolvedNTSPFiles, string[] missingStreamedImages)
        {
            UnresolvedFiles = unresolvedFiles;
            MissingDependencies = missingDependencies;
            PackedDependencies = packedDependencies;
            UnresolvedNTSPFiles = unresolvedNTSPFiles;
            MissingStreamedImages = missingStreamedImages;
        }

        public static ResolveInfo Combine(params ResolveInfo[] infos)
        {
            HashSet<string> unresolvedFiles = [];
            HashSet<string> missingDependencies = [];
            HashSet<string> packedDependencies = [];
            HashSet<string> unresolvedNTSPFiles = [];
            HashSet<string> missingStreamedImages = [];

            foreach(ResolveInfo info in infos)
            {
                unresolvedFiles.UnionWith(info.UnresolvedFiles);
                missingDependencies.UnionWith(info.MissingDependencies);
                packedDependencies.UnionWith(info.PackedDependencies);
                unresolvedNTSPFiles.UnionWith(info.UnresolvedNTSPFiles);
                missingStreamedImages.UnionWith(info.MissingStreamedImages);
            }

            return new([.. unresolvedFiles], [.. missingDependencies], [.. packedDependencies], [.. unresolvedNTSPFiles], [.. missingStreamedImages]);
        }
    }
}
