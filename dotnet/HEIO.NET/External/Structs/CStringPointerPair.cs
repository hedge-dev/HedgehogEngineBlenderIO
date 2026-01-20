using System;
using System.Collections.Generic;
using System.Linq;

namespace HEIO.NET.External.Structs
{
    public unsafe struct CStringPointerPair
    {
        public char* name;
        public void* pointer;

        public CStringPointerPair(char* name, void* pointer)
        {
            this.name = name;
            this.pointer = pointer;
        }

        public static CArray FromDictionary<I, O>(Dictionary<string, I> dictionary, Func<I, O> convert) where O : unmanaged
        {
            KeyValuePair<string, I>[] dictPairs = [.. dictionary];
            O* array = Allocate.AllocFromArray([.. dictPairs.Select(x => x.Value)], convert);
            CStringPointerPair[] resultPairs = [.. dictPairs.Select((x, i) => new CStringPointerPair(x.Key.ToPointer(), &array[i]))];
            CStringPointerPair* result = Allocate.AllocFromArray(resultPairs);

            return new(
                result,
                dictPairs.Length
            );
        }
    }
}
