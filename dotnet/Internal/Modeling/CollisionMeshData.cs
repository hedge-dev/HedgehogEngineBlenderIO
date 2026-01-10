using HEIO.NET.Internal.Modeling.ConvertFrom;
using HEIO.NET.Internal.Modeling.ConvertTo;
using SharpNeedle.Framework.HedgehogEngine.Bullet;
using System.Collections.Generic;
using System.Numerics;

namespace HEIO.NET.Internal.Modeling
{
    public class CollisionMeshDataGroup
    {
        public uint Size { get; set; }

        public uint Layer { get; set; }

        public bool IsConvex { get; set; }

        public uint ConvexType { get; set; }

        public IList<byte>? ConvexFlagValues { get; set; }

        public CollisionMeshDataGroup(uint size, uint layer, bool isConvex)
        {
            Size = size;
            Layer = layer;
            IsConvex = isConvex;
            ConvexType = 0;
            ConvexFlagValues = isConvex ? [] : null;
        }
    }

    public class CollisionMeshData
    {
        public IList<Vector3> Vertices { get; set; }

        public IList<uint> TriangleIndices { get; set; }

        public IList<uint> Types { get; set; }

        public IList<byte>? TypeValues { get; set; }

        public IList<uint> Flags { get; set; }

        public IList<byte>? FlagValues { get; set; }

        public IList<CollisionMeshDataGroup> Groups { get; set; }


        public CollisionMeshData()
        {
            Vertices = [];
            TriangleIndices = [];
            Types = [];
            Flags = [];
            Groups = [];
        }

        public CollisionMeshData(Vector3[] vertices, uint[] triangleIndices, uint[] types, byte[]? typeValues, uint[] flags, byte[]? flagValues, CollisionMeshDataGroup[] layers)
        {
            Vertices = vertices;
            TriangleIndices = triangleIndices;
            Types = types;
            TypeValues = typeValues;
            Flags = flags;
            FlagValues = flagValues;
            Groups = layers;
        }

        public static CollisionMeshData FromBulletMesh(BulletMesh mesh, bool mergeVertices, float vertexMergeDistance, bool removeUnusedVertices)
        {
            return ConvertFrom.BulletMeshConverter.ConvertToCollisionMeshData(mesh, mergeVertices, vertexMergeDistance, removeUnusedVertices);
        }

        public static BulletMesh ToBulletMesh(CollisionMeshData[] meshData, BulletPrimitive[] primitives)
        {
            return ConvertTo.BulletMeshConverter.ConvertToBulletMesh(meshData, primitives);
        }
    }
}
