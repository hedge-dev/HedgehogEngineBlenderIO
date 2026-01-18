using HEIO.NET.Internal.Json;
using HEIO.NET.Internal.Modeling.ConvertTo;
using SharpNeedle.Framework.HedgehogEngine.Mirage;
using SharpNeedle.Framework.HedgehogEngine.Mirage.ModelData;
using System.IO;
using System.Text.Json;
using System.Text.Json.Serialization;

namespace HEIO.NET.Internal.Modeling
{
    public readonly struct MeshCompileData
    {
        public string Name { get; }

        public MeshData[] MeshData { get; }

        public Model.Node[]? Nodes { get; }

        public SampleChunkNode[]? SCAParameters { get; }

        [JsonConstructor]
        public MeshCompileData(string name, MeshData[] meshData, Model.Node[]? nodes, SampleChunkNode[]? scaParameters)
        {
            Name = name;
            MeshData = meshData;
            Nodes = nodes;
            SCAParameters = scaParameters;
        }

        public static ModelBase[] ToHEModels(MeshCompileData[] compileData, ModelVersionMode versionMode, Topology topology, bool optimizedVertexData, bool multithreading = true)
        {
            return ModelConverter.CompileMeshData(compileData, versionMode, topology, optimizedVertexData, multithreading);
        }

        public void SaveToJson(string directory)
        {
            string json = JsonSerializer.Serialize(this, SourceGenerationContext.Default.MeshCompileData);
            File.WriteAllText(Path.Combine(directory, Name + ".json"), json);
        }

        public static MeshCompileData FromJson(string json)
        {
            return JsonSerializer.Deserialize(json, SourceGenerationContext.Default.MeshCompileData);
        }
    }
}
