using HEIO.NET.Internal;
using HEIO.NET.Internal.Modeling;
using SharpNeedle.Framework.HedgehogEngine.Mirage.ModelData;

namespace HEIO.NET.External.Structs
{
    public unsafe struct CMeshDataSet : IConvertInternal<MeshDataSet>
    {
        public char* name;

        public CMeshData* meshData;
        public nint meshDataSize;

        public CModelNode* nodes;
        public nint nodesSize;

        public CSampleChunkNode* sampleChunkNodeRoot;

        public static CMeshDataSet FromInternal(MeshDataSet set)
        {
            return new()
            {
                name = set.Name.ToPointer(),

                meshData = Allocate.AllocFromArray(set.MeshData, CMeshData.FromInternal),
                meshDataSize = set.MeshData.Length,

                nodes = Allocate.AllocFromArray(set.Nodes, CModelNode.FromInternal),
                nodesSize = set.Nodes?.Length ?? 0,

                sampleChunkNodeRoot = CSampleChunkNode.FromSampleChunkNodeTree(set.SampleChunkNodeRoot)
            };
        }

        public readonly MeshDataSet ToInternal()
        {
            return new(
                Util.FromPointer(name)!,
                Util.ToArray<CMeshData, MeshData>(meshData, meshDataSize)!,
                Util.ToArray<CModelNode, Model.Node>(nodes, nodesSize),
                sampleChunkNodeRoot->ToSampleChunkNodeTree(null)
            );
        }
    }
}
