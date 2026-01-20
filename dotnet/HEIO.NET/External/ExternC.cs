using HEIO.NET.External.Structs;
using HEIO.NET.Internal;
using HEIO.NET.Internal.Modeling;
using SharpNeedle.Framework.HedgehogEngine.Bullet;
using SharpNeedle.Framework.HedgehogEngine.Mirage.MaterialData;
using SharpNeedle.IO;
using SharpNeedle.Resource;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Numerics;
using System.Runtime.InteropServices;

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
        public static CResolveInfo* ResolveInfoCombine(CResolveInfo** resolveInfos, nint resolveInfosSize)
        {
            try
            {
                ResolveInfo[] resolveInfoArray = new ResolveInfo[resolveInfosSize];
                for (int i = 0; i < resolveInfosSize; i++)
                {
                    resolveInfoArray[i] = resolveInfos[i]->ToResolveInfo();
                }

                return CResolveInfo.PointerFromInternal(ResolveInfo.Combine(resolveInfoArray));
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
                string nameString = Util.FromPointer(name)!;

                while (searchStack.TryPop(out nint currentNodeAddr))
                {
                    CSampleChunkNode* currentNode = (CSampleChunkNode*)currentNodeAddr;

                    string nodeName = Util.FromPointer(currentNode->name)!;
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
        public static CArray ImageLoadDirectoryImages(char* directory, char** images, nint imagesSize, char* streamingDirectory, CResolveInfo** resolveInfo)
        {
            try
            {
                string directoryString = Util.FromPointer(directory)!;
                string[] imagesStrings = Util.ToStringArray(images, imagesSize);
                string streamingDirectoryString = Util.FromPointer(streamingDirectory)!;

                Dictionary<string, Image> output = Image.LoadDirectoryImages(directoryString, imagesStrings, streamingDirectoryString, out ResolveInfo outInfo);

                *resolveInfo = CResolveInfo.PointerFromInternal(outInfo);

                return CStringPointerPair.FromDictionary(output, CImage.FromInternal);
            }
            catch (Exception exception)
            {
                ErrorHandler.HandleError(exception);
                return default;
            }
        }

        [UnmanagedCallersOnly(EntryPoint = "image_load_material_images")]
        public static CArray ImageLoadMaterialImages(CMaterial** materials, nint materialsSize, char* streamingDirectory, CResolveInfo** resolveInfo)
        {
            try
            {
                FileSystem system = new();

                Material[] snMaterials = new Material[materialsSize];
                IFile[] files = new IFile[materialsSize];

                for (int i = 0; i < materialsSize; i++)
                {
                    snMaterials[i] = materials[i]->ToMaterial();
                    files[i] = system.Open(Util.FromPointer(materials[i]->filePath)!)!;
                }

                string streamingDirectoryString = Util.FromPointer(streamingDirectory)!;
                Dictionary<string, Image> output = Image.LoadMaterialImages(snMaterials, files, streamingDirectoryString, out ResolveInfo outInfo);
                *resolveInfo = CResolveInfo.PointerFromInternal(outInfo);

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
                string filePathString = Util.FromPointer(filePath)!;
                Material material = new();
                material.Read(filePathString);
                return CMaterial.PointerFromInternal(material);
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
                material->ToMaterial().Write(Util.FromPointer(filepath)!);
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
        public static CArray ModelReadFiles(char** filepaths, nint filepathsSize, bool includeLoD, CMeshImportSettings* settings, CResolveInfo** resolveInfo)
        {
            try
            {
                string[] filepathsArray = Util.ToStringArray(filepaths, filepathsSize);
                MeshImportSettings internalSettings = settings->ToInternal();

                ModelSet[] modelSets = ModelSet.ReadModelFiles(filepathsArray, includeLoD, internalSettings, out ResolveInfo resultResolveInfo);

                *resolveInfo = CResolveInfo.PointerFromInternal(resultResolveInfo);

                return new(
                    Allocate.AllocFromArray(modelSets, CModelSet.FromInternal),
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
        public static CArray ModelGetMaterials(CModelSet** model_sets, nint model_sets_size)
        {
            try
            {
                List<nint> materials = [];

                for (int i = 0; i < model_sets_size; i++)
                {
                    CModelSet* model_set = model_sets[i];

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
            CModelSet** model_sets,
            nint model_sets_size,
            int versionMode,
            int topology,
            bool optimizedVertexData,
            bool multithreading,
            char* directory)
        {

        }

        #endregion


        #region Bullet Mesh

        [UnmanagedCallersOnly(EntryPoint = "bullet_mesh_read_files")]
        public static CArray BulletMeshReadFiles(char** filepaths, nint filepathsSize, CMeshImportSettings* settings)
        {
            try
            {
                string[] filepathsArray = Util.ToStringArray(filepaths, filepathsSize);
                MeshImportSettings internalSettings = settings->ToInternal();

                CollisionMeshData[] meshData = CollisionMeshData.ReadFiles(filepathsArray, internalSettings);

                nint[] results = [.. meshData.Select(x => (nint)CCollisionMeshData.PointerFromInternal(x))];
                CCollisionMeshData** result = (CCollisionMeshData**)Allocate.AllocFromArray(results);

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

        [UnmanagedCallersOnly(EntryPoint = "bullet_mesh_compile_mesh_data")]
        public static CBulletMesh* BulletMeshCompileMeshData(CCollisionMeshData** collisionMeshData, nint collisionMeshDataSize)
        {
            try
            {
                CollisionMeshData[] internalMeshData = new CollisionMeshData[collisionMeshDataSize];
                for (int i = 0; i < collisionMeshDataSize; i++)
                {
                    internalMeshData[i] = collisionMeshData[i]->ToInternal();
                }

                BulletMesh bulletMesh = CollisionMeshData.CompileBulletMesh(internalMeshData);
                return CBulletMesh.PointerFromInternal(bulletMesh);
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
                bulletMesh->ToInternal().Write(Util.FromPointer(filepath)!, false);
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
        public static CPointCloudCollection* PointCloudReadFiles(char** filepaths, nint filepathsSize, bool includeLoD, CMeshImportSettings* settings, CResolveInfo** resolveInfo)
        {
            try
            {
                string[] filepathsArray = Util.ToStringArray(filepaths, filepathsSize);
                MeshImportSettings internalSettings = settings->ToInternal();

                PointCloudCollection collection = PointCloudCollection.ReadPointClouds(filepathsArray, includeLoD, internalSettings, out ResolveInfo resultResolveInfo);

                *resolveInfo = CResolveInfo.PointerFromInternal(resultResolveInfo);

                return CPointCloudCollection.PointerFromInternal(collection);
            }
            catch (Exception exception)
            {
                ErrorHandler.HandleError(exception);
                return null;
            }
        }

        #endregion
    }
}
