using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace HEIO.NET.VertexUtils
{
    internal static class PolygonUtilities
    {
        public static IEnumerable<ushort> FlipTriangles(ushort[] indices)
        {
            for(int i = 0; i < indices.Length; i += 3)
            {
                yield return indices[i + 1];
                yield return indices[i];
                yield return indices[i + 2];
            }
        }

        public static IEnumerable<ushort> ExpandStrip(ushort[] indices)
        {
            bool rev = false;
            ushort a = indices[0];
            ushort b = indices[1];

            for(int i = 2; i < indices.Length; i++)
            {
                ushort c = indices[i];

                if(c == ushort.MaxValue)
                {
                    a = indices[++i];
                    b = indices[++i];
                    rev = false;
                    continue;
                }

                rev = !rev;

                if(a != b && b != c && c != a)
                {
                    if(rev)
                    {
                        yield return b;
                        yield return a;
                        yield return c;
                    }
                    else
                    {
                        yield return a;
                        yield return b;
                        yield return c;
                    }
                }

                a = b;
                b = c;
            }
        }
    }
}
