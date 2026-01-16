using HEIO.NET.Internal;
using HEIO.NET.Internal.Modeling;
using System;
using System.Linq;
using System.Numerics;
using System.Runtime.InteropServices;

namespace HEIO.NET
{
    public unsafe struct CPointCloudPoint
    {
        public char* instanceName;
        public int resourceIndex;
        public Vector3 position;
        public Vector3 rotation;
        public Vector3 scale;
    }

    public unsafe struct CPointCloudCloud
    {
        public char* name;
        public CPointCloudPoint* points;
        public nint pointsSize;

        public static CPointCloudCloud* FromClouds(PointCloudCollection.Cloud[] clouds)
        {
            CPointCloudCloud* result = Allocate.Alloc<CPointCloudCloud>(clouds.Length);

            for(int i = 0; i < clouds.Length; i++)
            {
                PointCloudCollection.Cloud cloud = clouds[i];
                CPointCloudCloud* resultCloud = &result[i];

                resultCloud->name = cloud.Name.ToPointer();

                resultCloud->pointsSize = cloud.Points.Length;
                resultCloud->points = Allocate.Alloc<CPointCloudPoint>(resultCloud->pointsSize);

                for (int j = 0; j < resultCloud->pointsSize; j++)
                {
                    PointCloudCollection.Point point = cloud.Points[j];
                    CPointCloudPoint* resultPoint = &resultCloud->points[j];

                    resultPoint->instanceName = point.InstanceName.ToPointer();
                    resultPoint->resourceIndex = point.ResourceIndex;
                    resultPoint->position = point.Position;
                    resultPoint->rotation = point.Rotation;
                    resultPoint->scale = point.Scale;
                }
            }

            return result;
        }
    }

    public unsafe struct CPointCloudCollection
    {
        public CModelSet** models;
        public nint modelsSize;

        public CPointCloudCloud* modelClouds;
        public nint modelCloudsSize;

        public CCollisionMeshData** collisionMeshes;
        public nint collisionMeshesSize;

        public CPointCloudCloud* collisionMeshClouds;
        public nint collisionMeshCloudsSize;

        public static CPointCloudCollection* FromPointCloudCollection(PointCloudCollection collection)
        {
            CPointCloudCollection* result = Allocate.Alloc<CPointCloudCollection>();

            result->models = (CModelSet**)Allocate.AllocFromArray(collection.Models.Select(x => (nint)CModelSet.FromModelSet(x)).ToArray());
            result->modelsSize = collection.Models.Length;

            result->modelClouds = CPointCloudCloud.FromClouds(collection.ModelClouds);
            result->modelCloudsSize = collection.ModelClouds.Length;

            result->collisionMeshes = (CCollisionMeshData**)Allocate.AllocFromArray(collection.Models.Select(x => (nint)CModelSet.FromModelSet(x)).ToArray());
            result->collisionMeshesSize = collection.CollisionMeshes.Length;

            result->collisionMeshClouds = CPointCloudCloud.FromClouds(collection.CollisionMeshClouds);
            result->collisionMeshCloudsSize = collection.CollisionMeshClouds.Length;

            return result;
        }

        [UnmanagedCallersOnly(EntryPoint = "point_cloud_read_files")]
        public static CPointCloudCollection* ReadPointCloudFiles(char** filepaths, nint filepathsSize, bool includeLoD, CMeshImportSettings* settings, CResolveInfo** resolveInfo)
        {
            try
            {
                string[] filepathsArray = Util.ToStringArray(filepaths, filepathsSize);
                MeshImportSettings internalSettings = settings->ToMeshImportSettings();

                PointCloudCollection collection = PointCloudCollection.ReadPointClouds(filepathsArray, includeLoD, internalSettings, out ResolveInfo resultResolveInfo);

                *resolveInfo = CResolveInfo.FromResolveInfo(resultResolveInfo);

                return FromPointCloudCollection(collection);
            }
            catch (Exception exception)
            {
                ErrorHandler.HandleError(exception);
                return null;
            }
        }
    }
}
