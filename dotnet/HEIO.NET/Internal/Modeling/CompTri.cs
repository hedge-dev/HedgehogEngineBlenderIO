using System;

namespace HEIO.NET.Internal.Modeling
{
    internal readonly struct CompTri : IComparable<CompTri>
    {
        public readonly uint i1, i2, i3;

        public CompTri(int i1, int i2, int i3)
        {
            if(i1 > i2)
            {
                (i1, i2) = (i2, i1);
            }

            if(i2 > i3)
            {
                (i2, i3) = (i3, i2);
            }

            if(i1 > i2)
            {
                (i1, i2) = (i2, i1);
            }

            this.i1 = (uint)i1;
            this.i2 = (uint)i2;
            this.i3 = (uint)i3;
        }

        public CompTri(uint i1, uint i2, uint i3)
        {
            if(i1 > i2)
            {
                (i1, i2) = (i2, i1);
            }

            if(i2 > i3)
            {
                (i2, i3) = (i3, i2);
            }

            if(i1 > i2)
            {
                (i1, i2) = (i2, i1);
            }

            this.i1 = i1;
            this.i2 = i2;
            this.i3 = i3;
        }

        public int CompareTo(CompTri other)
        {
            if(i1 != other.i1)
            {
                return i1 > other.i1 ? 1 : -1;
            }

            if(i2 != other.i2)
            {
                return i2 > other.i2 ? 1 : -1;
            }

            if(i3 != other.i3)
            {
                return i3 > other.i3 ? 1 : -1;
            }

            return 0;
        }


    }
}
