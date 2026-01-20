using SharpNeedle.Framework.HedgehogEngine.Mirage.MaterialData;
using SharpNeedle.Structs;
using System.Numerics;

namespace HEIO.NET.External.Structs
{
    public unsafe struct CMaterial
    {
        public char* name;
        public uint dataVersion;
        public char* filePath;
        public CSampleChunkNode* rootNode;

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

        public static CMaterial FromInternal(Material material)
        {
            return new()
            {
                name = material.Name.ToPointer(),
                dataVersion = material.DataVersion,
                filePath = (material.BaseFile?.Path).ToPointer(),
                rootNode = CSampleChunkNode.FromSampleChunkNodeTree(material.Root),

                shaderName = material.ShaderName.ToPointer(),
                alphaThreshold = material.AlphaThreshold,
                noBackFaceCulling = material.NoBackFaceCulling,
                blendMode = (byte)material.BlendMode,

                floatParametersSize = material.FloatParameters.Count,
                floatParameters = IMaterialParameter<Vector4>.FromInternalParameters<CFloatMaterialParameter>(material.FloatParameters),

                integerParametersSize = material.IntParameters.Count,
                integerParameters = IMaterialParameter<Vector4Int>.FromInternalParameters<CIntegerMaterialParameter>(material.IntParameters),

                boolParametersSize = material.BoolParameters.Count,
                boolParameters = IMaterialParameter<bool>.FromInternalParameters<CBoolMaterialParameter>(material.BoolParameters),

                texturesName = material.Texset.Name.ToPointer(),
                texturesSize = material.Texset.Textures.Count,
                textures = Allocate.AllocFromArray(material.Texset.Textures, CTexture.FromInternal),
            };
        }

        public static CMaterial* PointerFromInternal(Material material)
        {
            CMaterial* result = Allocate.Alloc<CMaterial>();
            *result = FromInternal(material);
            return result;
        }

        public readonly Material ToMaterial()
        {
            Material result = new()
            {
                Name = Util.FromPointer(name)!,
                DataVersion = dataVersion,

                ShaderName = Util.FromPointer(shaderName)!,
                AlphaThreshold = alphaThreshold,
                BlendMode = (MaterialBlendMode)blendMode,
                NoBackFaceCulling = noBackFaceCulling
            };

            if (rootNode != null)
            {
                result.Root = rootNode->ToSampleChunkNodeTree(result);
            }

            IMaterialParameter<Vector4>.ToInternalParameters(floatParameters, floatParametersSize, result.FloatParameters);
            IMaterialParameter<Vector4Int>.ToInternalParameters(integerParameters, integerParametersSize, result.IntParameters);
            IMaterialParameter<bool>.ToInternalParameters(boolParameters, boolParametersSize, result.BoolParameters);

            result.Texset = new()
            {
                Name = Util.FromPointer(texturesName)!,
                Textures = [.. Util.ToArray<CTexture, Texture>(textures, texturesSize)!]
            };

            return result;
        }
    }
}
