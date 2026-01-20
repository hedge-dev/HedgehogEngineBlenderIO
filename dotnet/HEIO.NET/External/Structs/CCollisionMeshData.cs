using HEIO.NET.Internal.Modeling;
using System.Numerics;

namespace HEIO.NET.External.Structs
{
    public unsafe struct CCollisionMeshData : IConvertInternal<CollisionMeshData>
    {
        public char* name;

        public Vector3* vertices;
        public nint verticesSize;

        public uint* triangleIndices;
        public nint triangleIndicesSize;

        public uint* types;
        public nint typesSize;

        public byte* typeValues;
        public nint typeValuesSize;

        public uint* flags;
        public nint flagsSize;

        public byte* flagValues;
        public nint flagValuesSize;

        public CCollisionMeshDataGroup* groups;
        public nint groupsSize;

        public CBulletPrimitive* primitives;
        public nint primitivesSize;

        public static CCollisionMeshData FromInternal(CollisionMeshData meshData)
        {
            return new()
            {
                name = meshData.Name.AllocString(),

                vertices = Allocate.AllocFromArray(meshData.Vertices),
                verticesSize = meshData.Vertices.Count,

                triangleIndices = Allocate.AllocFromArray(meshData.TriangleIndices),
                triangleIndicesSize = meshData.TriangleIndices.Count,

                types = Allocate.AllocFromArray(meshData.Types),
                typesSize = meshData.Types.Count,

                typeValues = Allocate.AllocFromArray(meshData.TypeValues),
                typeValuesSize = meshData.TypeValues?.Count ?? 0,

                flags = Allocate.AllocFromArray(meshData.Flags),
                flagsSize = meshData.Flags.Count,

                flagValues = Allocate.AllocFromArray(meshData.FlagValues),
                flagValuesSize = meshData.FlagValues?.Count ?? 0,

                groups = Allocate.AllocFromArray(meshData.Groups, CCollisionMeshDataGroup.FromInternal),
                groupsSize = meshData.Groups.Count,

                primitives = CBulletPrimitive.FromInternalArray(meshData.Primitives),
                primitivesSize = meshData.Primitives.Count,
            };
        }

        public CollisionMeshData ToInternal()
        {
            return new CollisionMeshData(
                Util.ToString(name)!,
                Util.ToArray(vertices, verticesSize)!,
                Util.ToArray(triangleIndices, triangleIndicesSize)!,
                Util.ToArray(types, typesSize)!,
                Util.ToArray(typeValues, typeValuesSize),
                Util.ToArray(flags, flagsSize)!,
                Util.ToArray(flagValues, flagValuesSize),
                Util.ToArray<CCollisionMeshDataGroup, CollisionMeshDataGroup>(groups, groupsSize)!,
                CBulletPrimitive.ToInternalArray(primitives, primitivesSize)
            );
        }

    }
}
