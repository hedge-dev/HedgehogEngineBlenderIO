using SharpNeedle.Framework.HedgehogEngine.Bullet;
using System.Numerics;

namespace HEIO.NET.External.Structs
{
    public unsafe struct CBulletShape : IConvertInternal<BulletShape>
    {
        public byte flags;
        public uint layer;

        public Vector3* vertices;
        public nint verticesSize;

        public uint* faces;
        public nint facesSize;

        public byte* bvh;
        public nint bvhSize;

        public ulong* types;
        public nint typesSize;

        public uint unknown1;
        public uint unknown2;

        public static CBulletShape FromInternal(BulletShape shape)
        {
            return new()
            {
                flags = (byte)shape.Flags,
                layer = shape.Layer,

                vertices = Allocate.AllocFromArray(shape.Vertices),
                verticesSize = shape.Vertices.Length,

                faces = Allocate.AllocFromArray(shape.Faces),
                facesSize = shape.Faces?.Length ?? 0,

                bvh = Allocate.AllocFromArray(shape.BVH),
                bvhSize = shape.BVH?.Length ?? 0,

                types = Allocate.AllocFromArray(shape.Types),
                typesSize = shape.Types.Length,

                unknown1 = shape.Unknown1,
                unknown2 = shape.Unknown2
            };
        }

        public readonly BulletShape ToInternal()
        {
            return new()
            {
                IsConvex = ((BulletShapeFlags)flags).HasFlag(BulletShapeFlags.IsConvexShape),
                Layer = layer,
                Vertices = Util.ToArray(vertices, verticesSize) ?? [],
                Faces = Util.ToArray(faces, facesSize),
                BVH = Util.ToArray(bvh, bvhSize),
                Types = Util.ToArray(types, typesSize) ?? [],
                Unknown1 = unknown1,
                Unknown2 = unknown2,
            };
        }
    }
}
