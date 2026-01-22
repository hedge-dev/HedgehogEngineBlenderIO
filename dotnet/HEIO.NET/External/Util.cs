using System;
using System.Linq;
using System.Runtime.InteropServices;
using System.Text;

namespace HEIO.NET.External
{
    internal interface IConvertInternal<T>
    {
        public T ToInternal();
    }

    internal static unsafe class Util
    {
        public static bool IsWindows = RuntimeInformation.IsOSPlatform(OSPlatform.Windows);

        public static T[]? ToArray<T>(T* values, int valuesSize) where T : unmanaged
        {
            if(values == null)
            {
                return null;
            }

            T[] result = new T[valuesSize];
            new Span<T>(values, (int)valuesSize).CopyTo(new Span<T>(result, 0, (int)valuesSize));
            return result;
        }

        public static O[]? ToArray<I, O>(I* values, int valuesSize) where I : unmanaged, IConvertInternal<O>
        {
            return ToArray(values, valuesSize)?.Select(x => x.ToInternal()).ToArray();
        }

        public static O[]? PointersToArray<I, O>(I** values, int valuesSize) where I : unmanaged, IConvertInternal<O>
        {
            return ToArray((nint*)values, valuesSize)?.Select(x => ((I*)x)->ToInternal()).ToArray();
        }

        public static T[][]? To2DArray<T>(T** values, int valuesSize, int innerValuesSize) where T : unmanaged
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
    

        public static string? ToString(char* pointer)
        {
            if(IsWindows)
            {
                return Marshal.PtrToStringUni((nint)pointer);
            }
            else
            {
                int* utf32 = (int*)pointer;
                int length = 0;

                while (utf32[length] != 0)
                {
                    length++;
                }

                return Encoding.UTF32.GetString((byte*)pointer, length * 4);
            }
        }

        public static string[]? ToStringArray(char** values, int valuesSize)
        {
            if(values == null)
            {
                return null;
            }

            string[] result = new string[valuesSize];

            for (int i = 0; i < result.Length; i++)
            {
                result[i] = ToString(values[i])!;
            }

            return result;
        }
        
    }
}
