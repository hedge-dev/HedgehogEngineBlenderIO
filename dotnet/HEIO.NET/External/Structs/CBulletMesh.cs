using SharpNeedle.Framework.HedgehogEngine.Bullet;

namespace HEIO.NET.External.Structs
{
    public unsafe struct CBulletMesh : IConvertInternal<BulletMesh>
    {
        public char* name;
        public int bulletMeshVersion;

        public CBulletShape* shapes;
        public nint shapesSize;

        public CBulletPrimitive* primitives;
        public nint primitivesSize;

        public static CBulletMesh FromInternal(BulletMesh mesh)
        {
            return new()
            {
                name = mesh.Name.ToPointer(),
                bulletMeshVersion = mesh.BulletMeshVersion,

                shapes = Allocate.AllocFromArray(mesh.Shapes, CBulletShape.FromInternal),
                shapesSize = mesh.Shapes.Length,

                primitives = CBulletPrimitive.FromInternalArray(mesh.Primitives),
                primitivesSize = mesh.Primitives.Length
            };
        }

        public static CBulletMesh* PointerFromInternal(BulletMesh mesh)
        {
            CBulletMesh* result = Allocate.Alloc<CBulletMesh>();
            *result = FromInternal(mesh);
            return result;
        }

        public readonly BulletMesh ToInternal()
        {
            return new()
            {
                Name = Util.FromPointer(name)!,
                BulletMeshVersion = bulletMeshVersion,
                Shapes = Util.ToArray<CBulletShape, BulletShape>(shapes, shapesSize)!,
                Primitives = CBulletPrimitive.ToInternalArray(primitives, primitivesSize)
            };
        }

    }
}
