using System.IO;
using SharpNeedle.IO;
using System.Collections.Generic;
using System;
using SharpNeedle.Utilities;
using SharpNeedle.Framework.HedgehogEngine.Mirage;
using SharpNeedle.Framework.HedgehogEngine.Needle.TextureStreaming;
using System.Linq;
using static HEIO.NET.DependencyResolverManager;

namespace HEIO.NET
{

    public class Image
    {
        public string Filepath { get; } = string.Empty;

        public byte[]? StreamedData { get; }


        private Image(string filepath, byte[]? streamedData)
        {
            Filepath = filepath;
            StreamedData = streamedData;
        }


        public static Image? LoadImage(IFile file, Dictionary<string, Package?> packages, string streamingDirectory, out string? noNTSP, out bool noNTSI)
        {
            Stream stream = file.Open(FileAccess.Read);
            uint signature = BitConverter.ToUInt32(stream.ReadBytes(4));
            stream.Position = 0;
            noNTSP = null;
            noNTSI = false;

            if(signature == 0x4953544e)
            {
                Info info = new();
                info.Read(file);

                if(!packages.TryGetValue(info.PackageName, out Package? package))
                {
                    string ntspPath = Path.Join(streamingDirectory, info.PackageName + ".ntsp");
                    IFile? packageFile = FileSystem.Instance.Open(ntspPath);

                    if(packageFile != null)
                    {
                        package = new();
                        package.Read(packageFile);
                    }
                    else
                    {
                        noNTSP = info.PackageName;
                        noNTSI = true;
                    }

                    packages[info.PackageName] = package;
                }

                if(package == null)
                {
                    return null;
                }

                byte[] ddsData;
                try
                {
                    ddsData = info.UnpackDDS(package);
                }
                catch(InvalidDataException)
                {
                    noNTSI = true;
                    return null;
                }

                return new(file.Path, ddsData);
            }

            return new(file.Path, null);
        }

        public static Dictionary<string, Image> LoadDirectoryImages(string directory, string[] images, string streamingDirectory, out ResolveInfo info)
        {
            DependencyResolverManager dependencyManager = new();
            Dictionary<string, Image> result = [];
            Dictionary<string, Package?> packages = [];

            HashSet<string> missingStreamedImages = new();
            HashSet<string> unresolvedNTSPFiles = new();
            HashSet<string> unresolvedFiles = new();

            ResolverInfo resolver = dependencyManager.GetResolver(new HostDirectory(directory));

            foreach(string imageName in images)
            {
                string filename = imageName + ".dds";

                if(resolver.Resolver.GetFile(filename) is IFile imageFile)
                {
                    Image? image = LoadImage(imageFile, packages, streamingDirectory, out string? noNTSP, out bool noNTSI);

                    if(noNTSP != null)
                    {
                        unresolvedNTSPFiles.Add(noNTSP);
                    }

                    if(noNTSI)
                    {
                        missingStreamedImages.Add(imageName);
                    }

                    if(image != null)
                    {
                        result.Add(imageName!, image);
                    }
                }
                else
                {
                    unresolvedFiles.Add(filename);
                }
            }

            info = new(
                [.. unresolvedFiles],
                resolver.MissingDependencies,
                [.. resolver.PackedDependencies.Select(x => x.file.Path)],
                [.. unresolvedNTSPFiles],
                [.. missingStreamedImages]
            );

            return result;
        }

        public static Dictionary<string, Image> LoadMaterialImages(Material[] materials, string streamingDirectory, out ResolveInfo info)
        {
            DependencyResolverManager dependencyManager = new();
            Dictionary<string, Image> result = [];
            Dictionary<string, Package?> packages = [];

            HashSet<string> missingStreamedImages = new();
            HashSet<string> unresolvedNTSPFiles = new();

            info = dependencyManager.ResolveDependencies(materials.Select(x => (x, x.BaseFile!)), (resolver, material, file, unresolved) =>
            {
                foreach(Texture texture in material.Texset.Textures)
                {
                    if(string.IsNullOrWhiteSpace(texture.PictureName)
                        || result.ContainsKey(texture.PictureName))
                    {
                        continue;
                    }

                    string imageName = texture.PictureName + ".dds";

                    if(resolver.GetFile(imageName) is IFile imageFile)
                    {
                        Image? image = LoadImage(imageFile, packages, streamingDirectory, out string? noNTSP, out bool noNTSI);

                        if(noNTSP != null)
                        {
                            unresolvedNTSPFiles.Add(noNTSP);
                        }

                        if(noNTSI)
                        {
                            missingStreamedImages.Add(texture.PictureName);
                        }

                        if(image != null)
                        {
                            result.Add(texture.PictureName!, image);
                        }
                    }
                    else
                    {
                        unresolved.Add(imageName);
                    }
                }
            });

            info = ResolveInfo.Combine(info, new([], [], [], [.. unresolvedNTSPFiles], [.. missingStreamedImages]));

            return result;
        }


        public static unsafe void InvertGreenChannel(nint pixelPointer, int length)
        {
            float* pixels = (float*)pixelPointer;

            for(int i = 1; i < length; i += 4)
            {
                pixels[i] = 1 - pixels[i];
            }
        }
    }
}
