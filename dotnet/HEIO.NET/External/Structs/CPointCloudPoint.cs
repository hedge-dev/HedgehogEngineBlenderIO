using HEIO.NET.Internal;
using System.Numerics;

namespace HEIO.NET.External.Structs
{
    public unsafe struct CPointCloudPoint : IConvertInternal<PointCloudCollection.Point>
    {
        public char* instanceName;
        public int resourceIndex;
        public Vector3 position;
        public Vector3 rotation;
        public Vector3 scale;

        public static CPointCloudPoint FromInternal(PointCloudCollection.Point point)
        {
            return new()
            {
                instanceName = point.InstanceName.AllocString(),
                resourceIndex = point.ResourceIndex,
                position = point.Position,
                rotation = point.Rotation,
                scale = point.Scale
            };
        }

        public readonly PointCloudCollection.Point ToInternal()
        {
            return new(
                Util.ToString(instanceName)!,
                resourceIndex,
                position,
                rotation,
                scale
            );
        }
    }
}
