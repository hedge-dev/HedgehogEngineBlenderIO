using SharpNeedle.Framework.HedgehogEngine.Mirage.MaterialData;

namespace HEIO.NET.External.Structs
{
    public unsafe struct CTexture : IConvertInternal<Texture>
    {
        public char* name;
        public char* pictureName;
        public byte texCoordIndex;
        public byte wrapModeU;
        public byte wrapModeV;
        public char* type;

        public static CTexture FromInternal(Texture texture)
        {
            return new()
            {
                name = texture.Name.ToPointer(),
                pictureName = texture.PictureName.ToPointer(),
                texCoordIndex = texture.TexCoordIndex,
                wrapModeU = (byte)texture.WrapModeU,
                wrapModeV = (byte)texture.WrapModeV,
                type = texture.Type.ToPointer()
            };
        }

        public readonly Texture ToInternal()
        {
            return new Texture()
            {
                Name = Util.FromPointer(name)!,
                PictureName = Util.FromPointer(pictureName)!,
                TexCoordIndex = texCoordIndex,
                WrapModeU = (WrapMode)wrapModeU,
                WrapModeV = (WrapMode)wrapModeV,
                Type = Util.FromPointer(type)!,
            };
        }
    }
}
