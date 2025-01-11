using HEIO.NET.VertexUtils;
using SharpNeedle.Framework.HedgehogEngine.Bullet;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Numerics;

namespace HEIO.NET
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

        public CollisionMeshData(IList<Vector3> vertices, IList<uint> triangleIndices, IList<uint> types, IList<uint> flags, IList<CollisionMeshDataGroup> layers)
        {
            Vertices = vertices;
            TriangleIndices = triangleIndices;
            Types = types;
            Flags = flags;
            Groups = layers;
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

        public static CollisionMeshData FromBulletMesh(BulletMesh mesh, bool mergeVertices, float vertexMergeDistance, bool removeUnusedVertices)
        {
            CollisionMeshData result = new([], [], [], [], []);

            byte maxType = 0;
            uint mergedFlags = 0;

            foreach(BulletShape shape in mesh.Shapes)
            {
                CollisionMeshDataGroup layer;
                uint vertexOffset = (uint)result.Vertices.Count;

                if(result.Groups.Count == 43)
                {

                }

                if(shape.IsConvex)
                {
                    int[] faces = ConvexHullGenerator.GenerateHull(shape.Vertices);
                    ((List<uint>)result.TriangleIndices).AddRange(faces.Select(x => (uint)x + vertexOffset));

                    byte type = (byte)(shape.Types[0] >> 24);
                    uint flag = (uint)shape.Types[0] & 0xFFFFFF;

                    int triangleCount = faces.Length / 3;

                    layer = new((uint)triangleCount, shape.Layer, true)
                    {
                        ConvexType = type,
                        ConvexFlagValues = GetFlagBits(flag).ToArray()
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
                    for(int i = 0, f = 0; i < shape.Faces.Length; i+= 3, f++)
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

                        ulong attribute = shape.Types[f];
                        byte type = (byte)(attribute >> 24);
                        uint flag = (uint)attribute & 0xFFFFFF;

                        result.Types.Add(type);
                        result.Flags.Add(flag);

                        maxType = byte.Max(maxType, type);
                        mergedFlags |= flag;
                    }
                }

                ((List<Vector3>)result.Vertices).AddRange(shape.Vertices);

                result.Groups.Add(layer);
            }

            if(maxType > 0)
            {
                IEnumerable<int> types;
                IEnumerable<uint> typeValues;

                if(DistinctMap.TryCreateDistinctMap(result.Types!, out DistinctMap<uint> map))
                {
                    typeValues = map.Values;
                    types = map.Map!;
                }
                else
                {
                    typeValues = result.Types!;
                    types = Enumerable.Range(0, result.Types!.Count);
                }

                result.Types = types.Select(x => (uint)x).ToArray();
                result.TypeValues = typeValues.Select(x => (byte)x).ToArray();
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

            if(mergeVertices)
            {
                float mergeDistanceSquared = vertexMergeDistance * vertexMergeDistance;
                EqualityComparer<Vector3> mergeComparer = EqualityComparer<Vector3>.Create((v1, v2) =>
                        Vector3.DistanceSquared(v1, v2) < mergeDistanceSquared);

                if(DistinctMap.TryCreateDistinctMap(result.Vertices, mergeComparer, out DistinctMap<Vector3> map))
                {
                    result.Vertices = map.ValueArray;
                    for(int i = 0; i < result.TriangleIndices.Count; i++)
                    {
                        result.TriangleIndices[i] = map[result.TriangleIndices[i]];
                    }
                }
            }

            if(removeUnusedVertices)
            {
                bool[] useChecks = new bool[result.Vertices.Count];
                for(int i = 0; i < result.TriangleIndices.Count; i++)
                {
                    useChecks[result.TriangleIndices[i]] = true;
                }

                int unused = useChecks.Count(x => !x);
                if(unused > 0)
                {
                    Vector3[] usedVertices = new Vector3[result.Vertices.Count - unused];
                    uint[] map = new uint[result.Vertices.Count];
                    uint targetIndex = 0;

                    for(int i = 0; i < result.Vertices.Count; i++)
                    {
                        if(!useChecks[i])
                        {
                            continue;
                        }

                        usedVertices[targetIndex] = result.Vertices[i];
                        map[i] = targetIndex;
                        targetIndex++;
                    }

                    for(int i = 0; i < result.TriangleIndices.Count; i++)
                    {
                        result.TriangleIndices[i] = map[result.TriangleIndices[i]];
                    }

                    result.Vertices = usedVertices;
                }
            }

            return result;
        }
    
        public static BulletMesh ToBulletMesh(CollisionMeshData[] meshData, BulletPrimitive[] primitives)
        {
            List<BulletShape> resultShapes = [];

            foreach(CollisionMeshData mesh in meshData)
            {
                int polygonOffset = 0;
                int[] vertexIndexMap = new int[mesh.Vertices.Count];

                (uint fromflag, uint toflag)[]? flagmap = null;

                if(mesh.FlagValues != null)
                {
                    flagmap = new (uint fromflag, uint toflag)[mesh.FlagValues.Count];

                    for(int i = 0; i < mesh.FlagValues.Count; i++)
                    {
                        flagmap[i] = (1u << i, 1u << mesh.FlagValues[i]);
                    }
                }

                foreach(CollisionMeshDataGroup layer in mesh.Groups)
                {
                    Array.Fill(vertexIndexMap, -1);
                    List<Vector3> vertices = [];
                    int[] triangleIndices = new int[layer.Size * 3];
                    
                    for(int i = 0; i < layer.Size; i++)
                    {
                        for(int j = 0; j < 3; j++)
                        {
                            uint vertexIndex = mesh.TriangleIndices[j + ((i + polygonOffset) * 3)];
                            int newVertexIndex = vertexIndexMap[vertexIndex];

                            if(newVertexIndex == -1)
                            {
                                newVertexIndex = vertices.Count;
                                vertices.Add(mesh.Vertices[(int)vertexIndex]);
                                vertexIndexMap[vertexIndex] = newVertexIndex;
                            }

                            triangleIndices[j + (i * 3)] = newVertexIndex;
                        }
                    }

                    BulletShape shape = new()
                    {
                        Vertices = [.. vertices],
                        Layer = layer.Layer
                    };

                    if(layer.IsConvex)
                    {
                        shape.IsConvex = true;

                        uint flags = 0;

                        if(layer.ConvexFlagValues != null)
                        {
                            foreach(byte flag in layer.ConvexFlagValues)
                            {
                                flags |= 1u << flag;
                            }
                        }

                        shape.Types = [(flags & 0xFFFFFF) | (layer.ConvexType << 24)];
                    }
                    else
                    {
                        shape.Faces = (uint[])(object)triangleIndices;
                        shape.Types = new ulong[layer.Size];

                        if(flagmap != null)
                        {
                            for(int i = 0; i < layer.Size; i++)
                            {
                                uint internalFlags = mesh.Flags[polygonOffset + i];
                                uint flags = 0;

                                foreach((uint fromFlag, uint toFlag) in flagmap)
                                {
                                    if((internalFlags & fromFlag) != 0)
                                    {
                                        flags |= toFlag;
                                    }
                                }

                                shape.Types[i] = flags;
                            }
                        }
                        
                        if(mesh.TypeValues != null)
                        {
                            for(int i = 0; i < layer.Size; i++)
                            {
                                uint internalType = mesh.Types[polygonOffset + i];
                                shape.Types[i] |= (uint)(mesh.TypeValues[(int)internalType] << 24);
                            }
                        }

                        shape.GenerateBVH();
                    }


                    resultShapes.Add(shape);
                    polygonOffset += (int)layer.Size;
                }
            }

            return new()
            {
                Shapes = [.. resultShapes],
                Primitives = primitives
            };
        }
    }
}
