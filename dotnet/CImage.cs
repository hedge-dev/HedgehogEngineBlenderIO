using HEIO.NET.Internal;
using SharpNeedle.Framework.HedgehogEngine.Mirage.MaterialData;
using SharpNeedle.IO;
using System;
using System.Collections.Generic;
using System.Runtime.InteropServices;

namespace HEIO.NET
{
    public unsafe struct CImage
    {
        public char* filePath;
        public byte* streamedData;
        public nint streamedDataSize;

        public static CImage* FromImage(Image image)
        {
            CImage* result = Util.Alloc<CImage>();

            result->filePath = image.Filepath.ToPointer();

            if (image.StreamedData != null)
            {
                result->streamedData = Util.Alloc<byte>(image.StreamedData.Length);
                result->streamedDataSize = image.StreamedData.Length;

                Marshal.Copy(image.StreamedData, 0, (nint)result->streamedData, image.StreamedData.Length);
            }
            else
            {
                result->streamedData = null;
                result->streamedDataSize = 0;
            }

            return result;
        }

        private static void InternalFree(CImage* image)
        {
            Util.Free(image->filePath);
            Util.Free(image->streamedData);
            Util.Free(image);
        }

        [UnmanagedCallersOnly(EntryPoint = "image_free")]
        public static void Free(CImage* image)
        {
            try
            {
                InternalFree(image);
            }
            catch (Exception exception)
            {
                ErrorHandler.HandleError(exception);
                return;
            }
        }

        [UnmanagedCallersOnly(EntryPoint = "image_load_directory_images")]
        public static CStringPointerPairs* LoadDirectoryImages(char* directory, char** images, nint imagesSize, char* streamingDirectory, CResolveInfo** resolveInfo)
        {
            try
            {
                string directoryString = Util.FromPointer(directory)!;
                string[] imagesStrings = Util.ToStringArray(images, imagesSize);
                string streamingDirectoryString = Util.FromPointer(streamingDirectory)!;

                Dictionary<string, Image> output = Image.LoadDirectoryImages(directoryString, imagesStrings, streamingDirectoryString, out ResolveInfo outInfo);

                *resolveInfo = CResolveInfo.FromResolveInfo(outInfo);

                return FromImageList(output);
            }
            catch (Exception exception)
            {
                ErrorHandler.HandleError(exception);
                return null;
            }
        }

        [UnmanagedCallersOnly(EntryPoint = "image_load_material_images")]
        public static CStringPointerPairs* LoadMaterialImages(CMaterial** materials, nint materialsSize, char* streamingDirectory, CResolveInfo** resolveInfo)
        {
            try
            {
                FileSystem system = new();

                Material[] snMaterials = new Material[materialsSize];
                IFile[] files = new IFile[materialsSize];

                for (int i = 0; i < materialsSize; i++)
                {
                    snMaterials[i] = materials[i]->ToMaterial();
                    files[i] = system.Open(Util.FromPointer(materials[i]->filePath)!)!;
                }

                string streamingDirectoryString = Util.FromPointer(streamingDirectory)!;
                Dictionary<string, Image> output = Image.LoadMaterialImages(snMaterials, files, streamingDirectoryString, out ResolveInfo outInfo);
                *resolveInfo = CResolveInfo.FromResolveInfo(outInfo);
                return FromImageList(output);
            }
            catch (Exception exception)
            {
                ErrorHandler.HandleError(exception);
                return null;
            }

        }

        private static CStringPointerPairs* FromImageList(Dictionary<string, Image> images)
        {
            CStringPointerPair* pairs = Util.Alloc<CStringPointerPair>(images.Count);
            int index = 0;
            foreach (KeyValuePair<string, Image> image in images)
            {
                CStringPointerPair* entry = &pairs[index];

                entry->name = image.Key.ToPointer();
                entry->pointer = FromImage(image.Value);

                index++;
            }

            CStringPointerPairs* result = Util.Alloc<CStringPointerPairs>();
            result->pairs = pairs;
            result->size = images.Count;

            return result;
        }

        [UnmanagedCallersOnly(EntryPoint = "image_free_list")]
        public static void FreeImageList(CStringPointerPairs* images)
        {
            try
            {
                for (int i = 0; i < images->size; i++)
                {
                    CStringPointerPair* image = &images->pairs[i];
                    Util.Free(image->name);
                    InternalFree((CImage*)image->pointer);
                }

                Util.Free(images->pairs);
                Util.Free(images);
            }
            catch (Exception exception)
            {
                ErrorHandler.HandleError(exception);
                return;
            }
        }

        [UnmanagedCallersOnly(EntryPoint = "image_invert_green_channel")]
        public static void InvertGreenChannel(float* pixels, int pixelsSize)
        {
            try
            {
                Image.InvertGreenChannel(pixels, pixelsSize);
            }
            catch (Exception exception)
            {
                ErrorHandler.HandleError(exception);
                return;
            }
        }
    }
}
