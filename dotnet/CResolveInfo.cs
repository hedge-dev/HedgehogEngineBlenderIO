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

        [UnmanagedCallersOnly(EntryPoint = "resolve_info_free")]
        public static void Free(CResolveInfo* resolveInfo)
        {
            try
            {
                Util.FreeStringArray(resolveInfo->unresolvedFiles, resolveInfo->unresolvedFilesSize);
                Util.FreeStringArray(resolveInfo->missingDependencies, resolveInfo->missingDependenciesSize);
                Util.FreeStringArray(resolveInfo->packedDependencies, resolveInfo->packedDependenciesSize);
                Util.FreeStringArray(resolveInfo->unresolvedNTSPFiles, resolveInfo->unresolvedNTSPFilesSize);
                Util.FreeStringArray(resolveInfo->missingStreamedImages, resolveInfo->missingStreamedImagesSize);

                Util.Free(resolveInfo);
            }
            catch (Exception exception)
            {
                ErrorHandler.HandleError(exception);
                return;
            }
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
