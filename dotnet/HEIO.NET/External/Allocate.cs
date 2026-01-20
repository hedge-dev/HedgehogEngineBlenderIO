using System;
using System.Collections.Generic;
using System.Linq;
using System.Runtime.InteropServices;

namespace HEIO.NET.External
{
    public static unsafe class Allocate
    {
        private static readonly List<nint> _allocations = [];

        [UnmanagedCallersOnly(EntryPoint = "free_all")]
        public static void FreeAll()
        {
            foreach (nint pointer in _allocations)
            {
                Marshal.FreeHGlobal(pointer);
            }

            _allocations.Clear();
        }

        public static char* ToPointer(this string? value)
        {
            char* result = (char*)Marshal.StringToHGlobalUni(value);
            _allocations.Add((nint)result);
            return result;
        }

        public static T* Alloc<T>(nint count = 1) where T : unmanaged
        {
            if (count == 0)
            {
                return null;
            }

            T* result = (T*)Marshal.AllocHGlobal(count * sizeof(T));
            _allocations.Add((nint)result);
            return result;
        }

        public static T* AllocFromArray<T>(IList<T>? values) where T : unmanaged
        {
            T* result = Alloc<T>(values?.Count ?? 0);

            if (result != null)
            {
                if (values is not T[] array)
                {
                    array = [.. values!];
                }

                new Span<T>(array, 0, array.Length).CopyTo(new Span<T>(result, array.Length));
            }

            return result;
        }

        public static O* AllocFromArray<I, O>(IList<I>? values, Func<I, O> convert) where O : unmanaged
        {
            return AllocFromArray(values?.Select(convert).ToArray());
        }

        public static void AllocFrom2DArray<T>(IList<IList<T>> values, out T** outValues) where T : unmanaged
        {
            if (values.Count == 0)
            {
                outValues = null;
                return;
            }

            T[] allValues = values.SelectMany(x => x).ToArray();
            T* outAllValues = AllocFromArray(allValues);

            outValues = (T**)Alloc<nint>(values.Count);

            T* currentValues = outAllValues;
            for (int i = 0; i < values.Count; i++)
            {
                outValues[i] = currentValues;
                currentValues += values.Count;
            }
        }

        public static void AllocFrom2DArray<T>(IList<IList<T>> values, out T** outValues, out nint* outSizes) where T : unmanaged
        {
            AllocFrom2DArray(values, out outValues);

            outSizes = outValues != null
                ? AllocFromArray(values.Select(x => (nint)x.Count).ToArray())
                : null;
        }

        public static char** FromStringArray(string[] values)
        {
            char** result = (char**)Alloc<nint>(values.Length);

            for (int i = 0; i < values.Length; i++)
            {
                result[i] = values[i].ToPointer();
            }

            return result;
        }
    }
}
