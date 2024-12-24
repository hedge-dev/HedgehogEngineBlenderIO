using System.Collections.Generic;

namespace HEIO.NET.VertexUtils
{
    public struct VertexWeight
    {
        public short Index { get; set; }

        public float Weight { get; set; }

        public VertexWeight(short index, float weight)
        {
            Index = index;
            Weight = weight;
        }

        /// <summary>
        /// Compares two vertex weight sequences for equality.
        /// Assumes sequences are ordered
        /// </summary>
        public static bool CompareEquality(IList<VertexWeight> a, IList<VertexWeight> b)
        {
            if(a.Count != b.Count)
            {
                return false;
            }

            if(a.Count == 0)
            {
                return true;
            }

            IEnumerator<VertexWeight> enumA = a.GetEnumerator();
            IEnumerator<VertexWeight> enumB = b.GetEnumerator();

            while(enumA.MoveNext() && enumB.MoveNext())
            {
                if(enumA.Current.Index != enumB.Current.Index)
                {
                    return false;
                }

                float diff = enumA.Current.Weight - enumB.Current.Weight;
                if(diff is < (-0.001f) or > 0.001f)
                {
                    return false;
                }
            }

            return true;
        }

        public override string ToString()
        {
            return $"{Index}: {Weight}";
        }
    }
}
