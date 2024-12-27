using HEIO.NET.VertexUtils;
using SharpNeedle.Framework.HedgehogEngine.Mirage;
using SharpNeedle.Resource;
using System.Collections.Generic;
using System.Linq;
using System.Numerics;

namespace HEIO.NET
{
    public struct Vertex
    {
        public Vector3 Position { get; set; }

        public Vector3[]? MorphPositions { get; set; }

        public Vector3 Normal { get; set; }

        public Vector3 Tangent { get; set; }

        public List<VertexWeight> Weights { get; set; }

        public Vertex(Vector3 position, int morphCount, Vector3 normal, Vector3 tangent, List<VertexWeight> weights)
        {
            Position = position;
            MorphPositions = morphCount == 0 ? null : new Vector3[morphCount];
            Normal = normal;
            Tangent = tangent;
            Weights = [.. weights.Where(x => x.Weight != 0).OrderBy(x => x.Index)];
        }

        private static bool CompareMorphs(Vector3[] a, Vector3[] b, float mergeDistanceSquared)
        {
            for(int i = 0; i < a.Length; i++)
            {
                if(Vector3.DistanceSquared(a[i], b[i]) >= mergeDistanceSquared)
                {
                    return false;
                }
            }

            return true;
        }

        public static EqualityComparer<Vertex> GetMergeComparer(float mergeDistance, bool compareNormals, bool compareMorphs)
        {
            float mergeDistanceSquared = mergeDistance * mergeDistance;

            if(compareMorphs)
            {
                if(compareNormals)
                {
                    return EqualityComparer<Vertex>.Create((v1, v2) =>
                        Vector3.DistanceSquared(v1.Position, v2.Position) < mergeDistanceSquared
                        && CompareMorphs(v1.MorphPositions!, v2.MorphPositions!, mergeDistanceSquared)
                        && VertexWeight.CompareEquality(v1.Weights, v2.Weights)
                        && Vector3.Dot(v1.Normal, v2.Normal) > 0.995f);
                }
                else
                {
                    return EqualityComparer<Vertex>.Create((v1, v2) =>
                        Vector3.DistanceSquared(v1.Position, v2.Position) < mergeDistanceSquared
                        && CompareMorphs(v1.MorphPositions!, v2.MorphPositions!, mergeDistanceSquared)
                        && VertexWeight.CompareEquality(v1.Weights, v2.Weights));
                }
            }
            else
            {
                if(compareNormals)
                {
                    return EqualityComparer<Vertex>.Create((v1, v2) =>
                        Vector3.DistanceSquared(v1.Position, v2.Position) < mergeDistanceSquared
                        && VertexWeight.CompareEquality(v1.Weights, v2.Weights)
                        && Vector3.Dot(v1.Normal, v2.Normal) > 0.995f);
                }
                else
                {
                    return EqualityComparer<Vertex>.Create((v1, v2) =>
                        Vector3.DistanceSquared(v1.Position, v2.Position) < mergeDistanceSquared
                        && VertexWeight.CompareEquality(v1.Weights, v2.Weights));
                }
            }

        }

    }

    public enum VertexMergeMode
    {
        None,
        SubMesh,
        SubMeshGroup,
        All
    }

    public class MeshData
    {
        public string Name { get; set; }

        public IList<Vertex> Vertices { get; set; }
            
        public IList<int> TriangleIndices { get; set; }

        public IList<Vector3>? PolygonNormals { get; set; }

        public IList<Vector3>? PolygonTangents { get; set; }

        public IList<IList<Vector2>> TextureCoordinates { get; set; }

        public IList<IList<Vector4>> Colors { get; set; }

        public bool UseByteColors { get; set; }


        public IList<ResourceReference<Material>> SetMaterials { get; set; }

        public IList<MeshSlot> SetSlots { get; }

        public IList<int> SetSizes { get; set; }


        public IList<string> GroupNames { get; set; }

        public IList<int> GroupSizes { get; set; }


        public MeshData(
            string name, 
            IList<Vertex> vertices, 
            IList<int> triangleIndices, 
            IList<Vector3>? polygonNormals, 
            IList<Vector3>? polygonTangents,
            IList<IList<Vector2>> textureCoordinates, 
            IList<IList<Vector4>> colors, 
            bool useByteColors, 
            IList<ResourceReference<Material>> setMaterials, 
            IList<MeshSlot> setSlots, 
            IList<int> setSizes, 
            IList<string> groupNames, 
            IList<int> groupSizes)
        {
            Name = name;
            Vertices = vertices;
            TriangleIndices = triangleIndices;
            PolygonNormals = polygonNormals;
            PolygonTangents = polygonTangents;
            TextureCoordinates = textureCoordinates;
            Colors = colors;
            UseByteColors = useByteColors;
            SetMaterials = setMaterials;
            SetSlots = setSlots;
            SetSizes = setSizes;
            GroupNames = groupNames;
            GroupSizes = groupSizes;
        }

        public static MeshData FromHEMorph(ModelBase model, MorphModel morph, VertexMergeMode vertexMergeMode, float mergeDistance, bool mergeSplitEdges)
        {
            Topology topology = model.Root?.FindNode("Topology")?.Value == 3
                ? Topology.TriangleList
                : Topology.TriangleStrips;

            MeshProcessor processor = new(
                morph.Name,
                topology,
                vertexMergeMode != VertexMergeMode.None,
                mergeDistance,
                mergeSplitEdges,
                morph.Targets.Count
            );

            processor.AddGroupInfo(morph.Meshgroup!.Name ?? string.Empty, morph.Meshgroup!.Count);

            for(int i = 0; i < morph.Meshgroup.Count; i++)
            {
                processor.AddMesh(morph.Meshgroup[i], i == morph.Meshgroup.Count - 1);
            }

            for(int i = 0; i < morph.Targets.Count; i++)
            {
                processor.AddMorphPositions(morph.Targets[i].Positions, i, 0);
            }

            processor.ProcessData();

            return processor.ResultData;
        }

        public static MeshData[] FromHEMeshGroups(ModelBase model, VertexMergeMode vertexMergeMode, float mergeDistance, bool mergeSplitEdges)
        {
            Topology topology = model.Root?.FindNode("Topology")?.Value == 3
                ? Topology.TriangleList
                : Topology.TriangleStrips;

            List<MeshData> results = [];
            
            foreach(MeshGroup group in model.Groups)
            {
                string meshname = model.Name;
                if(!string.IsNullOrWhiteSpace(group.Name))
                {
                    meshname += "_" + group.Name;
                }

                MeshProcessor processor = new(
                    meshname,
                    topology,
                    vertexMergeMode != VertexMergeMode.None,
                    mergeDistance,
                    mergeSplitEdges,
                    0
                );

                processor.AddGroupInfo(group.Name ?? string.Empty, group.Count);

                foreach(Mesh mesh in group)
                {
                    processor.AddMesh(mesh);

                    if(vertexMergeMode == VertexMergeMode.SubMesh)
                    {
                        processor.ProcessData();
                    }
                }

                processor.ProcessData();
                results.Add(processor.ResultData);
            }

            return [.. results];
        }
        
        public static MeshData FromHEModel(ModelBase model, VertexMergeMode vertexMergeMode, float mergeDistance, bool mergeSplitEdges)
        {
            Topology topology = model.Root?.FindNode("Topology")?.Value == 3 
                ? Topology.TriangleList 
                : Topology.TriangleStrips;

            MeshProcessor processor = new(
                model.Name, 
                topology, 
                vertexMergeMode != VertexMergeMode.None, 
                mergeDistance, 
                mergeSplitEdges,
                0
            );

            foreach(MeshGroup group in model.Groups)
            {
                processor.AddGroupInfo(group.Name ?? string.Empty, group.Count);

                foreach(Mesh mesh in group)
                {
                    processor.AddMesh(mesh);

                    if(vertexMergeMode == VertexMergeMode.SubMesh)
                    {
                        processor.ProcessData();
                    }
                }

                if(vertexMergeMode == VertexMergeMode.SubMeshGroup)
                {
                    processor.ProcessData();
                }
            }

            processor.ProcessData();

            return processor.ResultData;
        }

    }
}
