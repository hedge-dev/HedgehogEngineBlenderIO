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

    public unsafe struct CArray
    {
        public void* array;
        public nint size;

        public CArray(void* array, nint size)
        {
            this.array = array;
            this.size = size;
        }
    }
}
