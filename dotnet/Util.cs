using System.Runtime.InteropServices;

namespace HEIO.NET
{
    internal static unsafe class Util
    {
        public static char* ToPointer(this string? value)
        {
            return (char*)Marshal.StringToHGlobalUni(value);
        }

        public static string? FromPointer(char* pointer)
        {
            return Marshal.PtrToStringUni((nint)pointer);
        }

        public static T* Alloc<T>(nint count = 1) where T : unmanaged
        {
            if(count == 0)
            {
                return null;
            }

            return (T*)Marshal.AllocHGlobal(count  * sizeof(T));
        }

        public static void Free<T>(T* pointer) where T : unmanaged
        {
            Marshal.FreeHGlobal((nint)pointer);
        }

        public static void Free<T>(T** pointer) where T : unmanaged
        {
            Marshal.FreeHGlobal((nint)pointer);
        }

        public static char** FromStringArray(string[] values)
        {
            char** result = (char**)Util.Alloc<nint>(values.Length);

            for (int i = 0; i < values.Length; i++)
            {
                result[i] = values[i].ToPointer();
            }

            return result;
        }

        public static string[] ToStringArray(char** values, nint valuesSize)
        {
            string[] result = new string[valuesSize];

            for(int i = 0; i < result.Length; i++)
            {
                result[i] = FromPointer(values[i])!;
            }

            return result;
        }

        public static void FreeStringArray(char** values, nint size)
        {
            for (int i = 0; i < size; i++)
            {
                Free(values[i]);
            }

            Free(values);
        }
    }
}
