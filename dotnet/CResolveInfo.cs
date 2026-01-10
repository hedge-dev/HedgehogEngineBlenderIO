using HEIO.NET.Internal;
using System.Runtime.InteropServices;

namespace HEIO.NET
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


        public static CResolveInfo* FromResolveInfo(ResolveInfo resolveInfo)
        {
            CResolveInfo* result = Util.Alloc<CResolveInfo>();

            result->unresolvedFiles = Util.FromStringArray(resolveInfo.UnresolvedFiles);
            result->unresolvedFilesSize = resolveInfo.UnresolvedFiles.Length;

            result->missingDependencies = Util.FromStringArray(resolveInfo.MissingDependencies);
            result->missingDependenciesSize = resolveInfo.MissingDependencies.Length;

            result->packedDependencies = Util.FromStringArray(resolveInfo.PackedDependencies);
            result->packedDependenciesSize = resolveInfo.PackedDependencies.Length;

            result->unresolvedNTSPFiles = Util.FromStringArray(resolveInfo.UnresolvedNTSPFiles);
            result->unresolvedNTSPFilesSize = resolveInfo.UnresolvedNTSPFiles.Length;

            result->missingStreamedImages = Util.FromStringArray(resolveInfo.MissingStreamedImages);
            result->missingStreamedImagesSize = resolveInfo.MissingStreamedImages.Length;

            return result;
        }

        [UnmanagedCallersOnly(EntryPoint = "resolve_info_free")]
        public static void Free(CResolveInfo* resolveInfo)
        {
            Util.FreeStringArray(resolveInfo->unresolvedFiles, resolveInfo->unresolvedFilesSize);
            Util.FreeStringArray(resolveInfo->missingDependencies, resolveInfo->missingDependenciesSize);
            Util.FreeStringArray(resolveInfo->packedDependencies, resolveInfo->packedDependenciesSize);
            Util.FreeStringArray(resolveInfo->unresolvedNTSPFiles, resolveInfo->unresolvedNTSPFilesSize);
            Util.FreeStringArray(resolveInfo->missingStreamedImages, resolveInfo->missingStreamedImagesSize);

            Util.Free(resolveInfo);
        }
    }
}
