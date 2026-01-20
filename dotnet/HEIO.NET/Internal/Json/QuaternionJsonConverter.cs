using System;
using System.Globalization;
using System.Numerics;
using System.Text.Json;
using System.Text.Json.Serialization;

namespace HEIO.NET.Internal.Json
{
    /// <summary>
    /// Json converter for <see cref="Quaternion"/>.
    /// </summary>
    internal class QuaternionJsonConverter : JsonConverter<Quaternion>
    {
        /// <inheritdoc/>
        public override Quaternion Read(ref Utf8JsonReader reader, Type typeToConvert, JsonSerializerOptions options)
        {
            if(reader.TokenType != JsonTokenType.String)
            {
                throw new JsonException("Expected a string for Quaternion!");
            }

            string[] values = reader.GetString()!.Split(' ');
            return new(
                float.Parse(values[0], CultureInfo.InvariantCulture),
                float.Parse(values[1], CultureInfo.InvariantCulture),
                float.Parse(values[2], CultureInfo.InvariantCulture),
                float.Parse(values[3], CultureInfo.InvariantCulture));
        }

        /// <inheritdoc/>
        public override void Write(Utf8JsonWriter writer, Quaternion value, JsonSerializerOptions options)
        {
            string output =
                value.X.ToString("F4", CultureInfo.InvariantCulture)
                + ' '
                + value.Y.ToString("F4", CultureInfo.InvariantCulture)
                + ' '
                + value.Z.ToString("F4", CultureInfo.InvariantCulture)
                + ' '
                + value.W.ToString("F4", CultureInfo.InvariantCulture);

            writer.WriteStringValue(output);
        }
    }
}
