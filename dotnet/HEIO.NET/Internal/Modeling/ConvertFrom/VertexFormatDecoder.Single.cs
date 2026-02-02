using Amicitia.IO.Binary;

namespace HEIO.NET.Internal.Modeling.ConvertFrom
{
    internal static partial class VertexFormatDecoder
    {
        private static float DecodeFloat1(BinaryObjectReader reader)
        {
            return reader.ReadSingle();
        }

        private static float DecodeInt1(BinaryObjectReader reader)
        {
            return reader.ReadInt32();
        }

        private static float DecodeUInt1(BinaryObjectReader reader)
        {
            return reader.ReadUInt32();
        }

        private static float DecodeInt1Norm(BinaryObjectReader reader)
        {
            return reader.ReadInt32() / (float)int.MaxValue;
        }

        private static float DecodeUInt1Norm(BinaryObjectReader reader)
        {
            return reader.ReadUInt32() / (float)uint.MaxValue;
        }
    }
}
