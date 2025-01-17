using Amicitia.IO.Binary;

namespace HEIO.NET.Modeling.ConvertTo
{
    internal static partial class VertexFormatEncoder
    {
        private static void EncodeFloat1(BinaryObjectWriter writer, float value)
        {
            writer.WriteSingle(value);
        }

        private static void EncodeInt1(BinaryObjectWriter writer, float value)
        {
            writer.WriteInt32((int)value);
        }

        private static void EncodeUInt1(BinaryObjectWriter writer, float value)
        {
            writer.WriteUInt32((uint)value);
        }

        private static void EncodeInt1Norm(BinaryObjectWriter writer, float value)
        {
            writer.WriteInt32((int)(float.Clamp(-1, 1, value) * int.MaxValue));
        }

        private static void EncodeUInt1Norm(BinaryObjectWriter writer, float value)
        {
            writer.WriteUInt32((uint)(float.Clamp(0, 1, value) * uint.MaxValue));
        }
    }
}
