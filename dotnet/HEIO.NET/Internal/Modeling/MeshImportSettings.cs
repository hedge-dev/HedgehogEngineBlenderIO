namespace HEIO.NET.Internal.Modeling
{
    public readonly struct MeshImportSettings
    {
        public VertexMergeMode VertexMergeMode { get; }
        public float VertexMergeDistance { get; }
        public bool MergeSplitEdges { get; }

        public bool MergeCollisionVertices { get; }
        public float CollisionVertexMergeDistance { get; }
        public bool RemoveUnusedCollisionVertices { get; }

        public bool MergeVertices => VertexMergeMode != VertexMergeMode.None;

        public MeshImportSettings(VertexMergeMode vertexMergeMode, float vertexMergeDistance, bool mergeSplitEdges, bool mergeCollisionVertices, float collisionVertexMergeDistance, bool removeUnusedCollisionVertices)
        {
            VertexMergeMode = vertexMergeMode;
            VertexMergeDistance = vertexMergeDistance;
            MergeSplitEdges = mergeSplitEdges;
            MergeCollisionVertices = mergeCollisionVertices;
            CollisionVertexMergeDistance = collisionVertexMergeDistance;
            RemoveUnusedCollisionVertices = removeUnusedCollisionVertices;
        }
    }
}
