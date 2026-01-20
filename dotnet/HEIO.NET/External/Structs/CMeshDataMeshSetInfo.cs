using HEIO.NET.Internal.Modeling;
using SharpNeedle.Framework.HedgehogEngine.Mirage.MaterialData;
using SharpNeedle.Framework.HedgehogEngine.Mirage.ModelData;
using SharpNeedle.Resource;

namespace HEIO.NET.External.Structs
{
    public unsafe struct CMeshDataMeshSetInfo : IConvertInternal<MeshDataMeshSetInfo>
    {
        public bool useByteColors;
        public bool enable8Weights;
        public bool enableMultiTangent;
        public CStringPointerPair materialReference;
        public uint meshSlotType;
        public char* meshSlotName;
        public int size;

        public static CMeshDataMeshSetInfo FromInternal(MeshDataMeshSetInfo info)
        {
            CMaterial* material = info.Material.IsValid() ? Allocate.AllocFrom(info.Material.Resource!, CMaterial.FromInternal) : null;

            return new()
            {
                useByteColors = info.UseByteColors,
                enable8Weights = info.Enable8Weights,
                enableMultiTangent = info.EnableMultiTangent,
                materialReference = new(info.Material.Name.AllocString(), material),
                meshSlotType = (uint)info.Slot.Type,
                meshSlotName = info.Slot.Name.AllocString(),
                size = info.Size
            };
        }

        public readonly MeshDataMeshSetInfo ToInternal()
        {
            ResourceReference<Material> material;

            if (materialReference.pointer != null)
            {
                material = ((CMaterial*)materialReference.pointer)->ToMaterial();
            }
            else
            {
                material = new(Util.ToString(materialReference.name)!);
            }

            return new(
                useByteColors,
                enable8Weights,
                enableMultiTangent,
                material,
                new((MeshType)meshSlotType, Util.ToString(meshSlotName)!),
                size
            );
        }
    }
}
