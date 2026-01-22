using SharpNeedle.Framework.HedgehogEngine.Bullet;
using System.Collections.Generic;
using System.Numerics;

namespace HEIO.NET.External.Structs
{
    public unsafe struct CBulletPrimitive : IConvertInternal<BulletPrimitive>
    {
        public byte shapeType;
        public byte surfaceLayer;
        public byte surfaceType;
        public uint surfaceFlags;
        public Vector3 position;
        public Quaternion rotation;
        public Vector3 dimensions;

        public static CBulletPrimitive FromInternal(BulletPrimitive primitive)
        {
            return new()
            {
                shapeType = (byte)primitive.ShapeType,
                surfaceLayer = primitive.SurfaceLayer,
                surfaceType = primitive.SurfaceType,
                surfaceFlags = primitive.SurfaceFlags,
                position = primitive.Position,
                rotation = primitive.Rotation,
                dimensions = primitive.Dimensions
            };
        }

        public static CBulletPrimitive* FromInternalArray(IList<BulletPrimitive> primitives)
        {
            return Allocate.AllocFromArray(primitives, FromInternal);
        }

        public readonly BulletPrimitive ToInternal()
        {
            return new()
            {
                ShapeType = (BulletPrimiteShapeType)shapeType,
                SurfaceLayer = surfaceLayer,
                SurfaceType = surfaceType,
                SurfaceFlags = surfaceFlags,
                Position = position,
                Rotation = rotation,
                Dimensions = dimensions
            };
        }

        public static BulletPrimitive[] ToInternalArray(CBulletPrimitive* primitives, nint size)
        {
            return Util.ToArray<CBulletPrimitive, BulletPrimitive>(primitives, size) ?? [];
        }
    }
}
