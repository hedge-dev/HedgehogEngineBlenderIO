using HEIO.NET.Internal.Modeling;
using SharpNeedle.Resource;
using SharpNeedle.Framework.HedgehogEngine.Bullet;
using System;
using System.Linq;
using System.Numerics;
using System.Runtime.InteropServices;
using BulletSharp;

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

    public struct CBulletPrimitive
    {
        public byte shapeType;
        public byte surfaceLayer;
        public byte surfaceType;
        public uint surfaceFlags;
        public Vector3 position;
        public Quaternion rotation;
        public Vector3 dimensions;

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
            result->primitives = Allocate.Alloc<CBulletPrimitive>(result->primitivesSize);

            for (int i = 0; i < result->primitivesSize; i++)
            {
                BulletPrimitive primitive = meshData.Primitives[i];
                CBulletPrimitive* resultPrimitive = &result->primitives[i];

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

            BulletPrimitive[] resultPrimitives = new BulletPrimitive[primitivesSize];
            for (int i = 0; i < primitivesSize; i++)
            {
                CBulletPrimitive* primitive = &primitives[i];

                resultPrimitives[i] = new()
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

            return new CollisionMeshData(
                Util.FromPointer(name)!,
                Util.ToArray(vertices, verticesSize)!,
                Util.ToArray(triangleIndices, triangleIndicesSize)!,
                Util.ToArray(types, typesSize)!,
                Util.ToArray(typeValues, typeValuesSize),
                Util.ToArray(flags, flagsSize)!,
                Util.ToArray(flagValues, flagValuesSize),
                resultGroups,
                resultPrimitives
            );
        }

        [UnmanagedCallersOnly(EntryPoint = "collision_mesh_read_files")]
        public static CArray ReadFiles(char** filepaths, nint filepathsSize, CMeshImportSettings* settings)
        {
            try
            {
                string[] filepathsArray = Util.ToStringArray(filepaths, filepathsSize);
                MeshImportSettings internalSettings = settings->ToMeshImportSettings();

                CollisionMeshData[] meshData = CollisionMeshData.ReadFiles(filepathsArray, internalSettings);

                nint[] results = [.. meshData.Select(x => (nint)FromCollisionMeshData(x))];
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

        [UnmanagedCallersOnly(EntryPoint = "collision_mesh_write_to_file")]
        public static void WriteToFile(CCollisionMeshData** collisionMeshData, nint collisionMeshDataSize, char* name, int bulletMeshVersion, char* filepath)
        {
            try
            {
                Native.Load();
                CollisionMeshData[] internalMeshData = new CollisionMeshData[collisionMeshDataSize];
                for (int i = 0; i < collisionMeshDataSize; i++)
                {
                    internalMeshData[i] = collisionMeshData[i]->ToCollisionMeshData();
                }

                BulletMesh bulletMesh = CollisionMeshData.ToBulletMesh(internalMeshData);
                bulletMesh.Name = Util.FromPointer(name)!;
                bulletMesh.BulletMeshVersion = bulletMeshVersion;

                bulletMesh.Write(Util.FromPointer(filepath)!, false);
            }
            catch (Exception exception)
            {
                ErrorHandler.HandleError(exception);
                return;
            }
        }
    }
}
