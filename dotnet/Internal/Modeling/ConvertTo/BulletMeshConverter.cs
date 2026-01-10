using SharpNeedle.Framework.HedgehogEngine.Bullet;
using System;
using System.Collections.Generic;
using System.Numerics;

namespace HEIO.NET.Internal.Modeling.ConvertTo
{
    internal static class BulletMeshConverter
    {
        public static BulletMesh ConvertToBulletMesh(CollisionMeshData[] meshData, BulletPrimitive[] primitives)
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
                            uint vertexIndex = mesh.TriangleIndices[j + (i + polygonOffset) * 3];
                            int newVertexIndex = vertexIndexMap[vertexIndex];

                            if(newVertexIndex == -1)
                            {
                                newVertexIndex = vertices.Count;
                                vertices.Add(mesh.Vertices[(int)vertexIndex]);
                                vertexIndexMap[vertexIndex] = newVertexIndex;
                            }

                            triangleIndices[j + i * 3] = newVertexIndex;
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

                        shape.Types = [flags & 0xFFFFFF | layer.ConvexType << 24];
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
