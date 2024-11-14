using System.IO;
using BCnEncoder.Decoder;
using Microsoft.Toolkit.HighPerformance;
using BCnEncoder.Shared;
using BCnEncoder.Shared.ImageFiles;

namespace HEIO.NET
{
    public static class Image
    {
        public static (int width, int height, float[] colors, bool hasAlpha, bool isHDR)? LoadDDS(string filepath)
        {
            if(!File.Exists(filepath))
            {
                return null;
            }

            float[] result;
            int width, height;
            bool hasAlpha = false, isHDR = false;

            using(FileStream stream = File.Open(filepath, FileMode.Open))
            {
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

                    for(int y = height - 1, destIndex = 0; y >= 0; y--)
                    {
                        for(int x = 0; x < width; x++, destIndex += 4)
                        {
                            ColorRgba32 color = rgbaData[x, y];
                            result[destIndex] = color.r * factor;
                            result[destIndex + 1] = color.g * factor;
                            result[destIndex + 2] = color.b * factor;
                            result[destIndex + 3] = color.a * factor;
                        }
                    }
                }
            }

            return (width, height, result, hasAlpha, isHDR);
        }
    }
}
