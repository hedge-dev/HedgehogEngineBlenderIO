using HEIO.NET.Internal.Modeling;

namespace HEIO.NET.External.Structs
{
    public unsafe struct CCollisionMeshDataGroup : IConvertInternal<CollisionMeshDataGroup>
    {
        public uint size;
        public uint layer;
        public bool isConvex;
        public uint convexType;
        public byte* convexFlagValues;
        public nint convexFlagValuesSize;

        public static CCollisionMeshDataGroup FromInternal(CollisionMeshDataGroup group)
        {
            return new()
            {
                size = group.Size,
                layer = group.Layer,
                isConvex = group.IsConvex,
                convexType = group.ConvexType,
                convexFlagValues = Allocate.AllocFromArray(group.ConvexFlagValues),
                convexFlagValuesSize = group.ConvexFlagValues?.Count ?? 0
            };
        }

        public CollisionMeshDataGroup ToInternal()
        {
            CollisionMeshDataGroup result = new(
                size,
                layer,
                isConvex
            ) {
                ConvexType = convexType,
                ConvexFlagValues = Util.ToArray(convexFlagValues, convexFlagValuesSize)
            };

            return result;
        }
    }
}
