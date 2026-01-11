namespace HEIO.NET.Internal.Modeling
{
    public readonly struct MeshImportSettings
    {
        public VertexMergeMode VertexMergeMode  {get; }
        public float MergeDistance  {get; }
        public bool MergeSplitEdges { get; }

        public bool MergeVertices => VertexMergeMode != VertexMergeMode.None;

        public MeshImportSettings(VertexMergeMode vertexMergeMode, float mergeDistance, bool mergeSplitEdges)
        {
            VertexMergeMode = vertexMergeMode;
            MergeDistance = mergeDistance;
            MergeSplitEdges = mergeSplitEdges;
        }
    }
}
