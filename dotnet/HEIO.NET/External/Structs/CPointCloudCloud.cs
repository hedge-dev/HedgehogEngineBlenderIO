using HEIO.NET.Internal;
using System.Linq;

namespace HEIO.NET.External.Structs
{
    public unsafe struct CPointCloudCloud : IConvertInternal<PointCloudCollection.Cloud>
    {
        public char* name;
        public CPointCloudPoint* points;
        public nint pointsSize;

        public static CPointCloudCloud FromInternal(PointCloudCollection.Cloud cloud)
        {
            return new()
            {
                name = cloud.Name.ToPointer(),

                points = Allocate.AllocFromArray(cloud.Points, CPointCloudPoint.FromInternal),
                pointsSize = cloud.Points.Length
            };
        }

        public static CPointCloudCloud* FromInternalArray(PointCloudCollection.Cloud[] clouds)
        {
            return Allocate.AllocFromArray(clouds.Select(x => FromInternal(x)).ToArray());
        }

        public readonly PointCloudCollection.Cloud ToInternal()
        {
            return new(
                Util.FromPointer(name)!,
                Util.ToArray<CPointCloudPoint, PointCloudCollection.Point>(points, pointsSize)!
            );
        }

        public static PointCloudCollection.Cloud[] ToInternalArray(CPointCloudCloud* clouds, nint cloudsSize)
        {
            return Util.ToArray<CPointCloudCloud, PointCloudCollection.Cloud>(clouds, cloudsSize)!;
        }
    }
}
