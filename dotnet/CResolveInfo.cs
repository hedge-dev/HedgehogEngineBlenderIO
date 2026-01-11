using HEIO.NET.Internal;
using System;
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
            CResolveInfo* result = Allocate.Alloc<CResolveInfo>();

            result->unresolvedFiles = Allocate.FromStringArray(resolveInfo.UnresolvedFiles);
            result->unresolvedFilesSize = resolveInfo.UnresolvedFiles.Length;

            result->missingDependencies = Allocate.FromStringArray(resolveInfo.MissingDependencies);
            result->missingDependenciesSize = resolveInfo.MissingDependencies.Length;

            result->packedDependencies = Allocate.FromStringArray(resolveInfo.PackedDependencies);
            result->packedDependenciesSize = resolveInfo.PackedDependencies.Length;

            result->unresolvedNTSPFiles = Allocate.FromStringArray(resolveInfo.UnresolvedNTSPFiles);
            result->unresolvedNTSPFilesSize = resolveInfo.UnresolvedNTSPFiles.Length;

            result->missingStreamedImages = Allocate.FromStringArray(resolveInfo.MissingStreamedImages);
            result->missingStreamedImagesSize = resolveInfo.MissingStreamedImages.Length;

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


        [UnmanagedCallersOnly(EntryPoint = "resolve_info_combine")]
        public static CResolveInfo* Combine(CResolveInfo** resolveInfos, nint resolveInfosSize)
        {
            try
            {
                ResolveInfo[] resolveInfoArray = new ResolveInfo[resolveInfosSize];
                for (int i = 0; i < resolveInfosSize; i++)
                {
                    resolveInfoArray[i] = resolveInfos[i]->ToResolveInfo();
                }

                return FromResolveInfo(ResolveInfo.Combine(resolveInfoArray));
            }
            catch (Exception exception)
            {
                ErrorHandler.HandleError(exception);
                return null;
            }
        }
    }
}
