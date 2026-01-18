using HEIO.NET.Internal.Modeling;
using System;
using System.Collections.Generic;
using System.Numerics;
using System.Text;
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
    [JsonSerializable(typeof(MeshCompileData))]
    [JsonSerializable(typeof(Vector4[]))]
    internal partial class SourceGenerationContext : JsonSerializerContext
    {
    }
}
