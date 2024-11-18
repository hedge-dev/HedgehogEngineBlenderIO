using System.IO;
using SharpNeedle.HedgehogEngine.Needle.TextureStreaming;
using SharpNeedle.IO;
using System.Collections.Generic;
using SharpNeedle.HedgehogEngine.Mirage;
using System;
using SharpNeedle.Utilities;

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


        public static Image? LoadImage(string filepath, string streamingDirectory)
        {
            if(!File.Exists(filepath))
            {
                return null;
            }

            IFile file = FileSystem.Open(filepath);

            Stream stream = file.Open(FileAccess.Read);
            uint signature = BitConverter.ToUInt32(stream.ReadBytes(4));
            stream.Position = 0;

            if(signature == 0x4953544e)
            {
                Info info = new();
                info.Read(file);

                string ntspPath = Path.Join(streamingDirectory, info.PackageName + ".ntsp");
                if(!File.Exists(ntspPath))
                {
                    return null;
                }

                Package package = new();
                package.Read(FileSystem.Open(ntspPath));

                return new(filepath, info.UnpackDDS(package));
            }

            return new(filepath, null);
        }
    
        public static Dictionary<string, Image> LoadMaterialImages(Material[] materials, string materialDirectory, string streamingDirectory)
        {
            Dictionary<string, Image> result = [];

            foreach(Material material in materials)
            {
                foreach(Texture texture in material.Texset.Textures)
                {
                    if(!result.ContainsKey(texture.PictureName))
                    {
                        Image? image = LoadImage(Path.Join(materialDirectory, texture.PictureName + ".dds"), streamingDirectory);
                        if(image != null)
                        {
                            result.Add(texture.PictureName, image);
                        }
                    }
                }
            }

            return result;
        }
    }
}
