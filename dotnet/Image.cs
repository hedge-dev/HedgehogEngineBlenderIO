using System.IO;
using SharpNeedle.IO;
using System.Collections.Generic;
using System;
using SharpNeedle.Utilities;
using SharpNeedle.Framework.HedgehogEngine.Mirage;
using SharpNeedle.Framework.HedgehogEngine.Needle.TextureStreaming;
using System.Linq;
using SharpNeedle.Resource;

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


        public static Image? LoadImage(IFile file, Dictionary<string, Package?> packages, string streamingDirectory)
        {
            Stream stream = file.Open(FileAccess.Read);
            uint signature = BitConverter.ToUInt32(stream.ReadBytes(4));
            stream.Position = 0;

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

                    packages[info.PackageName] = package;
                }

                return package == null 
                    ? null 
                    : new(file.Path, info.UnpackDDS(package));
            }

            return new(file.Path, null);
        }
    
        public static Dictionary<string, Image> LoadMaterialImages(Material[] materials, string streamingDirectory, out ResolveInfo info)
        {
            DependencyResourceManager dependencyManager = new();
            Dictionary<string, Image> result = [];
            Dictionary<string, Package?> packages = [];

            info = dependencyManager.ResolveDependencies(materials.Select(x => (x, x.BaseFile!)), (resolvers, material, file, unresolved) =>
            {
                foreach(Texture texture in material.Texset.Textures)
                {
                    if(string.IsNullOrWhiteSpace(texture.PictureName) 
                        || result.ContainsKey(texture.PictureName))
                    {
                        continue;
                    }

                    string imageName = texture.PictureName + ".dds";
                    bool resolved = false;

                    foreach(IResourceResolver resolver in resolvers)
                    {
                        if(resolver.GetFile(imageName) is IFile imageFile)
                        {
                            Image? image = LoadImage(imageFile, packages, streamingDirectory);
                            if(image != null)
                            {
                                result.Add(texture.PictureName!, image);
                            }

                            resolved = true;
                        }
                    }

                    if(!resolved)
                    {
                        unresolved.Add(imageName);
                    }
                }
            });

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
