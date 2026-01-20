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
                unresolvedFiles = Allocate.FromStringArray(resolveInfo.UnresolvedFiles),
                unresolvedFilesSize = resolveInfo.UnresolvedFiles.Length,

                missingDependencies = Allocate.FromStringArray(resolveInfo.MissingDependencies),
                missingDependenciesSize = resolveInfo.MissingDependencies.Length,

                packedDependencies = Allocate.FromStringArray(resolveInfo.PackedDependencies),
                packedDependenciesSize = resolveInfo.PackedDependencies.Length,

                unresolvedNTSPFiles = Allocate.FromStringArray(resolveInfo.UnresolvedNTSPFiles),
                unresolvedNTSPFilesSize = resolveInfo.UnresolvedNTSPFiles.Length,

                missingStreamedImages = Allocate.FromStringArray(resolveInfo.MissingStreamedImages),
                missingStreamedImagesSize = resolveInfo.MissingStreamedImages.Length
            };
        }

        public static CResolveInfo* PointerFromInternal(ResolveInfo resolveInfo)
        {
            CResolveInfo* result = Allocate.Alloc<CResolveInfo>();
            *result = FromInternal(resolveInfo);
            return result;
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
