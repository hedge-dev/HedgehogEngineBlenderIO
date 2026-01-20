using HEIO.NET.Internal;

namespace HEIO.NET.External.Structs
{
    public unsafe struct CResolveInfo
    {
        public char** unresolvedFiles;
        public nint unresolvedFilesSize;

        public char** missingDependencies;
        public nint missingDependenciesSize;

        public char** packedDependencies;
        public nint packedDependenciesSize;

        public char** unresolvedNTSPFiles;
        public nint unresolvedNTSPFilesSize;

        public char** missingStreamedImages;
        public nint missingStreamedImagesSize;


        public static CResolveInfo FromInternal(ResolveInfo resolveInfo)
        {
            return new()
            {
                unresolvedFiles = Allocate.AllocStringArray(resolveInfo.UnresolvedFiles),
                unresolvedFilesSize = resolveInfo.UnresolvedFiles.Length,

                missingDependencies = Allocate.AllocStringArray(resolveInfo.MissingDependencies),
                missingDependenciesSize = resolveInfo.MissingDependencies.Length,

                packedDependencies = Allocate.AllocStringArray(resolveInfo.PackedDependencies),
                packedDependenciesSize = resolveInfo.PackedDependencies.Length,

                unresolvedNTSPFiles = Allocate.AllocStringArray(resolveInfo.UnresolvedNTSPFiles),
                unresolvedNTSPFilesSize = resolveInfo.UnresolvedNTSPFiles.Length,

                missingStreamedImages = Allocate.AllocStringArray(resolveInfo.MissingStreamedImages),
                missingStreamedImagesSize = resolveInfo.MissingStreamedImages.Length
            };
        }

        public readonly ResolveInfo ToResolveInfo()
        {
            return new(
                Util.ToStringArray(unresolvedFiles, unresolvedFilesSize),
                Util.ToStringArray(missingDependencies, missingDependenciesSize),
                Util.ToStringArray(packedDependencies, packedDependenciesSize),
                Util.ToStringArray(unresolvedNTSPFiles, unresolvedNTSPFilesSize),
                Util.ToStringArray(missingStreamedImages, missingStreamedImagesSize)
            );
        }
    }
}
