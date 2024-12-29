using HEIO.NET.VertexUtils;
using SharpNeedle.Framework.HedgehogEngine.Mirage.Bullet;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Numerics;

namespace HEIO.NET
{
    public class CollisionMeshDataLayer
    {
        public uint Size { get; set; }

        public uint Value { get; set; }

        public bool IsConvex { get; set; }

        public uint Type { get; set; }

        public IList<byte>? FlagValues { get; set; }

        public CollisionMeshDataLayer(uint size, uint value, bool isConvex)
        {
            Size = size;
            Value = value;
            IsConvex = isConvex;
            Type = 0;
            FlagValues = isConvex ? [] : null;
        }
    }

    public class CollisionMeshData
    {
        public IList<Vector3> Vertices { get; set; }

        public IList<uint> TriangleIndices { get; set; }

        public IList<byte> Types { get; set; }

        public IList<byte>? TypeValues { get; set; }

        public IList<uint> Flags { get; set; }

        public IList<byte>? FlagValues { get; set; }

        public IList<CollisionMeshDataLayer> Layers { get; set; }

        public CollisionMeshData(IList<Vector3> vertices, IList<uint> triangleIndices, IList<byte> types, IList<uint> flags, IList<CollisionMeshDataLayer> layers)
        {
            Vertices = vertices;
            TriangleIndices = triangleIndices;
            Types = types;
            Flags = flags;
            Layers = layers;
        }

        private static IEnumerable<byte> GetFlagBits(uint flag)
        {
            for(byte i = 0; i < 31; i++, flag >>= 1)
            {
                if((flag & 1) != 0)
                {
                    yield return i;
                }
            }
        }


        public static CollisionMeshData FromBulletMesh(BulletMesh mesh)
        {
            CollisionMeshData result = new([], [], [], [], []);

            byte maxType = 0;
            uint mergedFlags = 0;

            foreach(BulletShape shape in mesh.Shapes)
            {
                CollisionMeshDataLayer layer;
                uint vertexOffset = (uint)result.Vertices.Count;

                if(shape.IsConvex)
                {
                    int[] faces = ConvexHullGenerator.GenerateHull(shape.Vertices);
                    ((List<uint>)result.TriangleIndices).AddRange(faces.Select(x => (uint)x + vertexOffset));

                    byte type = (byte)(shape.Types[0] >> 24);
                    uint flag = shape.Types[0] & 0xFFFFFF;

                    int triangleCount = faces.Length / 3;

                    layer = new((uint)triangleCount, shape.Layer, true)
                    {
                        Type = type,
                        FlagValues = GetFlagBits(flag).ToArray()
                    };

                    for(int i = 0; i < triangleCount; i++)
                    {
                        result.Types.Add(type);
                        result.Flags.Add(flag);
                    }

                    maxType = byte.Max(maxType, type);
                    mergedFlags |= flag;
                }
                else
                {
                    layer = new((uint)(shape.Faces!.Length / 3), shape.Layer, shape.IsConvex);

                    SortedSet<CompTri> usedTriangles = [];

                    for(int i = 0; i < shape.Faces.Length; i+= 3)
                    {
                        uint t1 = shape.Faces[i];
                        uint t2 = shape.Faces[i + 1];
                        uint t3 = shape.Faces[i + 2];

                        if(t1 == t2 || t2 == t3 || t3 == t1 || !usedTriangles.Add(new(t1, t2, t3)))
                        {
                            layer.Size--;
                            continue;
                        }

                        result.TriangleIndices.Add(t1 + vertexOffset);
                        result.TriangleIndices.Add(t2 + vertexOffset);
                        result.TriangleIndices.Add(t3 + vertexOffset);

                        byte type = (byte)(shape.Types[0] >> 24);
                        uint flag = shape.Types[0] & 0xFFFFFF;

                        result.Types.Add(type);
                        result.Flags.Add(flag);

                        maxType = byte.Max(maxType, type);
                        mergedFlags |= flag;
                    }
                }

                ((List<Vector3>)result.Vertices).AddRange(shape.Vertices);

                result.Layers.Add(layer);
            }

            if(maxType > 0)
            {
                IEnumerable<int> types;

                if(DistinctMap.TryCreateDistinctMap(result.Types!, out DistinctMap<byte> map))
                {
                    result.TypeValues = map.Values;
                    types = map.Map!;
                }
                else
                {
                    result.TypeValues = result.Types!;
                    types = Enumerable.Range(0, result.Types!.Count);
                }

                result.Types = types.Select(x => (byte)x).ToArray();
            }

            if(mergedFlags != 0)
            {
                result.FlagValues = GetFlagBits(mergedFlags).ToArray();
                List<(uint retainMask, uint shiftMask, int shiftCount)> shifts = [];

                int prev = -1;
                uint invRetainMask = uint.MaxValue;

                foreach(byte value in result.FlagValues)
                {
                    int diff = value - prev;
                    if(diff > 1)
                    {
                        uint retainMask = ~invRetainMask;
                        uint shiftMask = invRetainMask << (diff - 1);
                        shifts.Add((retainMask, shiftMask, diff - 1));
                    }

                    invRetainMask <<= 1;
                    prev = value;
                }

                for(int i = 0; i < result.Flags!.Count; i++)
                {
                    uint flag = result.Flags[i];

                    foreach((uint retainMask, uint shiftMask, int shiftCount) in shifts)
                    {
                        flag = (flag & retainMask) | ((flag & shiftMask) >> shiftCount);
                    }

                    result.Flags[i] = flag;
                }
            }

            return result;
        }
    }
}
