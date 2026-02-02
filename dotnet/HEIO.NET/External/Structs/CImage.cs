using HEIO.NET.Internal;

namespace HEIO.NET.External.Structs
{
    public unsafe struct CImage
    {
        public char* filePath;
        public byte* streamedData;
        public int streamedDataSize;

        public static CImage FromInternal(Image image)
        {
            CImage result = new()
            {
                filePath = image.Filepath.AllocString()
            };

            if (image.StreamedData != null)
            {
                result.streamedData = Allocate.AllocFromArray(image.StreamedData);
                result.streamedDataSize = image.StreamedData.Length;
            }

            return result;
        }
    }
}
