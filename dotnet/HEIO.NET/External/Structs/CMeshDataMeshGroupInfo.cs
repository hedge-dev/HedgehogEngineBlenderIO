using HEIO.NET.Internal.Modeling;

namespace HEIO.NET.External.Structs
{
    public unsafe struct CMeshDataMeshGroupInfo : IConvertInternal<MeshDataMeshGroupInfo>
    {
        public char* name;
        public int size;

        public static CMeshDataMeshGroupInfo FromInternal(MeshDataMeshGroupInfo info)
        {
            return new()
            {
                name = info.Name.ToPointer(),
                size = info.Size
            };
        }

        public readonly MeshDataMeshGroupInfo ToInternal()
        {
            return new(
                Util.FromPointer(name)!,
                size
            );
        }
    }
}
