using SharpNeedle.Framework.HedgehogEngine.Mirage.MaterialData;
using SharpNeedle.IO;
using SharpNeedle.Resource;
using SharpNeedle.Structs;
using System.Collections.Generic;
using System.Numerics;
using System.Runtime.InteropServices;

namespace HEIO.NET
{
    internal class InternalMaterial : Material
    {
        public void SetBaseFile(IFile? file)
        {
            BaseFile = file;
        }
    }


    public unsafe interface IMaterialParameter<V>
    {
        public char* Name { get; set; }
        public V Value { get; set;  }
    }

    public unsafe struct CFloatMaterialParameter : IMaterialParameter<Vector4>
    {
        public char* name;
        public Vector4 value;

        public unsafe char* Name { 
            readonly get => name; 
            set => name = value; 
        }

        public Vector4 Value { 
            readonly get => value;
            set => this.value = value; 
        }
    }

    public unsafe struct CIntegerMaterialParameter : IMaterialParameter<Vector4Int>
    {
        public char* name;
        public Vector4Int value;

        public unsafe char* Name
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

        public unsafe char* Name { 
            readonly get => name; 
            set => name = value; 
        }

        public bool Value { 
            readonly get => value;
            set => this.value = value; 
        }
    }

    public unsafe struct CTexture
    {
        public char* name;
        public char* pictureName;
        public byte texCoordIndex;
        public byte wrapModeU;
        public byte wrapModeV;
        public char* type;
    }

    public unsafe struct CMaterial
    {
        public char* name;
        public uint dataVersion;
        public char* filePath;

        public char* shaderName;
        public byte alphaThreshold;
        public bool noBackFaceCulling;
        public byte blendMode;

        public CFloatMaterialParameter* floatParameters;
        public nint floatParametersSize;

        public CIntegerMaterialParameter* integerParameters;
        public nint integerParametersSize;

        public CBoolMaterialParameter* boolParameters;
        public nint boolParametersSize;

        public char* texturesName;
        public CTexture* textures;
        public nint texturesSize;

        public static CMaterial* FromMaterial(Material material)
        {
            CMaterial* result = Util.Alloc<CMaterial>();

            result->name = material.Name.ToPointer();
            result->dataVersion = material.DataVersion;
            result->filePath = (material.BaseFile?.Path).ToPointer();

            result->shaderName = material.ShaderName.ToPointer();
            result->alphaThreshold = material.AlphaThreshold;
            result->noBackFaceCulling = material.NoBackFaceCulling;
            result->blendMode = (byte)material.BlendMode;

            result->floatParametersSize = material.FloatParameters.Count;
            result->floatParameters = FromParameters<CFloatMaterialParameter, Vector4>(material.FloatParameters);

            result->integerParametersSize = material.IntParameters.Count;
            result->integerParameters = FromParameters<CIntegerMaterialParameter, Vector4Int>(material.IntParameters);

            result->boolParametersSize = material.BoolParameters.Count;
            result->boolParameters = FromParameters<CBoolMaterialParameter, bool>(material.BoolParameters);

            result->texturesName = material.Texset.Name.ToPointer();
            result->texturesSize = material.Texset.Textures.Count;
            result->textures = Util.Alloc<CTexture>(result->texturesSize);

            for(int i = 0; i < result->texturesSize; i++)
            {
                Texture texture = material.Texset.Textures[i];
                CTexture* resultTexture = &result->textures[i];

                resultTexture->name = texture.Name.ToPointer();
                resultTexture->pictureName = texture.PictureName.ToPointer();
                resultTexture->texCoordIndex = texture.TexCoordIndex;
                resultTexture->wrapModeU = (byte)texture.WrapModeU;
                resultTexture->wrapModeV = (byte)texture.WrapModeV;
                resultTexture->type = texture.Type.ToPointer();
            }

            return result;
        }

        private static T* FromParameters<T, V>(Dictionary<string, MaterialParameter<V>> parameters) where T : unmanaged, IMaterialParameter<V> where V : unmanaged
        {
            T* result = Util.Alloc<T>(parameters.Count);

            int index = 0;
            foreach (KeyValuePair<string, MaterialParameter<V>> parameter in parameters)
            {
                T* resultParameter = &result[index];
                resultParameter->Name = parameter.Key.ToPointer();
                resultParameter->Value = parameter.Value.Value;
                index++;
            }

            return result;
        }

        public Material ToMaterial()
        {
            InternalMaterial result = new()
            {
                Name = Util.FromPointer(name)!,
                DataVersion = dataVersion,

                ShaderName = Util.FromPointer(shaderName)!,
                AlphaThreshold = alphaThreshold,
                BlendMode = (MaterialBlendMode)blendMode,
                NoBackFaceCulling = noBackFaceCulling
            };

            ToParameters(floatParameters, floatParametersSize, result.FloatParameters);
            ToParameters(integerParameters, integerParametersSize, result.IntParameters);
            ToParameters(boolParameters, boolParametersSize, result.BoolParameters);

            result.Texset = new()
            {
                Name = Util.FromPointer(texturesName)!
            };

            for(int i = 0; i < texturesSize; i++)
            {
                CTexture* texture = &textures[i];

                result.Texset.Textures.Add(new()
                {
                    Name = Util.FromPointer(texture->name)!,
                    PictureName = Util.FromPointer(texture->pictureName)!,
                    TexCoordIndex = texture->texCoordIndex,
                    WrapModeU = (WrapMode)texture->wrapModeU,
                    WrapModeV = (WrapMode)texture->wrapModeV,
                    Type = Util.FromPointer(texture->type)!
                });
            }

            return result;
        }

        private static void ToParameters<T, V>(T* parameters, nint size, Dictionary<string, MaterialParameter<V>> output) where T : unmanaged, IMaterialParameter<V> where V : unmanaged
        {
            for (int i = 0; i < size; i++)
            {
                T* parameter = &parameters[i];

                output.Add(
                    Util.FromPointer(parameter->Name)!,
                    new() { Value = parameter->Value }
                );
            }
        }

        [UnmanagedCallersOnly(EntryPoint = "material_free")]
        public static void Free(CMaterial* material)
        {
            FreeParameters<CFloatMaterialParameter, Vector4>(material->floatParameters, material->floatParametersSize);
            FreeParameters<CIntegerMaterialParameter, Vector4Int>(material->integerParameters, material->integerParametersSize);
            FreeParameters<CBoolMaterialParameter, bool>(material->boolParameters, material->boolParametersSize);

            for (int i = 0; i < material->texturesSize; i++)
            {
                CTexture* parameter = &material->textures[i];
                Util.Free(parameter->name);
                Util.Free(parameter->pictureName);
                Util.Free(parameter->type);
            }

            Util.Free(material->name);
            Util.Free(material->shaderName);
            Util.Free(material->texturesName);
            Util.Free(material->textures);

            Util.Free(material);
        }

        private static void FreeParameters<T, V>(T* parameters, nint parametersSize) where T : unmanaged, IMaterialParameter<V> where V : unmanaged
        {
            for (int i = 0; i < parametersSize; i++)
            {
                T* parameter = &parameters[i];
                Util.Free(parameter->Name);
            }

            Util.Free(parameters);
        }

        [UnmanagedCallersOnly(EntryPoint = "material_read_file")]
        public static CMaterial* ReadFiles(char* filePath)
        {            
            string filePathString = Util.FromPointer(filePath)!;
            Material material = new ResourceManager().Open<Material>(filePathString);
            return FromMaterial(material);
        }
    }
}
