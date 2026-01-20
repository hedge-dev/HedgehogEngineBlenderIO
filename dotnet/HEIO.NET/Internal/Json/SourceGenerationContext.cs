using System.Numerics;
using System.Text.Json.Serialization;

namespace HEIO.NET.Internal.Json
{
    [JsonSourceGenerationOptions(
        WriteIndented = true, 
        Converters = [
            typeof(Matrix4x4JsonConverter),
            typeof(QuaternionJsonConverter),
            typeof(Vector2JsonConverter),
            typeof(Vector3JsonConverter),
            typeof(Vector4JsonConverter)
        ],
        DefaultIgnoreCondition = JsonIgnoreCondition.WhenWritingNull
    )]
    [JsonSerializable(typeof(MeshDataSet))]
    [JsonSerializable(typeof(Vector4[]))]
    internal partial class SourceGenerationContext : JsonSerializerContext
    {
    }
}
