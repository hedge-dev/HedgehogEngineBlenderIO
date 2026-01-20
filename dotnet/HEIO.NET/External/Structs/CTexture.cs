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
                name = texture.Name.AllocString(),
                pictureName = texture.PictureName.AllocString(),
                texCoordIndex = texture.TexCoordIndex,
                wrapModeU = (byte)texture.WrapModeU,
                wrapModeV = (byte)texture.WrapModeV,
                type = texture.Type.AllocString()
            };
        }

        public readonly Texture ToInternal()
        {
            return new Texture()
            {
                Name = Util.ToString(name)!,
                PictureName = Util.ToString(pictureName)!,
                TexCoordIndex = texCoordIndex,
                WrapModeU = (WrapMode)wrapModeU,
                WrapModeV = (WrapMode)wrapModeV,
                Type = Util.ToString(type)!,
            };
        }
    }
}
