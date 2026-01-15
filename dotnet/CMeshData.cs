using HEIO.NET.Internal;
using HEIO.NET.Internal.Modeling;
using SharpNeedle.Framework.HedgehogEngine.Mirage.ModelData;
using SharpNeedle.Framework.HedgehogEngine.Needle.Archive;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Numerics;
using System.Runtime.InteropServices;

namespace HEIO.NET
{
    public unsafe struct CUVDirection
    {
        public Vector3 tangent;
        public Vector3 binormal;

        public CUVDirection(UVDirection direction)
        {
            tangent = direction.Tangent;
            binormal = direction.Binormal;
        }
    }

    public unsafe struct CVertexWeight
    {
        public short index;
        public float weight;

        public CVertexWeight(VertexWeight vertexWeight)
        {
            index = vertexWeight.Index;
            weight = vertexWeight.Weight;
        }
    }

    public unsafe struct CVertex
    {
        public Vector3 position;
        public Vector3 normal;
        public CUVDirection uvDirection;
        public CUVDirection uvDirection2;

        public CVertexWeight* weights;
        public nint weightsSize;

        public Vector3* morphPositions;
        public nint morphPositionsSize;
    }

    public unsafe struct CMeshDataMeshSetInfo
    {
        public bool useByteColors;
        public bool enable8Weights;
        public bool enableMultiTangent;
        public CStringPointerPair materialReference;
        public uint meshSlotType;
        public char* meshSlotName;
        public int size;
    }

    public unsafe struct CMeshDataGroupInfo
    {
        public char* name;
        public int size;
    }

    public unsafe struct CMeshData
    {
        public char* name;

        public CVertex* vertices;
        public nint verticesSize;

        public nint triangleIndexCount;

        public int* triangleIndices;
        public Vector3* polygonNormals;
        public CUVDirection* polygonUVDirections;
        public CUVDirection* polygonUVDirections2;

        public Vector2** textureCoordinates;
        public nint textureCoordinatesSize;

        public Vector4** colors;
        public nint colorsSize;

        public CMeshDataMeshSetInfo* meshSets;
        public nint meshSetsSize;

        public CMeshDataGroupInfo* groups;
        public nint groupsSize;

        public char** morphNames;
        public nint morphNamesSize;

        public static CMeshData* FromMeshData(MeshData meshData)
        {
            CMeshData* result = Allocate.Alloc<CMeshData>();

            result->name = meshData.Name.ToPointer();

            result->verticesSize = meshData.Vertices.Count;
            result->vertices = Allocate.Alloc<CVertex>(result->verticesSize);

            for (int i = 0; i < result->verticesSize; i++)
            {
                Vertex vertex = meshData.Vertices[i];
                CVertex* resultVertex = &result->vertices[i];

                resultVertex->position = vertex.Position;
                resultVertex->normal = vertex.Normal;
                resultVertex->uvDirection = new(vertex.UVDirection);
                resultVertex->uvDirection2 = new(vertex.UVDirection2);

                resultVertex->weightsSize = vertex.Weights.Length;
                resultVertex->weights = Allocate.AllocFromArray(vertex.Weights.Select(x => new CVertexWeight(x)).ToArray());

                resultVertex->morphPositionsSize = vertex.MorphPositions?.Length ?? 0;
                resultVertex->morphPositions = Allocate.AllocFromArray(vertex.MorphPositions);
            }

            result->triangleIndexCount = meshData.TriangleIndices.Count;

            result->triangleIndices = Allocate.AllocFromArray(meshData.TriangleIndices);
            result->polygonNormals = Allocate.AllocFromArray(meshData.PolygonNormals);
            result->polygonUVDirections = Allocate.AllocFromArray(meshData.PolygonUVDirections?.Select(x => new CUVDirection(x)).ToArray());
            result->polygonUVDirections2 = Allocate.AllocFromArray(meshData.PolygonUVDirections2?.Select(x => new CUVDirection(x)).ToArray());

            result->textureCoordinatesSize = meshData.TextureCoordinates.Count;
            Allocate.AllocFrom2DArray(meshData.TextureCoordinates, out result->textureCoordinates);

            result->colorsSize = meshData.Colors.Count;
            Allocate.AllocFrom2DArray(meshData.Colors, out result->colors);

            result->meshSetsSize = meshData.MeshSets.Count;
            result->meshSets = Allocate.Alloc<CMeshDataMeshSetInfo>(result->meshSetsSize);

            for (int i = 0; i < result->meshSetsSize; i++)
            {
                MeshDataSetInfo meshSet = meshData.MeshSets[i];
                CMeshDataMeshSetInfo* resultMeshSet = &result->meshSets[i];

                CMaterial* material = meshSet.Material.IsValid() ? CMaterial.FromMaterial(meshSet.Material.Resource!) : null;

                resultMeshSet->useByteColors = meshSet.UseByteColors;
                resultMeshSet->enable8Weights = meshSet.Enable8Weights;
                resultMeshSet->enableMultiTangent = meshSet.EnableMultiTangent;
                resultMeshSet->materialReference = new(meshSet.Material.Name.ToPointer(), material);
                resultMeshSet->meshSlotType = (uint)meshSet.Slot.Type;
                resultMeshSet->meshSlotName = meshSet.Slot.Name.ToPointer();
                resultMeshSet->size = meshSet.Size;
            }

            result->groupsSize = meshData.Groups.Count;
            result->groups = Allocate.Alloc<CMeshDataGroupInfo>(result->groupsSize);

            for (int i = 0; i < result->groupsSize; i++)
            {
                MeshDataGroupInfo group = meshData.Groups[i];
                CMeshDataGroupInfo* resultGroup = &result->groups[i];

                resultGroup->name = group.Name.ToPointer();
                resultGroup->size = group.Size;
            }

            result->morphNamesSize = meshData.MorphNames?.Count ?? 0;
            result->morphNames = meshData.MorphNames != null ? Allocate.FromStringArray([.. meshData.MorphNames]) : null;

            return result;
        }

    }

    public unsafe struct CModelNode
    {
        public char* name;
        public int parentIndex;
        public Matrix4x4 transform;
    }

    public unsafe struct CMeshDataSet
    {
        public char* name;
        public bool isTerrain;

        public CMeshData** meshData;
        public nint meshDataSize;

        public CModelNode* nodes;
        public nint nodesSize;

        public CSampleChunkNode* sampleChunkNodeRoot;
    }

    public unsafe struct CLODItem
    {
        public int cascadeFlag;
        public float unknown2;
        public byte cascadeLevel;

        public CLODItem(LODInfoBlock.LODItem item)
        {
            cascadeFlag = item.CascadeFlag;
            unknown2 = item.Unknown2;
            cascadeLevel = item.CascadeLevel;
        }
    }

    public unsafe struct CModelSet
    {
        public CMeshDataSet* meshDataSets;
        public nint meshDataSetsSize;

        public CLODItem* lodItems;
        public nint lodItemsSize;
        public byte lodUnknown1;


        public static CModelSet* FromModelSet(ModelSet modelSet)
        {
            CModelSet* result = Allocate.Alloc<CModelSet>();

            result->meshDataSetsSize = modelSet.MeshDataSets.Length;
            result->meshDataSets = Allocate.Alloc<CMeshDataSet>(result->meshDataSetsSize);

            for (int i = 0; i < result->meshDataSetsSize; i++)
            {
                MeshDataSet set = modelSet.MeshDataSets[i];
                CMeshDataSet* resultSet = &result->meshDataSets[i];

                resultSet->name = set.Name.ToPointer();
                resultSet->isTerrain = typeof(TerrainModel).IsAssignableFrom(set.OriginalType);
                resultSet->meshData = (CMeshData**)Allocate.AllocFromArray(set.MeshData.Select(x => (nint)CMeshData.FromMeshData(x)).ToArray());
                resultSet->meshDataSize = set.MeshData.Length;

                CModelNode[]? modelNodes = set.Nodes?.Select(
                    x => new CModelNode()
                    {
                        name = x.Name.ToPointer(),
                        parentIndex = x.ParentIndex,
                        transform = x.Transform
                    }
                ).ToArray();

                resultSet->nodesSize = modelNodes?.Length ?? 0;
                resultSet->nodes = Allocate.AllocFromArray(modelNodes);

                resultSet->sampleChunkNodeRoot = CSampleChunkNode.FromSampleChunkNodeTree(set.SampleChunkNodeRoot);
            }

            CLODItem[]? resultLODItems = modelSet.LODInfo?.Items.Select(x => new CLODItem(x)).ToArray();
            result->lodItems = Allocate.AllocFromArray(resultLODItems);
            result->lodItemsSize = resultLODItems?.Length ?? 0;
            result->lodUnknown1 = modelSet.LODInfo?.Unknown1 ?? 0;

            return result;
        }

        [UnmanagedCallersOnly(EntryPoint = "model_read_files")]
        public static CArray ReadModelFiles(char** filepaths, nint filepathsSize, bool includeLoD, CMeshImportSettings* settings, CResolveInfo** resolveInfo)
        {
            try
            {
                string[] filepathsArray = Util.ToStringArray(filepaths, filepathsSize);
                MeshImportSettings internalSettings = settings->ToMeshImportSettings();

                ModelSet[] modelSets = ModelSet.ReadModelFiles(filepathsArray, includeLoD, internalSettings, out ResolveInfo resultResolveInfo);

                *resolveInfo = CResolveInfo.FromResolveInfo(resultResolveInfo);

                nint[] results = [.. modelSets.Select(x => (nint)FromModelSet(x))];
                CModelSet** result = (CModelSet**)Allocate.AllocFromArray(results);

                return new(
                    result,
                    results.Length
                );
            }
            catch (Exception exception)
            {
                ErrorHandler.HandleError(exception);
                return default;
            }
        }

        [UnmanagedCallersOnly(EntryPoint = "model_get_materials")]
        public static CArray GetMaterials(CModelSet** model_sets, nint model_sets_size)
        {
            try
            {
                List<nint> materials = [];

                for (int i = 0; i < model_sets_size; i++)
                {
                    CModelSet* model_set = model_sets[i];

                    for (int j = 0; j < model_set->meshDataSetsSize; j++)
                    {
                        CMeshDataSet* mesh_data_set = &model_set->meshDataSets[j];

                        for (int k = 0; k < mesh_data_set->meshDataSize; k++)
                        {
                            CMeshData* mesh_data = mesh_data_set->meshData[k];

                            for (int l = 0; l < mesh_data->meshSetsSize; l++)
                            {
                                CStringPointerPair materialReference = mesh_data->meshSets[l].materialReference;
                                if (materialReference.pointer != null)
                                {
                                    materials.Add((nint)materialReference.pointer);
                                }
                            }
                        }
                    }
                }

                return new(Allocate.AllocFromArray(materials), materials.Count);
            }
            catch (Exception exception)
            {
                ErrorHandler.HandleError(exception);
                return default;
            }
        }
    }
}
