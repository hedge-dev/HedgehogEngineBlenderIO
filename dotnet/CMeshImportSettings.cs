using HEIO.NET.Internal.Modeling;

namespace HEIO.NET
{
    public struct CMeshImportSettings
    {
        public uint vertexMergeMode;
        public float mergeDistance;
        public bool mergeSplitEdges;

        public bool mergeCollisionVertices;
        public float collisionVertexMergeDistance;
        public bool removeUnusedCollisionVertices;

        public readonly MeshImportSettings ToMeshImportSettings()
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
