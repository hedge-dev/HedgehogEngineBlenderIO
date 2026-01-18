using SharpNeedle.Framework.HedgehogEngine.Bullet;
using SharpNeedle.IO;
using System.Collections.Generic;
using System.Linq;
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

        public static CollisionMeshData[] ReadFiles(IFile[] files, MeshImportSettings settings)
        {
            CollisionMeshData[] result = new CollisionMeshData[files.Length];

            for (int i = 0; i < files.Length; i++)
            {
                BulletMesh mesh = new();
                mesh.Read(files[i]);

                result[i] = FromBulletMesh(mesh, settings);
            }

            return result;
        }

        public static CollisionMeshData[] ReadFiles(string[] filepaths, MeshImportSettings settings)
        {
            return ReadFiles(
                filepaths.Select(x => FileSystem.Instance.Open(x)!).ToArray(),
                settings
            );
        }

        public static CollisionMeshData FromBulletMesh(BulletMesh mesh, MeshImportSettings settings)
        {
            return ConvertFrom.BulletMeshConverter.ConvertToCollisionMeshData(mesh, settings);
        }

        public static BulletMesh ToBulletMesh(CollisionMeshData[] meshData)
        {
            return ConvertTo.BulletMeshConverter.ConvertToBulletMesh(meshData);
        }
    }
}
