using SharpNeedle.Framework.HedgehogEngine.Mirage.MaterialData;
using SharpNeedle.Structs;
using System.Collections.Generic;
using System.Numerics;

namespace HEIO.NET.External.Structs
{
    public unsafe interface IMaterialParameter<V> where V : unmanaged
    {
        public char* Name { get; set; }
        public V Value { get; set; }

        public static T* FromInternalParameters<T>(Dictionary<string, MaterialParameter<V>> parameters) where T : unmanaged, IMaterialParameter<V>
        {
            T* result = Allocate.Alloc<T>(parameters.Count);

            int index = 0;
            foreach (KeyValuePair<string, MaterialParameter<V>> parameter in parameters)
            {
                T* resultParameter = &result[index];
                resultParameter->Name = parameter.Key.AllocString();
                resultParameter->Value = parameter.Value.Value;
                index++;
            }

            return result;
        }

        public static void ToInternalParameters<T>(T* parameters, nint size, Dictionary<string, MaterialParameter<V>> output) where T : unmanaged, IMaterialParameter<V>
        {
            for (int i = 0; i < size; i++)
            {
                T* parameter = &parameters[i];

                output.Add(
                    Util.ToString(parameter->Name)!,
                    new() { Value = parameter->Value }
                );
            }
        }
    }

    public unsafe struct CFloatMaterialParameter : IMaterialParameter<Vector4>
    {
        public char* name;
        public Vector4 value;

        public char* Name
        {
            readonly get => name;
            set => name = value;
        }

        public Vector4 Value
        {
            readonly get => value;
            set => this.value = value;
        }
    }

    public unsafe struct CIntegerMaterialParameter : IMaterialParameter<Vector4Int>
    {
        public char* name;
        public Vector4Int value;

        public char* Name
        {
            readonly get => name;
            set => name = value;
        }

        public Vector4Int Value
        {
            readonly get => value;
            set => this.value = value;
        }
    }

    public unsafe struct CBoolMaterialParameter : IMaterialParameter<bool>
    {
        public char* name;
        public bool value;

        public char* Name
        {
            readonly get => name;
            set => name = value;
        }

        public bool Value
        {
            readonly get => value;
            set => this.value = value;
        }
    }
}
