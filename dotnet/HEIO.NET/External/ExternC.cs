using HEIO.NET.External.Structs;
using HEIO.NET.Internal;
using HEIO.NET.Internal.Json;
using HEIO.NET.Internal.Modeling;
using SharpNeedle.Framework.HedgehogEngine.Bullet;
using SharpNeedle.Framework.HedgehogEngine.Mirage.MaterialData;
using SharpNeedle.Framework.HedgehogEngine.Mirage.ModelData;
using SharpNeedle.Framework.HedgehogEngine.Needle.Archive;
using SharpNeedle.IO;
using SharpNeedle.Resource;
using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Numerics;
using System.Runtime.InteropServices;
using System.Text.Json;

namespace HEIO.NET.External
{
    public static unsafe class ExternC
    {
        #region Matrix

        [UnmanagedCallersOnly(EntryPoint = "matrix_multiply")]
        public static Matrix4x4 MatrixMultiply(Matrix4x4 a, Matrix4x4 b)
        {
            try
            {
                return a * b;
            }
            catch (Exception exception)
            {
                ErrorHandler.HandleError(exception);
                return default;
            }
        }

        [UnmanagedCallersOnly(EntryPoint = "matrix_invert")]
        public static bool MatrixInvert(Matrix4x4* matrix)
        {
            try
            {
                bool result = Matrix4x4.Invert(*matrix, out Matrix4x4 invertedMatrx);
                *matrix = result ? invertedMatrx : Matrix4x4.Identity;
                return result;
            }
            catch (Exception exception)
            {
                ErrorHandler.HandleError(exception);
                return default;
            }
        }

        [UnmanagedCallersOnly(EntryPoint = "matrix_create_translation")]
        public static Matrix4x4 MatrixCreateTranslation(Vector3 position)
        {
            try
            {
                return Matrix4x4.CreateTranslation(position);
            }
            catch (Exception exception)
            {
                ErrorHandler.HandleError(exception);
                return default;
            }
        }

        [UnmanagedCallersOnly(EntryPoint = "matrix_create_rotation")]
        public static Matrix4x4 MatrixCreateRotation(Vector3 eulerRotation)
        {
            try
            {
                float sX = MathF.Sin(eulerRotation.X);
                float cX = MathF.Cos(eulerRotation.X);

                float sY = MathF.Sin(eulerRotation.Y);
                float cY = MathF.Cos(eulerRotation.Y);

                float sZ = MathF.Sin(eulerRotation.Z);
                float cZ = MathF.Cos(eulerRotation.Z);

                // equal to matX * matY * matZ
                return new()
                {
                    M11 = cZ * cY,
                    M12 = sZ * cY,
                    M13 = -sY,

                    M21 = (cZ * sY * sX) - (sZ * cX),
                    M22 = (sZ * sY * sX) + (cZ * cX),
                    M23 = cY * sX,

                    M31 = (cZ * sY * cX) + (sZ * sX),
                    M32 = (sZ * sY * cX) - (cZ * sX),
                    M33 = cY * cX,

                    M44 = 1
                };
            }
            catch (Exception exception)
            {
                ErrorHandler.HandleError(exception);
                return default;
            }
        }

        [UnmanagedCallersOnly(EntryPoint = "matrix_create_from_quaternion")]
        public static Matrix4x4 MatrixCreateFromQuaternion(Quaternion quaternion)
        {
            try
            {
                return Matrix4x4.CreateFromQuaternion(quaternion);
            }
            catch (Exception exception)
            {
                ErrorHandler.HandleError(exception);
                return default;
            }
        }

        [UnmanagedCallersOnly(EntryPoint = "matrix_create_scale")]
        public static Matrix4x4 MatrixCreateScale(Vector3 scale)
        {
            try
            {
                return Matrix4x4.CreateScale(scale);
            }
            catch (Exception exception)
            {
                ErrorHandler.HandleError(exception);
                return default;
            }
        }

        [UnmanagedCallersOnly(EntryPoint = "matrix_decompose")]
        public static void MatrixDecompose(Matrix4x4 matrix, Vector3* position, Quaternion* rotation, Vector3* scale)
        {
            try
            {
                Matrix4x4.Decompose(matrix, out *scale, out *rotation, out *position);
            }
            catch (Exception exception)
            {
                ErrorHandler.HandleError(exception);
                return;
            }
        }

        [UnmanagedCallersOnly(EntryPoint = "matrix_to_euler")]
        public static Vector3 MatrixToEuler(Matrix4x4 matrix)
        {
            try
            {
                const double threshold = 16 * 1.192092896e-07;
                double cy = double.Hypot(matrix.M11, matrix.M12);

                if (cy > threshold)
                {
                    return new(
                        MathF.Atan2(matrix.M23, matrix.M33),
                        MathF.Atan2(-matrix.M13, (float)cy),
                        MathF.Atan2(matrix.M12, matrix.M11)
                    );

                }
                else
                {
                    return new(
                        MathF.Atan2(-matrix.M32, matrix.M22),
                        MathF.Atan2(-matrix.M13, (float)cy),
                        0f
                    );
                }
            }
            catch (Exception exception)
            {
                ErrorHandler.HandleError(exception);
                return default;
            }
        }

        #endregion


        #region Quaternion

        [UnmanagedCallersOnly(EntryPoint = "quaternion_create_from_rotation_matrix")]
        public static Quaternion QuaternionCreateFromRotationMatrix(Matrix4x4 matrix)
        {
            try
            {
                return Quaternion.CreateFromRotationMatrix(matrix);
            }
            catch (Exception exception)
            {
                ErrorHandler.HandleError(exception);
                return default;
            }
        }

        #endregion


        #region Resolve Info

        [UnmanagedCallersOnly(EntryPoint = "resolve_info_combine")]
        public static CResolveInfo* ResolveInfoCombine(CResolveInfo** resolveInfos, int resolveInfosSize)
        {
            try
            {
                ResolveInfo[] resolveInfoArray = new ResolveInfo[resolveInfosSize];
                for (int i = 0; i < resolveInfosSize; i++)
                {
                    resolveInfoArray[i] = resolveInfos[i]->ToResolveInfo();
                }

                return Allocate.AllocFrom(ResolveInfo.Combine(resolveInfoArray), CResolveInfo.FromInternal);
            }
            catch (Exception exception)
            {
                ErrorHandler.HandleError(exception);
                return null;
            }
        }

        #endregion


        #region Sample Chunk Node

        [UnmanagedCallersOnly(EntryPoint = "sample_chunk_node_find")]
        public static CSampleChunkNode* SampleChunkNodeFind(CSampleChunkNode* node, char* name)
        {
            try
            {
                Stack<nint> searchStack = [];
                searchStack.Push((nint)node);
                string nameString = Util.ToString(name)!;

                while (searchStack.TryPop(out nint currentNodeAddr))
                {
                    CSampleChunkNode* currentNode = (CSampleChunkNode*)currentNodeAddr;

                    string nodeName = Util.ToString(currentNode->name)!;
                    if (nodeName == nameString)
                    {
                        return currentNode;
                    }

                    if (currentNode->sibling != null)
                    {
                        searchStack.Push((nint)currentNode->sibling);
                    }

                    if (currentNode->child != null)
                    {
                        searchStack.Push((nint)currentNode->child);
                    }
                }

                return null;
            }
            catch (Exception exception)
            {
                ErrorHandler.HandleError(exception);
                return null;
            }
        }

        #endregion


        #region Image

        [UnmanagedCallersOnly(EntryPoint = "image_load_directory_images")]
        public static CArray ImageLoadDirectoryImages(char* directory, char** images, int imagesSize, char* streamingDirectory, CResolveInfo** resolveInfo)
        {
            try
            {
                string directoryString = Util.ToString(directory)!;
                string[] imagesStrings = Util.ToStringArray(images, imagesSize)!;
                string streamingDirectoryString = Util.ToString(streamingDirectory)!;

                Dictionary<string, Image> output = Image.LoadDirectoryImages(directoryString, imagesStrings, streamingDirectoryString, out ResolveInfo outInfo);

                *resolveInfo = Allocate.AllocFrom(outInfo, CResolveInfo.FromInternal);

                return CStringPointerPair.FromDictionary(output, CImage.FromInternal);
            }
            catch (Exception exception)
            {
                ErrorHandler.HandleError(exception);
                return default;
            }
        }

        [UnmanagedCallersOnly(EntryPoint = "image_load_material_images")]
        public static CArray ImageLoadMaterialImages(CMaterial** materials, int materialsSize, char* streamingDirectory, CResolveInfo** resolveInfo)
        {
            try
            {
                FileSystem system = new();

                Material[] snMaterials = new Material[materialsSize];
                IFile[] files = new IFile[materialsSize];

                for (int i = 0; i < materialsSize; i++)
                {
                    snMaterials[i] = materials[i]->ToMaterial();
                    files[i] = system.Open(Util.ToString(materials[i]->filePath)!)!;
                }

                string streamingDirectoryString = Util.ToString(streamingDirectory)!;
                Dictionary<string, Image> output = Image.LoadMaterialImages(snMaterials, files, streamingDirectoryString, out ResolveInfo outInfo);
                *resolveInfo = Allocate.AllocFrom(outInfo, CResolveInfo.FromInternal);

                return CStringPointerPair.FromDictionary(output, CImage.FromInternal);
            }
            catch (Exception exception)
            {
                ErrorHandler.HandleError(exception);
                return default;
            }

        }

        [UnmanagedCallersOnly(EntryPoint = "image_invert_green_channel")]
        public static void ImageInvertGreenChannel(float* pixels, int pixelsSize)
        {
            try
            {
                Image.InvertGreenChannel(pixels, pixelsSize);
            }
            catch (Exception exception)
            {
                ErrorHandler.HandleError(exception);
                return;
            }
        }

        #endregion


        #region Material

        [UnmanagedCallersOnly(EntryPoint = "material_read_file")]
        public static CMaterial* MaterialReadFile(char* filePath)
        {
            try
            {
                string filePathString = Util.ToString(filePath)!;
                Material material = new();
                material.Read(filePathString);
                return Allocate.AllocFrom(material, CMaterial.FromInternal);
            }
            catch (Exception exception)
            {
                ErrorHandler.HandleError(exception);
                return null;
            }
        }

        [UnmanagedCallersOnly(EntryPoint = "material_write_file")]
        public static void MaterialWriteFile(CMaterial* material, char* filepath)
        {
            try
            {
                material->ToMaterial().Write(Util.ToString(filepath)!);
            }
            catch (Exception exception)
            {
                ErrorHandler.HandleError(exception);
                return;
            }
        }

        #endregion


        #region Model

        [UnmanagedCallersOnly(EntryPoint = "model_read_files")]
        public static CArray ModelReadFiles(char** filepaths, int filepathsSize, bool includeLoD, CMeshImportSettings* settings, CResolveInfo** resolveInfo)
        {
            try
            {
                string[] filepathsArray = Util.ToStringArray(filepaths, filepathsSize)!;
                MeshImportSettings internalSettings = settings->ToInternal();

                ModelSet[] modelSets = ModelSet.ReadModelFiles(filepathsArray, includeLoD, internalSettings, out ResolveInfo resultResolveInfo);

                CModelSet** result = Allocate.AllocPointersFromArray(modelSets, CModelSet.FromInternal);

                *resolveInfo = Allocate.AllocFrom(resultResolveInfo, CResolveInfo.FromInternal);

                return new(
                    result,
                    modelSets.Length
                );
            }
            catch (Exception exception)
            {
                ErrorHandler.HandleError(exception);
                return default;
            }
        }

        [UnmanagedCallersOnly(EntryPoint = "model_get_materials")]
        public static CArray ModelGetMaterials(CModelSet** modelSets, int modelSetsSize)
        {
            try
            {
                List<nint> materials = [];

                for (int i = 0; i < modelSetsSize; i++)
                {
                    CModelSet* model_set = modelSets[i];

                    for (int j = 0; j < model_set->meshDataSetsSize; j++)
                    {
                        CMeshDataSet* mesh_data_set = model_set->meshDataSets[j];

                        for (int k = 0; k < mesh_data_set->meshDataSize; k++)
                        {
                            CMeshData* mesh_data = &mesh_data_set->meshData[k];

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

        [UnmanagedCallersOnly(EntryPoint = "model_compile_to_files")]
        public static void ModelCompileToFiles(
            CModelSet** modelSets,
            int modelSetsSize,
            int versionMode,
            int topology,
            bool optimizedVertexData,
            bool multithreading,
            char* directory)
        {
            try
            {
                string outputDirectory = Util.ToString(directory)!;

                Dictionary<nint, MeshDataSet> meshDataSets = [];

                for (int i = 0; i < modelSetsSize; i++)
                {
                    CModelSet* modelSet = modelSets[i];
                    for (int j = 0; j < modelSet->meshDataSetsSize; j++)
                    {
                        CMeshDataSet* meshDataSet = modelSet->meshDataSets[j];
                        if (!meshDataSets.ContainsKey((nint)meshDataSet))
                        {
                            MeshDataSet internalMeshDataSet = meshDataSet->ToInternal();

                            string json = JsonSerializer.Serialize(internalMeshDataSet, SourceGenerationContext.Default.MeshDataSet);
                            File.WriteAllText(Path.Combine(outputDirectory, $"{meshDataSets.Count}_{internalMeshDataSet.Name}.json"), json);

                            meshDataSets.Add((nint)meshDataSet, internalMeshDataSet);
                        }
                    }
                }

                KeyValuePair<nint, MeshDataSet>[] meshDataSetsToConvert = meshDataSets.ToArray();

                ModelBase[] models = MeshDataSet.CompileMeshData(
                    [.. meshDataSetsToConvert.Select(x => x.Value)],
                    (ModelVersionMode)versionMode,
                    (Topology)topology,
                    optimizedVertexData,
                    multithreading
                );

                Dictionary<nint, ModelBase> modelDictionary = meshDataSetsToConvert.Select((x, i) => new KeyValuePair<nint, ModelBase>(x.Key, models[i])).ToDictionary();

                for(int i = 0; i < modelSetsSize; i++)
                {
                    CModelSet* modelSet = modelSets[i];
                    ResourceBase fileData;
                    ModelBase mainModel = modelDictionary[(nint)modelSet->meshDataSets[0]];

                    if (modelSet->lodItemsSize > 0)
                    {
                        NeedleArchive archive = new()
                        {
                            OffsetMode = NeedleArchiveDataOffsetMode.SelfRelative,
                            DataBlocks = [ modelSet->LODInfoToInternal()! ]
                        };

                        for(int j = 0; j < modelSet->meshDataSetsSize; j++)
                        {
                            archive.DataBlocks.Add(
                                new ModelBlock() 
                                { 
                                    Resource = modelDictionary[(nint)modelSet->meshDataSets[j]] 
                                }
                            );
                        }

                        fileData = archive;
                    }
                    else
                    {
                        fileData = mainModel;
                    }

                    string extension;
                    if(mainModel is TerrainModel)
                    {
                        extension = ".terrain-model";
                    }
                    else
                    {
                        extension = ".model";
                    }

                    string filepath = Path.Join(outputDirectory, mainModel.Name + extension);
                    fileData.Write(filepath);
                }
            }
            catch (Exception exception)
            {
                ErrorHandler.HandleError(exception);
                return;
            }
        }

        #endregion


        #region Bullet Mesh

        [UnmanagedCallersOnly(EntryPoint = "bullet_mesh_read_files")]
        public static CArray BulletMeshReadFiles(char** filepaths, int filepathsSize, CMeshImportSettings* settings)
        {
            try
            {
                string[] filepathsArray = Util.ToStringArray(filepaths, filepathsSize)!;
                MeshImportSettings internalSettings = settings->ToInternal();

                CollisionMeshData[] meshData = CollisionMeshData.ReadFiles(filepathsArray, internalSettings);

                CCollisionMeshData** result = Allocate.AllocPointersFromArray(meshData, CCollisionMeshData.FromInternal);

                return new(
                    result,
                    meshData.Length
                );
            }
            catch (Exception exception)
            {
                ErrorHandler.HandleError(exception);
                return default;
            }
        }

        [UnmanagedCallersOnly(EntryPoint = "bullet_mesh_compile_mesh_data")]
        public static CBulletMesh* BulletMeshCompileMeshData(CCollisionMeshData** collisionMeshData, int collisionMeshDataSize)
        {
            try
            {
                CollisionMeshData[] internalMeshData = new CollisionMeshData[collisionMeshDataSize];
                for (int i = 0; i < collisionMeshDataSize; i++)
                {
                    internalMeshData[i] = collisionMeshData[i]->ToInternal();
                }

                BulletMesh bulletMesh = CollisionMeshData.CompileBulletMesh(internalMeshData);
                return Allocate.AllocFrom(bulletMesh, CBulletMesh.FromInternal);
            }
            catch (Exception exception)
            {
                ErrorHandler.HandleError(exception);
                return null;
            }
        }

        [UnmanagedCallersOnly(EntryPoint = "bullet_mesh_write_to_file")]
        public static void BulletMeshWriteToFile(CBulletMesh* bulletMesh, char* filepath)
        {
            try
            {
                bulletMesh->ToInternal().Write(Util.ToString(filepath)!, false);
            }
            catch (Exception exception)
            {
                ErrorHandler.HandleError(exception);
                return;
            }
        }

        #endregion


        #region Point cloud

        [UnmanagedCallersOnly(EntryPoint = "point_cloud_read_files")]
        public static CPointCloudCollection* PointCloudReadFiles(char** filepaths, int filepathsSize, bool includeLoD, CMeshImportSettings* settings, CResolveInfo** resolveInfo)
        {
            try
            {
                string[] filepathsArray = Util.ToStringArray(filepaths, filepathsSize)!;
                MeshImportSettings internalSettings = settings->ToInternal();

                PointCloudCollection collection = PointCloudCollection.ReadPointClouds(filepathsArray, includeLoD, internalSettings, out ResolveInfo resultResolveInfo);

                *resolveInfo = Allocate.AllocFrom(resultResolveInfo, CResolveInfo.FromInternal);

                return Allocate.AllocFrom(collection, CPointCloudCollection.FromInternal);
            }
            catch (Exception exception)
            {
                ErrorHandler.HandleError(exception);
                return null;
            }
        }

        [UnmanagedCallersOnly(EntryPoint = "point_cloud_write_file")]
        public static void PointCloudWriteFile(CPointCloudCloud* cloud, char** resourceNames, int resourceNamesSize, uint formatVersion, char* filepath)
        {
            try
            {
                string[] resourceNamesArray = Util.ToStringArray(resourceNames, resourceNamesSize)!;

                PointCloudCollection.WritePointCloudToFile(
                    cloud->ToInternal(),
                    resourceNamesArray,
                    formatVersion,
                    Util.ToString(filepath)!
                );
            }
            catch (Exception exception)
            {
                ErrorHandler.HandleError(exception);
                return;
            }
        }

        #endregion
    }
}
