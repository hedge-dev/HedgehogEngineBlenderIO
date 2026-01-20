using HEIO.NET.Internal.Modeling;

namespace HEIO.NET.External.Structs
{
    public struct CMeshImportSettings : IConvertInternal<MeshImportSettings>
    {
        public uint vertexMergeMode;
        public float mergeDistance;
        public bool mergeSplitEdges;

        public bool mergeCollisionVertices;
        public float collisionVertexMergeDistance;
        public bool removeUnusedCollisionVertices;

        public static CMeshImportSettings FromInternal(MeshImportSettings settings)
        {
            return new()
            {
                vertexMergeMode = (uint)settings.VertexMergeMode,
                mergeDistance = settings.VertexMergeDistance,
                mergeSplitEdges = settings.MergeSplitEdges,
                mergeCollisionVertices = settings.MergeCollisionVertices,
                collisionVertexMergeDistance = settings.CollisionVertexMergeDistance,
                removeUnusedCollisionVertices = settings.RemoveUnusedCollisionVertices
            };
        }

        public readonly MeshImportSettings ToInternal()
        {
            return new(
                (VertexMergeMode)vertexMergeMode,
                mergeDistance,
                mergeSplitEdges,
                mergeCollisionVertices,
                collisionVertexMergeDistance,
                removeUnusedCollisionVertices
            );
        }
    }
}
