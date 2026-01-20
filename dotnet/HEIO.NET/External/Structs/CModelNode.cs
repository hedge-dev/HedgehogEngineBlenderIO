using SharpNeedle.Framework.HedgehogEngine.Mirage.ModelData;
using System.Numerics;

namespace HEIO.NET.External.Structs
{
    public unsafe struct CModelNode : IConvertInternal<Model.Node>
    {
        public char* name;
        public int parentIndex;
        public Matrix4x4 transform;

        public static CModelNode FromInternal(Model.Node node)
        {
            return new()
            {
                name = node.Name.ToPointer(),
                parentIndex = node.ParentIndex,
                transform = node.Transform
            };
        }

        public readonly Model.Node ToInternal()
        {
            return new()
            {
                Name = Util.FromPointer(name)!,
                ParentIndex = parentIndex,
                Transform = transform
            };
        }
    }
}
