using System;
using System.Numerics;
using System.Text.Json;
using System.Text.Json.Serialization;

namespace HEIO.NET.Json
{
	/// <summary>
	/// Json converter for <see cref="Matrix4x4"/>.
	/// </summary>
	internal sealed class Matrix4x4JsonConverter : JsonConverter<Matrix4x4>
	{
		/// <inheritdoc/>
		public override Matrix4x4 Read(ref Utf8JsonReader reader, Type typeToConvert, JsonSerializerOptions options)
		{
			if(reader.TokenType != JsonTokenType.StartArray)
			{
				throw new JsonException("Matrix4x4 must be an array!");
			}

			Vector4[] rows = JsonSerializer.Deserialize<Vector4[]>(ref reader, options) 
				?? throw new JsonException("Failed to read Matrix4x4!");

			if(rows.Length < 4)
			{
				throw new JsonException("Matrix4x4 has too few rows! 4 rows required!");
			}

			return new(
				rows[0].X, rows[0].Y, rows[0].Z, rows[0].W,
				rows[1].X, rows[1].Y, rows[1].Z, rows[1].W,
				rows[2].X, rows[2].Y, rows[2].Z, rows[2].W,
				rows[3].X, rows[3].Y, rows[3].Z, rows[3].W);
		}

		/// <inheritdoc/>
		public override void Write(Utf8JsonWriter writer, Matrix4x4 value, JsonSerializerOptions options)
		{
			Vector4[] rows = new Vector4[]
			{
				new(value.M11, value.M12, value.M13, value.M14),
				new(value.M21, value.M22, value.M23, value.M24),
				new(value.M31, value.M32, value.M33, value.M34),
				new(value.M41, value.M42, value.M43, value.M44),
			};

			JsonSerializer.Serialize(writer, rows, options);
		}
	}
}
