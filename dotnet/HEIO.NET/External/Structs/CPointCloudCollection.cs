using HEIO.NET.Internal;
using HEIO.NET.Internal.Modeling;

namespace HEIO.NET.External.Structs
{
    public unsafe struct CPointCloudCollection : IConvertInternal<PointCloudCollection>
    {
        public CModelSet** models;
        public int modelsSize;

        public CPointCloudCloud* modelClouds;
        public int modelCloudsSize;

        public CCollisionMeshData** collisionMeshes;
        public int collisionMeshesSize;

        public CPointCloudCloud* collisionMeshClouds;
        public int collisionMeshCloudsSize;

        public static CPointCloudCollection FromInternal(PointCloudCollection collection)
        {
            return new()
            {
                models = Allocate.AllocPointersFromArray(collection.Models, CModelSet.FromInternal),
                modelsSize = collection.Models.Length,

                modelClouds = CPointCloudCloud.FromInternalArray(collection.ModelClouds),
                modelCloudsSize = collection.ModelClouds.Length,

                collisionMeshes = Allocate.AllocPointersFromArray(collection.CollisionMeshes, CCollisionMeshData.FromInternal),
                collisionMeshesSize = collection.CollisionMeshes.Length,

                collisionMeshClouds = CPointCloudCloud.FromInternalArray(collection.CollisionMeshClouds),
                collisionMeshCloudsSize = collection.CollisionMeshClouds.Length
            };
        }

        public readonly PointCloudCollection ToInternal()
        {
            return new(
                Util.PointersToArray<CModelSet, ModelSet>(models, modelsSize) ?? [],
                CPointCloudCloud.ToInternalArray(modelClouds, modelsSize),
                Util.PointersToArray<CCollisionMeshData, CollisionMeshData>(collisionMeshes, collisionMeshesSize) ?? [],
                CPointCloudCloud.ToInternalArray(collisionMeshClouds, collisionMeshCloudsSize)
            );
        }
    }
}
