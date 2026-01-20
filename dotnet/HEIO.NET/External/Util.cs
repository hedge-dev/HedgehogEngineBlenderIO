using System;
using System.Linq;
using System.Runtime.InteropServices;

namespace HEIO.NET.External
{
    internal interface IConvertInternal<T>
    {
        public T ToInternal();
    }

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
        
        public static T[]? ToArray<T>(T* values, nint valuesSize) where T : unmanaged
        {
            if(values == null)
            {
                return null;
            }

            T[] result = new T[valuesSize];
            new Span<T>(values, (int)valuesSize).CopyTo(new Span<T>(result, 0, (int)valuesSize));
            return result;
        }

        public static O[]? ToArray<I, O>(I* values, nint valuesSize) where I : unmanaged, IConvertInternal<O>
        {
            return ToArray(values, valuesSize)?.Select(x => x.ToInternal()).ToArray();
        }

        public static T[][]? To2DArray<T>(T** values, nint valuesSize, nint innerValuesSize) where T : unmanaged
        {
            if(values == null)
            {
                return null;
            }

            T[][] result = new T[valuesSize][];

            for(int i = 0; i < result.Length; i++)
            {
                result[i] = ToArray(values[i], innerValuesSize)!;
            }

            return result;
        }
    }
}
