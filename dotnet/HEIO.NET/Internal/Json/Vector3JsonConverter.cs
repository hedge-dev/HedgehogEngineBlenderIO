using System;
using System.Globalization;
using System.Numerics;
using System.Text.Json;
using System.Text.Json.Serialization;

namespace HEIO.NET.Internal.Json
{
    /// <summary>
    /// Json converter for <see cref="Vector3"/>.
    /// </summary>
    internal class Vector3JsonConverter : JsonConverter<Vector3>
    {
        /// <inheritdoc/>
        public override Vector3 Read(ref Utf8JsonReader reader, Type typeToConvert, JsonSerializerOptions options)
        {
            if(reader.TokenType != JsonTokenType.String)
            {
                throw new JsonException("Expected a string for Vector3!");
            }

            string[] values = reader.GetString()!.Split(' ');
            return new(
                float.Parse(values[0], CultureInfo.InvariantCulture),
                float.Parse(values[1], CultureInfo.InvariantCulture),
                float.Parse(values[2], CultureInfo.InvariantCulture));
        }

        /// <inheritdoc/>
        public override void Write(Utf8JsonWriter writer, Vector3 value, JsonSerializerOptions options)
        {
            string output =
                value.X.ToString("F4", CultureInfo.InvariantCulture)
                + ' '
                + value.Y.ToString("F4", CultureInfo.InvariantCulture)
                + ' '
                + value.Z.ToString("F4", CultureInfo.InvariantCulture);

            writer.WriteStringValue(output);
        }
    }
}
