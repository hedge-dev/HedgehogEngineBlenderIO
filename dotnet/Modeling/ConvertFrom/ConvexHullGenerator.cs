using MIConvexHull;
using System.Collections.Generic;
using System.Linq;
using System.Numerics;

namespace HEIO.NET.Modeling.ConvertFrom
{
    internal static class ConvexHullGenerator
    {
        private readonly struct ConvexVertex : IVertex
        {
            public int Index { get; }

            public double[] Position { get; }

            public ConvexVertex(int index, Vector3 vector)
            {
                Index = index;
                Position = [vector.X, vector.Y, vector.Z];
            }
        }

        private readonly struct ConvexVertex2D : IVertex2D
        {
            public int Index { get; }

            public double X { get; }

            public double Y { get; }

            public ConvexVertex2D(int index, double x, double y)
            {
                Index = index;
                X = x;
                Y = y;
            }

            public override string ToString()
            {
                return $"{X:F3}, {Y:F3}";
            }
        }

        public static int[] GenerateHull(IList<Vector3> vertices)
        {
            ConvexVertex[] convexVertices = new ConvexVertex[vertices.Count];
            for (int i = 0; i < convexVertices.Length; i++)
            {
                convexVertices[i] = new(i, vertices[i]);
            }

            ConvexHullCreationResult<ConvexVertex, DefaultConvexFace<ConvexVertex>> convexResult = ConvexHull.Create(convexVertices);

            if (convexResult.Result != null)
            {
                return convexResult.Result.Faces.SelectMany(x => x.Vertices).Select(x => x.Index).ToArray();
            }
            else
            {
                return GenerateHullFromPlane(vertices);
            }
        }

        private static int[] GenerateHullFromPlane(IList<Vector3> vertices)
        {
            ConvexVertex2D[] convexVertices2D = new ConvexVertex2D[vertices.Count];

            Vector3 position = vertices[0];
            Vector3 tangent = Vector3.Normalize(vertices[1] - position);
            Vector3 normal = Vector3.Normalize(Vector3.Cross(vertices[2] - position, tangent));
            Vector3 binormal = Vector3.Normalize(Vector3.Cross(tangent, normal));

            for (int i = 0; i < convexVertices2D.Length; i++)
            {
                Vector3 vertex = vertices[i] - position;
                float x = Vector3.Dot(vertex, tangent);
                float y = Vector3.Dot(vertex, binormal);

                convexVertices2D[i] = new(i, x, y);
            }

            ConvexHullCreationResult<ConvexVertex2D> convexResult2D = ConvexHull.Create2D(convexVertices2D);

            List<int> indices = [];

            int cw = 1, ccw = convexResult2D.Result.Count - 1;
            while (true)
            {
                indices.Add(convexResult2D.Result[cw - 1].Index);
                indices.Add(convexResult2D.Result[cw].Index);
                indices.Add(convexResult2D.Result[ccw].Index);

                ccw--;

                if (cw == ccw)
                {
                    break;
                }

                indices.Add(convexResult2D.Result[cw].Index);
                indices.Add(convexResult2D.Result[ccw].Index);
                indices.Add(convexResult2D.Result[ccw + 1].Index);

                cw++;

                if (cw == ccw)
                {
                    break;
                }
            }

            return [.. indices];
        }
    }
}
