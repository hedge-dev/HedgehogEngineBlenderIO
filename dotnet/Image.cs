using System.IO;
using BCnEncoder.Decoder;
using Microsoft.Toolkit.HighPerformance;
using BCnEncoder.Shared;
using BCnEncoder.Shared.ImageFiles;
using SharpNeedle.HedgehogEngine.Needle.TextureStreaming;
using SharpNeedle.Utilities;
using SharpNeedle.IO;
using System.Collections.Generic;
using SharpNeedle.HedgehogEngine.Mirage;
using System;

namespace HEIO.NET
{

    public class Image
    {
        public readonly struct ImageData
        {
            public int Width { get; }
            public int Height { get; }
            public bool HasAlpha { get; }
            public bool IsHDR { get; }
            public float[] Colors { get; }

            public ImageData(int width, int height, bool hasAlpha, bool isHDR, float[] colors)
            {
                Width = width;
                Height = height;
                HasAlpha = hasAlpha;
                IsHDR = isHDR;
                Colors = colors;
            }
        }

        public string Filepath { get; } = string.Empty;

        public ImageData? StreamedData { get; }


        private Image(string filepath, ImageData? streamedData)
        {
            Filepath = filepath;
            StreamedData = streamedData;
        }


        private static ImageData LoadDDS(Stream stream)
        {
            float[] result;
            int width, height;
            bool hasAlpha = false, isHDR = false;

            BcDecoder decoder = new();
            DdsFile file = DdsFile.Load(stream);
            CompressionFormat format = decoder.GetFormat(file);

            if(format.IsHdrFormat())
            {
                isHDR = true;
                Span2D<ColorRgbFloat> hdrData = decoder.DecodeHdr2D(file).Span;

                width = hdrData.Width;
                height = hdrData.Height;
                result = new float[width * height * 4];

                for(int y = height - 1, destIndex = 0; y >= 0; y--)
                {
                    for(int x = 0; x < width; x++, destIndex += 4)
                    {
                        ColorRgbFloat color = hdrData[x, y];
                        result[destIndex] = color.r;
                        result[destIndex + 1] = color.g;
                        result[destIndex + 2] = color.b;
                        result[destIndex + 3] = 1;
                    }
                }
            }
            else
            {
                hasAlpha = format is CompressionFormat.Rgba
                    or CompressionFormat.Bgra
                    or CompressionFormat.Bc1WithAlpha
                    or CompressionFormat.Bc2
                    or CompressionFormat.Bc3
                    or CompressionFormat.Bc7
                    or CompressionFormat.AtcExplicitAlpha
                    or CompressionFormat.AtcInterpolatedAlpha;

                Span2D<ColorRgba32> rgbaData = decoder.Decode2D(file).Span;

                width = rgbaData.Width;
                height = rgbaData.Height;
                result = new float[width * height * 4];

                const float factor = 1f / byte.MaxValue;

                Func<ColorRgba32, float> getBlue;

                if(format == CompressionFormat.Bc5)
                {
                    getBlue = (rgba) =>
                    {
                        float x = (rgba.r * factor * 2) - 1;
                        float y = (rgba.g * factor * 2) - 1;
                        return float.Sqrt(1 - (x * x) - (y * y));
                    };
                }
                else
                {
                    getBlue = (rgba) => rgba.b * factor;
                }

                for(int y = height - 1, destIndex = 0; y >= 0; y--)
                {
                    for(int x = 0; x < width; x++, destIndex += 4)
                    {
                        ColorRgba32 color = rgbaData[y, x];
                        result[destIndex] = color.r * factor;
                        result[destIndex + 1] = color.g * factor;
                        result[destIndex + 2] = getBlue(color);
                        result[destIndex + 3] = color.a * factor;
                    }
                }
            }

            return new(width, height, hasAlpha, isHDR, result);
        }

        public static Image? LoadImage(string filepath, string streamingDirectory)
        {
            if(!File.Exists(filepath))
            {
                return null;
            }

            IFile file = FileSystem.Open(filepath);

            Stream stream = file.Open(FileAccess.Read);
            uint signature = stream.Read<uint>();
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

                MemoryStream ddsStream = new(info.UnpackDDS(package));
                ImageData ddsData = LoadDDS(ddsStream);
                return new(filepath, ddsData);
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
