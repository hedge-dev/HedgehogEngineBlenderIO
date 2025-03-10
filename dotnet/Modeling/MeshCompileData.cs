using HEIO.NET.Json;
using HEIO.NET.Modeling.ConvertTo;
using SharpNeedle.Framework.HedgehogEngine.Mirage;
using System.IO;
using System.Text.Json;
using System.Text.Json.Serialization;

namespace HEIO.NET.Modeling
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
            string json = JsonSerializer.Serialize(this, JsonConverters.Options);
            File.WriteAllText(Path.Combine(directory, Name + ".json"), json);
        }

        public static MeshCompileData FromJson(string json)
        {
            return JsonSerializer.Deserialize<MeshCompileData>(json, JsonConverters.Options);
        }
    }
}
