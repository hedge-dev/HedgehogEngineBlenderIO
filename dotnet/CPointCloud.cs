using HEIO.NET.Internal;
using HEIO.NET.Internal.Modeling;
using SharpNeedle.Framework.HedgehogEngine.Bullet;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Numerics;
using System.Text;

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
        public nint collisionMeshCoudssSize;

        public CPointCloudCollection* FromPointCloudCollection(PointCloudCollection collection)
        {
            CPointCloudCollection* result = Allocate.Alloc<CPointCloudCollection>();

            result->models = (CModelSet**)Allocate.AllocFromArray(collection.Models.Select(x => (nint)CModelSet.FromModelSet(x)).ToArray());
            result->modelsSize = collection.Models.Length;

            result->collisionMeshes = (CCollisionMeshData**)Allocate.AllocFromArray(collection.Models.Select(x => (nint)CModelSet.FromModelSet(x)).ToArray());
            result->collisionMeshesSize = collection.CollisionMeshes.Length;

            return result;
        }
    }
}
