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
    }
}
