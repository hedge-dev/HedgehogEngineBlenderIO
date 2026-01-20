using J113D.Common;
using SharpNeedle.Framework.HedgehogEngine.Bullet;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Numerics;

namespace HEIO.NET.Internal.Modeling.ConvertFrom
{
    internal static class BulletMeshConverter
    {
        public static CollisionMeshData ConvertToCollisionMeshData(BulletMesh mesh, MeshImportSettings settings)
        {
            CollisionMeshData result = new(mesh.Name)
            {
                Primitives = mesh.Primitives
            };

            byte maxType = 0;
            uint mergedFlags = 0;

            foreach(BulletShape shape in mesh.Shapes)
            {
                uint vertexOffset = (uint)result.Vertices.Count;

                result.Groups.Add(shape.IsConvex
                    ? ProcessConvexShape(shape, vertexOffset, result, ref maxType, ref mergedFlags)
                    : ProcessShape(shape, vertexOffset, result, ref maxType, ref mergedFlags)
                );

                ((List<Vector3>)result.Vertices).AddRange(shape.Vertices);
            }

            if(maxType > 0)
            {
                (result.Types, result.TypeValues) = EvaluateTypes(result.Types);
            }

            if(mergedFlags != 0)
            {
                result.FlagValues = EvaluateFlags(mergedFlags, result.Flags);
            }

            if(settings.MergeCollisionVertices)
            {
                MergeVertices(result, settings.CollisionVertexMergeDistance);
            }

            RemoveInvalidTriangles(result);

            if (settings.RemoveUnusedCollisionVertices)
            {
                RemoveUnusedVertices(result);
            }

            return result;
        }

        private static CollisionMeshDataGroup ProcessConvexShape(BulletShape shape, uint vertexOffset, CollisionMeshData output, ref byte maxType, ref uint mergedFlags)
        {
            int[] faces = ConvexHullGenerator.GenerateHull(shape.Vertices);
            ((List<uint>)output.TriangleIndices).AddRange(faces.Select(x => (uint)x + vertexOffset));

            byte type = (byte)(shape.Types[0] >> 24);
            uint flag = (uint)shape.Types[0] & 0xFFFFFF;
            int triangleCount = faces.Length / 3;

            CollisionMeshDataGroup result = new((uint)triangleCount, shape.Layer, true)
            {
                ConvexType = type,
                ConvexFlagValues = GetFlagBits(flag).ToArray()
            };

            for(int i = 0; i < triangleCount; i++)
            {
                output.Types.Add(type);
                output.Flags.Add(flag);
            }

            maxType = byte.Max(maxType, type);
            mergedFlags |= flag;

            return result;
        }

        private static CollisionMeshDataGroup ProcessShape(BulletShape shape, uint vertexOffset, CollisionMeshData output, ref byte maxType, ref uint mergedFlags)
        {
            CollisionMeshDataGroup result = new((uint)(shape.Faces!.Length / 3), shape.Layer, shape.IsConvex);

            SortedSet<CompTri> usedTriangles = [];
            for(int i = 0, f = 0; i < shape.Faces.Length; i += 3, f++)
            {
                uint t1 = shape.Faces[i];
                uint t2 = shape.Faces[i + 1];
                uint t3 = shape.Faces[i + 2];

                if(t1 == t2 || t2 == t3 || t3 == t1 || !usedTriangles.Add(new(t1, t2, t3)))
                {
                    result.Size--;
                    continue;
                }

                output.TriangleIndices.Add(t1 + vertexOffset);
                output.TriangleIndices.Add(t2 + vertexOffset);
                output.TriangleIndices.Add(t3 + vertexOffset);

                ulong attribute = shape.Types[f];
                byte type = (byte)(attribute >> 24);
                uint flag = (uint)attribute & 0xFFFFFF;

                output.Types.Add(type);
                output.Flags.Add(flag);

                maxType = byte.Max(maxType, type);
                mergedFlags |= flag;
            }

            return result;
        }

        private static (uint[] types, byte[] typeValues) EvaluateTypes(IList<uint> types)
        {
            IEnumerable<int> resultTypes;
            IEnumerable<uint> resultTypeValues;

            if(types.TryCreateDistinctMap(out DistinctMap<uint> map))
            {
                resultTypeValues = map.Values;
                resultTypes = map.Map!;
            }
            else
            {
                resultTypeValues = types!;
                resultTypes = Enumerable.Range(0, types!.Count);
            }

            return (
                resultTypes.Select(x => (uint)x).ToArray(),
                resultTypeValues.Select(x => (byte)x).ToArray()
            );
        }

        private static byte[] EvaluateFlags(uint mergedFlags, IList<uint> flags)
        {
            byte[] flagValues = GetFlagBits(mergedFlags).ToArray();
            List<(uint retainMask, uint shiftMask, int shiftCount)> shifts = [];

            int prev = -1;
            uint invRetainMask = uint.MaxValue;

            foreach(byte value in flagValues)
            {
                int diff = value - prev;
                if(diff > 1)
                {
                    uint retainMask = ~invRetainMask;
                    uint shiftMask = invRetainMask << diff - 1;
                    shifts.Add((retainMask, shiftMask, diff - 1));
                }

                invRetainMask <<= 1;
                prev = value;
            }

            for(int i = 0; i < flags!.Count; i++)
            {
                uint flag = flags[i];

                foreach((uint retainMask, uint shiftMask, int shiftCount) in shifts)
                {
                    flag = flag & retainMask | (flag & shiftMask) >> shiftCount;
                }

                flags[i] = flag;
            }

            return flagValues;
        }

        private static void MergeVertices(CollisionMeshData output, float vertexMergeDistance)
        {
            float mergeDistanceSquared = vertexMergeDistance * vertexMergeDistance;
            EqualityComparer<Vector3> mergeComparer = EqualityComparer<Vector3>.Create((v1, v2) =>
                    Vector3.DistanceSquared(v1, v2) < mergeDistanceSquared);

            if(output.Vertices.TryCreateDistinctMap(mergeComparer, out DistinctMap<Vector3> map))
            {
                output.Vertices = map.ValueArray;
                for (int i = 0; i < output.TriangleIndices.Count; i++)
                {
                    output.TriangleIndices[i] = map[output.TriangleIndices[i]];
                }
            }
        }

        private static void RemoveInvalidTriangles(CollisionMeshData output)
        {
            uint[] newTriangleIndices = new uint[output.TriangleIndices.Count];
            uint[] newTypes = new uint[output.Types.Count];
            uint[] newFlags = new uint[output.Flags.Count];
            int newCount = 0;

            int currentGroupIndex = 0;
            int currentGroupSize = 0;
            uint[] newGroupSizes = output.Groups.Select(x => x.Size).ToArray();

            for(int i = 0; i < newTriangleIndices.Length; i += 3, currentGroupSize++)
            {
                if (currentGroupSize >= output.Groups[currentGroupIndex].Size)
                {
                    currentGroupIndex++;
                    currentGroupSize = 0;
                }

                uint t1 = output.TriangleIndices[i];
                uint t2 = output.TriangleIndices[i + 1];
                uint t3 = output.TriangleIndices[i + 2];

                if(t1 != t2 && t2 != t3 && t3 != t1)
                {
                    newTriangleIndices[newCount * 3] = t1;
                    newTriangleIndices[newCount * 3 + 1] = t2;
                    newTriangleIndices[newCount * 3 + 2] = t3;
                    newTypes[newCount] = output.Types[i / 3];
                    newFlags[newCount] = output.Flags[i / 3];

                    newCount++;
                }
                else
                {
                    newGroupSizes[currentGroupIndex]--;
                }
            }

            if (newCount < output.TriangleIndices.Count)
            {
                uint[] outTriangleIndices = new uint[newCount * 3];
                Array.Copy(newTriangleIndices, outTriangleIndices, outTriangleIndices.Length);

                uint[] outTypes = new uint[newCount];
                Array.Copy(newTypes, outTypes, outTypes.Length);

                uint[] outFlags = new uint[newCount];
                Array.Copy(newFlags, outFlags, outFlags.Length);

                output.TriangleIndices = outTriangleIndices;
                output.Types = outTypes;
                output.Flags = outFlags;

                for(int i = 0; i < newGroupSizes.Length; i++)
                {
                    output.Groups[i].Size = newGroupSizes[i];   
                }
            }

        }

        private static void RemoveUnusedVertices(CollisionMeshData output)
        {
            bool[] useChecks = new bool[output.Vertices.Count];
            for(int i = 0; i < output.TriangleIndices.Count; i++)
            {
                useChecks[output.TriangleIndices[i]] = true;
            }

            int unused = useChecks.Count(x => !x);
            if(unused > 0)
            {
                Vector3[] usedVertices = new Vector3[output.Vertices.Count - unused];
                uint[] map = new uint[output.Vertices.Count];
                uint targetIndex = 0;

                for(int i = 0; i < output.Vertices.Count; i++)
                {
                    if(!useChecks[i])
                    {
                        continue;
                    }

                    usedVertices[targetIndex] = output.Vertices[i];
                    map[i] = targetIndex;
                    targetIndex++;
                }

                for(int i = 0; i < output.TriangleIndices.Count; i++)
                {
                    output.TriangleIndices[i] = map[output.TriangleIndices[i]];
                }

                output.Vertices = usedVertices;
            }
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

    }
}
