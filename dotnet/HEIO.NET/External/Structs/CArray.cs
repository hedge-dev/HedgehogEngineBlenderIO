namespace HEIO.NET.External.Structs
{
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
