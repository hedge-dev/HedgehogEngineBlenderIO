namespace HEIO.NET
{
    public unsafe struct CStringPointerPair
    {
        public char* name;
        public void* pointer;

        public CStringPointerPair(char* name, void* pointer)
        {
            this.name = name;
            this.pointer = pointer;
        }
    }

    public unsafe struct CStringPointerPairs
    {
        public CStringPointerPair* pairs;
        public nint size;

        public CStringPointerPairs(CStringPointerPair* pairs, nint size)
        {
            this.pairs = pairs;
            this.size = size;
        }
    }
}
