using BulletSharp;
using HEIO.NET.Internal.Modeling;
using SharpNeedle.Framework.HedgehogEngine.Bullet;
using SharpNeedle.Resource;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Numerics;
using System.Runtime.InteropServices;
using static BulletSharp.DiscreteCollisionDetectorInterface;

namespace HEIO.NET
{
    public unsafe struct CCollisionMeshDataGroup
    {
        public uint size;
        public uint layer;
        public bool isConvex;
        public uint convexType;
        public byte* convexFlagValues;
        public nint convexFlagValuesSize;
    }

    public unsafe struct CBulletPrimitive
    {
        public byte shapeType;
        public byte surfaceLayer;
        public byte surfaceType;
        public uint surfaceFlags;
        public Vector3 position;
        public Quaternion rotation;
        public Vector3 dimensions;

        public static CBulletPrimitive* FromBulletPrimitiveArray(IList<BulletPrimitive> primitives)
        {
            CBulletPrimitive* result = Allocate.Alloc<CBulletPrimitive>(primitives.Count);

            for (int i = 0; i < primitives.Count; i++)
            {
                BulletPrimitive primitive = primitives[i];
                CBulletPrimitive* resultPrimitive = &result[i];

                resultPrimitive->shapeType = (byte)primitive.ShapeType;
                resultPrimitive->surfaceLayer = primitive.SurfaceLayer;
                resultPrimitive->surfaceType = primitive.SurfaceType;
                resultPrimitive->surfaceFlags = primitive.SurfaceFlags;
                resultPrimitive->position = primitive.Position;
                resultPrimitive->rotation = primitive.Rotation;
                resultPrimitive->dimensions = primitive.Dimensions;
            }

            return result;
        }

        public static BulletPrimitive[] ToBulletPrimitiveArray(CBulletPrimitive* primitives, nint size)
        {
            BulletPrimitive[] result = new BulletPrimitive[size];

            for (int i = 0; i < size; i++)
            {
                CBulletPrimitive* primitive = &primitives[i];

                result[i] = new()
                {
                    ShapeType = (BulletPrimiteShapeType)primitive->shapeType,
                    SurfaceLayer = primitive->surfaceLayer,
                    SurfaceType = primitive->surfaceType,
                    SurfaceFlags = primitive->surfaceFlags,
                    Position = primitive->position,
                    Rotation = primitive->rotation,
                    Dimensions = primitive->dimensions
                };
            }

            return result;
        }
    }

    public unsafe struct CCollisionMeshData
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

        public static CCollisionMeshData* FromCollisionMeshData(CollisionMeshData meshData)
        {
            CCollisionMeshData* result = Allocate.Alloc<CCollisionMeshData>();

            result->name = meshData.Name.ToPointer();

            result->vertices = Allocate.AllocFromArray(meshData.Vertices);
            result->verticesSize = meshData.Vertices.Count;

            result->triangleIndices = Allocate.AllocFromArray(meshData.TriangleIndices);
            result->triangleIndicesSize = meshData.TriangleIndices.Count;

            result->types = Allocate.AllocFromArray(meshData.Types);
            result->typesSize = meshData.Types.Count;

            result->typeValues = Allocate.AllocFromArray(meshData.TypeValues);
            result->typeValuesSize = meshData.TypeValues?.Count ?? 0;

            result->flags = Allocate.AllocFromArray(meshData.Flags);
            result->flagsSize = meshData.Flags.Count;

            result->flagValues = Allocate.AllocFromArray(meshData.FlagValues);
            result->flagValuesSize = meshData.FlagValues?.Count ?? 0;

            result->groupsSize = meshData.Groups.Count;
            result->groups = Allocate.Alloc<CCollisionMeshDataGroup>(result->groupsSize);

            for (int i = 0; i < result->groupsSize; i++)
            {
                CollisionMeshDataGroup group = meshData.Groups[i];
                CCollisionMeshDataGroup* resultGroup = &result->groups[i];

                resultGroup->size = group.Size;
                resultGroup->layer = group.Layer;
                resultGroup->isConvex = group.IsConvex;
                resultGroup->convexType = group.ConvexType;

                resultGroup->convexFlagValues = Allocate.AllocFromArray(group.ConvexFlagValues);
                resultGroup->convexFlagValuesSize = group.ConvexFlagValues?.Count ?? 0;
            }

            result->primitivesSize = meshData.Primitives.Count;
            result->primitives = CBulletPrimitive.FromBulletPrimitiveArray(meshData.Primitives);

            return result;
        }

        public CollisionMeshData ToCollisionMeshData()
        {
            CollisionMeshDataGroup[] resultGroups = new CollisionMeshDataGroup[groupsSize];
            for (int i = 0; i < groupsSize; i++)
            {
                CCollisionMeshDataGroup* group = &groups[i];
                CollisionMeshDataGroup resultGroup = new(
                    group->size,
                    group->layer,
                    group->isConvex
                ) {
                    ConvexType = group->convexType,
                    ConvexFlagValues = Util.ToArray(group->convexFlagValues, group->convexFlagValuesSize)
                };

                resultGroups[i] = resultGroup;
            }

            return new CollisionMeshData(
                Util.FromPointer(name)!,
                Util.ToArray(vertices, verticesSize)!,
                Util.ToArray(triangleIndices, triangleIndicesSize)!,
                Util.ToArray(types, typesSize)!,
                Util.ToArray(typeValues, typeValuesSize),
                Util.ToArray(flags, flagsSize)!,
                Util.ToArray(flagValues, flagValuesSize),
                resultGroups,
                CBulletPrimitive.ToBulletPrimitiveArray(primitives, primitivesSize)
            );
        }

    }

    public unsafe struct CBulletShape
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
    }

    public unsafe struct CBulletMesh
    {
        public char* name;
        public int bulletMeshVersion;
        
        public CBulletShape* shapes;
        public nint shapesSize;
        
        public CBulletPrimitive* primitives;
        public nint primitivesSize;

        public static CBulletMesh* FromBulletMesh(BulletMesh mesh)
        {
            CBulletMesh* result = Allocate.Alloc<CBulletMesh>();

            result->name = mesh.Name.ToPointer();
            result->bulletMeshVersion = mesh.BulletMeshVersion;

            result->shapesSize = mesh.Shapes.Length;
            result->shapes = Allocate.Alloc<CBulletShape>(mesh.Shapes.Length);

            for(int i = 0; i < result->shapesSize; i++)
            {
                CBulletShape* resultShape = &result->shapes[i];
                BulletShape shape = mesh.Shapes[i];

                resultShape->flags = (byte)shape.Flags;
                resultShape->layer = shape.Layer;

                resultShape->vertices = Allocate.AllocFromArray(shape.Vertices);
                resultShape->verticesSize = shape.Vertices.Length;

                resultShape->faces = Allocate.AllocFromArray(shape.Faces);
                resultShape->facesSize = shape.Faces?.Length ?? 0;

                resultShape->bvh = Allocate.AllocFromArray(shape.BVH);
                resultShape->bvhSize = shape.BVH?.Length ?? 0;

                resultShape->types = Allocate.AllocFromArray(shape.Types);
                resultShape->typesSize = shape.Types.Length;

                resultShape->unknown1 = shape.Unknown1;
                resultShape->unknown2 = shape.Unknown2;
            }

            result->primitivesSize = mesh.Primitives.Length;
            result->primitives = CBulletPrimitive.FromBulletPrimitiveArray(mesh.Primitives);

            return result;
        }

        public BulletMesh ToBulletMesh()
        {
            BulletMesh result = new()
            {
                Name = Util.FromPointer(name)!,
                BulletMeshVersion = bulletMeshVersion,
                Shapes = new BulletShape[shapesSize],
                Primitives = CBulletPrimitive.ToBulletPrimitiveArray(primitives, primitivesSize)
            };

            for(int i = 0; i < result.Shapes.Length; i++)
            {
                CBulletShape* shape = &shapes[i];

                result.Shapes[i] = new()
                {
                    IsConvex =( (BulletShapeFlags)shape->flags).HasFlag(BulletShapeFlags.IsConvexShape),
                    Layer = shape->layer,
                    Vertices = Util.ToArray(shape->vertices, shape->verticesSize)!,
                    Faces = Util.ToArray(shape->faces, shape->facesSize),
                    BVH = Util.ToArray(shape->bvh, shape->bvhSize),
                    Types = Util.ToArray(shape->types, shape->typesSize)!,
                    Unknown1 = shape->unknown1,
                    Unknown2 = shape->unknown2,
                };
            }

            return result;
        }


        [UnmanagedCallersOnly(EntryPoint = "bullet_mesh_read_files")]
        public static CArray ReadFiles(char** filepaths, nint filepathsSize, CMeshImportSettings* settings)
        {
            try
            {
                string[] filepathsArray = Util.ToStringArray(filepaths, filepathsSize);
                MeshImportSettings internalSettings = settings->ToMeshImportSettings();

                CollisionMeshData[] meshData = CollisionMeshData.ReadFiles(filepathsArray, internalSettings);

                nint[] results = [.. meshData.Select(x => (nint)CCollisionMeshData.FromCollisionMeshData(x))];
                CCollisionMeshData** result = (CCollisionMeshData**)Allocate.AllocFromArray(results);

                return new(
                    result,
                    results.Length
                );
            }
            catch (Exception exception)
            {
                ErrorHandler.HandleError(exception);
                return default;
            }
        }

        [UnmanagedCallersOnly(EntryPoint = "bullet_mesh_compile_mesh_data")]
        public static CBulletMesh* CompileMeshData(CCollisionMeshData** collisionMeshData, nint collisionMeshDataSize)
        {
            try
            {
                CollisionMeshData[] internalMeshData = new CollisionMeshData[collisionMeshDataSize];
                for (int i = 0; i < collisionMeshDataSize; i++)
                {
                    internalMeshData[i] = collisionMeshData[i]->ToCollisionMeshData();
                }

                BulletMesh bulletMesh = CollisionMeshData.CompileBulletMesh(internalMeshData);
                return FromBulletMesh(bulletMesh);
            }
            catch (Exception exception)
            {
                ErrorHandler.HandleError(exception);
                return null;
            }
        }

        [UnmanagedCallersOnly(EntryPoint = "bullet_mesh_write_to_file")]
        public static void WriteToFile(CBulletMesh* bulletMesh, char* filepath)
        {
            try
            {
                bulletMesh->ToBulletMesh().Write(Util.FromPointer(filepath)!, false);
            }
            catch (Exception exception)
            {
                ErrorHandler.HandleError(exception);
                return;
            }
        }
    }
}
