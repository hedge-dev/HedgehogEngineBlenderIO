using System.Runtime.InteropServices;

namespace HEIO.NET
{
    internal static unsafe class Util
    {
        public static string? FromPointer(char* pointer)
        {
            return Marshal.PtrToStringUni((nint)pointer);
        }

        public static string[] ToStringArray(char** values, nint valuesSize)
        {
            string[] result = new string[valuesSize];

            for (int i = 0; i < result.Length; i++)
            {
                result[i] = FromPointer(values[i])!;
            }

            return result;
        }
    }
}
