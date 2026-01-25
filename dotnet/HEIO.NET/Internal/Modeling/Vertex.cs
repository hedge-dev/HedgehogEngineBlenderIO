using System.Collections.Generic;
using System.Linq;
using System.Numerics;

namespace HEIO.NET.Internal.Modeling
{
    public struct Vertex
    {
        public Vector3 Position { get; set; }

        public Vector3[]? MorphPositions { get; set; }

        public Vector3 Normal { get; set; }

        public UVDirection UVDirection { get; set; }

        public UVDirection UVDirection2 { get; set; }

        public VertexWeight[] Weights { get; set; }

        public Vertex(Vector3 position, int morphCount, Vector3 normal, UVDirection uvDirection, UVDirection uvDirection2, VertexWeight[] weights)
        {
            Position = position;
            MorphPositions = morphCount == 0 ? null : new Vector3[morphCount];
            Normal = normal;
            UVDirection = uvDirection;
            UVDirection2 = uvDirection2;
            Weights = weights;
        }

        public Vertex(Vector3 position, Vector3[]? morphPositions, Vector3 normal, UVDirection uvDirection, UVDirection uvDirection2, VertexWeight[] weights)
        {
            Position = position;
            MorphPositions = morphPositions;
            Normal = normal;
            UVDirection = uvDirection;
            UVDirection2 = uvDirection2;
            Weights = [.. weights.Where(x => x.Weight != 0).OrderBy(x => x.Index)];
        }

        public static EqualityComparer<Vertex> GetMergeComparer(float mergeDistance, bool compareNormals, bool compareMorphs)
        {
            float mergeDistanceSquared = mergeDistance * mergeDistance;

            if(compareMorphs)
            {
                if(compareNormals)
                {
                    return EqualityComparer<Vertex>.Create((v1, v2) =>
                        Vector3.DistanceSquared(v1.Position, v2.Position) < mergeDistanceSquared
                        && VectorUtils.CompareArrayDistances(v1.MorphPositions!, v2.MorphPositions!, mergeDistanceSquared)
                        && VertexWeight.CompareEquality(v1.Weights, v2.Weights)
                        && UVDirection.AreNormalsEqual(v1.Normal, v2.Normal));
                }
                else
                {
                    return EqualityComparer<Vertex>.Create((v1, v2) =>
                        Vector3.DistanceSquared(v1.Position, v2.Position) < mergeDistanceSquared
                        && VectorUtils.CompareArrayDistances(v1.MorphPositions!, v2.MorphPositions!, mergeDistanceSquared)
                        && VertexWeight.CompareEquality(v1.Weights, v2.Weights));
                }
            }
            else
            {
                if(compareNormals)
                {
                    return EqualityComparer<Vertex>.Create((v1, v2) =>
                        Vector3.DistanceSquared(v1.Position, v2.Position) < mergeDistanceSquared
                        && VertexWeight.CompareEquality(v1.Weights, v2.Weights)
                        && UVDirection.AreNormalsEqual(v1.Normal, v2.Normal));
                }
                else
                {
                    return EqualityComparer<Vertex>.Create((v1, v2) =>
                        Vector3.DistanceSquared(v1.Position, v2.Position) < mergeDistanceSquared
                        && VertexWeight.CompareEquality(v1.Weights, v2.Weights));
                }
            }

        }

    }
}
