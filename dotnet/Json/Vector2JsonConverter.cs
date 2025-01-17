using System;
using System.Globalization;
using System.Numerics;
using System.Text.Json;
using System.Text.Json.Serialization;

namespace HEIO.NET.Json
{
    /// <summary>
    /// Json converter for <see cref="Vector2"/>.
    /// </summary>
    internal class Vector2JsonConverter : JsonConverter<Vector2>
	{
		/// <inheritdoc/>
		public override Vector2 Read(ref Utf8JsonReader reader, Type typeToConvert, JsonSerializerOptions options)
		{
			if(reader.TokenType != JsonTokenType.String)
			{
				throw new JsonException("Expected a string for Vector2!");
			}

			string[] values = reader.GetString()!.Split(' ');
			return new(
				float.Parse(values[0], CultureInfo.InvariantCulture),
				float.Parse(values[1], CultureInfo.InvariantCulture));
		}

		/// <inheritdoc/>
		public override void Write(Utf8JsonWriter writer, Vector2 value, JsonSerializerOptions options)
		{
            string output = 
                value.X.ToString("F4", CultureInfo.InvariantCulture) 
                + ' ' 
                + value.Y.ToString("F4", CultureInfo.InvariantCulture);

			writer.WriteStringValue(output);
		}
	}
}
