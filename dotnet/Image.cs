using System.IO;
using SharpNeedle.IO;
using System.Collections.Generic;
using System;
using SharpNeedle.Utilities;
using SharpNeedle.Framework.HedgehogEngine.Mirage;
using SharpNeedle.Framework.HedgehogEngine.Needle.TextureStreaming;

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


        public static Image? LoadImage(string filepath, Dictionary<string, Package?> packages, string streamingDirectory)
        {
            IFile? file = FileSystem.Instance.Open(filepath);
            if(file == null)
            {
                return null;
            }

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
                    : new(filepath, info.UnpackDDS(package));
            }

            return new(filepath, null);
        }
    
        public static Dictionary<string, Image> LoadMaterialImages(Material[] materials, string materialDirectory, string streamingDirectory)
        {
            Dictionary<string, Image> result = [];
            Dictionary<string, Package?> packages = [];

            foreach(Material material in materials)
            {
                foreach(Texture texture in material.Texset.Textures)
                {
                    if(!result.ContainsKey(texture.PictureName!))
                    {
                        Image? image = LoadImage(Path.Join(materialDirectory, texture.PictureName + ".dds"), packages, streamingDirectory);
                        if(image != null)
                        {
                            result.Add(texture.PictureName!, image);
                        }
                    }
                }
            }

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
