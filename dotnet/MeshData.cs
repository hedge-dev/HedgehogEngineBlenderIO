﻿using HEIO.NET.VertexUtils;
using SharpNeedle.Framework.HedgehogEngine.Mirage;
using SharpNeedle.Framework.HedgehogEngine.Needle.Archive;
using SharpNeedle.IO;
using SharpNeedle.Resource;
using SharpNeedle.Structs;
using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Numerics;

namespace HEIO.NET
{
    public struct Vertex
    {
        public int SetIndex { get; set; }

        public Vector3 Position { get; set; }


        public Vertex(Vector3 position)
        {
            Position = position;
        }

        public static EqualityComparer<Vertex> GetMergeComparer()
        {
            const float mergeDistance = 0.001f * 0.001f;

            return EqualityComparer<Vertex>.Create((v1, v2) =>
                v1.SetIndex == v2.SetIndex
                && Vector3.DistanceSquared(v1.Position, v2.Position) <= mergeDistance);
        }

    }

    public enum VertexMergeMode
    {
        None,
        SubMesh,
        All
    }

    public class MeshData
    {
        public string Name { get; set; }

        public Vertex[] Vertices { get; set; }


        public int[] TriangleIndices { get; set; }

        public Vector3[] Normals { get; set; }

        public Vector3[] Tangents { get; set; }

        public Vector2[][] TextureCoordinates { get; set; }

        public Vector4Int[][]? ByteColors { get; set; }

        public Vector4[][]? FloatColors { get; set; }


        public ResourceReference<Material>[] Materials { get; set; }

        public int[] MaterialTriangleLengths { get; set; }


        public MeshData(string name, Vertex[] vertices, int[] triangleIndices, Vector3[] normals, Vector3[] tangents, Vector2[][] textureCoordinates, Vector4Int[][]? byteColors, Vector4[][]? floatColors, ResourceReference<Material>[] materials, int[] materialTriangleLengths)
        {
            Name = name;
            Vertices = vertices;
            TriangleIndices = triangleIndices;
            Normals = normals;
            Tangents = tangents;
            TextureCoordinates = textureCoordinates;
            ByteColors = byteColors;
            FloatColors = floatColors;
            Materials = materials;
            MaterialTriangleLengths = materialTriangleLengths;
        }


        public static MeshData FromHEModel(ModelBase model, VertexMergeMode vertexMergeMode)
        {
            GPUModel gpuModel = GPUModel.ReadModelData(model);

            Vertex[] vertices = new Vertex[gpuModel.Vertices.Length];

            int setIndex = 0;
            int setVertexIndex = 0;
            int setSize = gpuModel.VertexSetSizes[0];

            for(int i = 0; i < vertices.Length; i++)
            {
                vertices[i] = new Vertex(gpuModel.Vertices[i].Position)
                {
                    SetIndex = setIndex
                };

                if(vertexMergeMode == VertexMergeMode.SubMesh)
                {
                    setVertexIndex++;

                    if(setVertexIndex > setSize)
                    {
                        setIndex++;
                        setVertexIndex = 0;
                        setSize = gpuModel.VertexSetSizes[setIndex];
                    }
                }
            }

            DistinctMap<Vertex> vertexMap = vertexMergeMode == VertexMergeMode.None
                ? new(vertices, null)
                : DistinctMap.CreateDistinctMap(vertices, Vertex.GetMergeComparer());

            int loopCount = gpuModel.Triangles.Length;

            int[] triangleIndices = new int[loopCount];
            Vector3[] normals = new Vector3[loopCount];
            Vector3[] tangents = new Vector3[loopCount];

            Vector2[][] textureCoordinates = new Vector2[gpuModel.TexcoordSets][];
            for(int i = 0; i < gpuModel.TexcoordSets; i++)
            {
                textureCoordinates[i] = new Vector2[loopCount];
            }

            Vector4Int[][]? byteColors = null;
            Vector4[][]? floatColors = null;

            if(gpuModel.UseByteColors)
            {
                byteColors = new Vector4Int[gpuModel.ColorSets][];
                for(int i = 0; i < gpuModel.ColorSets; i++)
                {
                    byteColors[i] = new Vector4Int[loopCount];
                }
            }
            else
            {
                floatColors = new Vector4[gpuModel.ColorSets][];
                for(int i = 0; i < gpuModel.ColorSets; i++)
                {
                    floatColors[i] = new Vector4[loopCount];
                }
            }


            for(int i = 0; i < loopCount; i++)
            {
                int vertexIndex = gpuModel.Triangles[i];
                GPUVertex gpuVertex = gpuModel.Vertices[vertexIndex];

                triangleIndices[i] = vertexMap[vertexIndex];
                normals[i] = gpuVertex.Normal;
                tangents[i] = gpuVertex.Tangent;

                for(int j = 0; j < gpuModel.TexcoordSets; j++)
                {
                    textureCoordinates[j][i] = new(gpuVertex.TextureCoordinates[j].X, 1 - gpuVertex.TextureCoordinates[j].Y);
                }

                if(gpuModel.UseByteColors)
                {
                    for(int j = 0; j < gpuModel.ColorSets; j++)
                    {
                        byteColors![j][i] = gpuVertex.ByteColors![j];
                    }
                }
                else
                {
                    for(int j = 0; j < gpuModel.ColorSets; j++)
                    {
                        floatColors![j][i] = gpuVertex.FloatColors![j];
                    }
                }
            }


            return new(
                model.Name,
                vertexMap.ValueArray,
                triangleIndices,
                normals,
                tangents,
                textureCoordinates,
                byteColors,
                floatColors,
                gpuModel.SetMaterials,
                gpuModel.TriangleSetSizes);
        }

    }
}
