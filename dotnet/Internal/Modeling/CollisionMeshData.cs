using SharpNeedle.Framework.HedgehogEngine.Bullet;
using SharpNeedle.IO;
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
        public string Name { get; set; }

        public IList<Vector3> Vertices { get; set; }

        public IList<uint> TriangleIndices { get; set; }

        public IList<uint> Types { get; set; }

        public IList<byte>? TypeValues { get; set; }

        public IList<uint> Flags { get; set; }

        public IList<byte>? FlagValues { get; set; }

        public IList<CollisionMeshDataGroup> Groups { get; set; }

        public IList<BulletPrimitive> Primitives { get; set; }


        public CollisionMeshData(string name)
        {
            Name = name;
            Vertices = [];
            TriangleIndices = [];
            Types = [];
            Flags = [];
            Groups = [];
            Primitives = [];
        }

        public CollisionMeshData(string name, Vector3[] vertices, uint[] triangleIndices, uint[] types, byte[]? typeValues, uint[] flags, byte[]? flagValues, CollisionMeshDataGroup[] layers, BulletPrimitive[] primitives)
        {
            Name = name;
            Vertices = vertices;
            TriangleIndices = triangleIndices;
            Types = types;
            TypeValues = typeValues;
            Flags = flags;
            FlagValues = flagValues;
            Groups = layers;
            Primitives = primitives;
        }

        public static CollisionMeshData[] ReadFiles(string[] filepaths, bool mergeVertices, float vertexMergeDistance, bool removeUnusedVertices)
        {
            CollisionMeshData[] result = new CollisionMeshData[filepaths.Length];

            for (int i = 0; i < filepaths.Length; i++)
            {
                BulletMesh mesh = new();
                IFile file = FileSystem.Instance.Open(filepaths[i])!;
                mesh.Read(file);

                result[i] = FromBulletMesh(mesh, mergeVertices, vertexMergeDistance, removeUnusedVertices);
            }

            return result;
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
