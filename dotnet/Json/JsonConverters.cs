using System.Text.Json;
using System.Text.Json.Serialization;

namespace HEIO.NET.Json
{
    internal static class JsonConverters
    {
        public static JsonSerializerOptions Options { get; }

        static JsonConverters()
        {
            Options = new()
            {
                WriteIndented = true,
                DefaultIgnoreCondition = JsonIgnoreCondition.WhenWritingNull
            };
            Options.Converters.Add(new Matrix4x4JsonConverter());
            Options.Converters.Add(new QuaternionJsonConverter());
            Options.Converters.Add(new Vector2JsonConverter());
            Options.Converters.Add(new Vector3JsonConverter());
            Options.Converters.Add(new Vector4JsonConverter());
        }
    }
}
