using CaseConverter;
using System.Reflection;
using System.Security.Cryptography.X509Certificates;
using System.Text;

namespace HEIO.NET.Util
{
    internal class Program
    {
        private static readonly Dictionary<string, (string type, string hint)> _pythonTypeLookup = new()
        {
            { "System.Char*", ("ctypes.c_wchar_p", "str") },
            { "System.Void*", ("ctypes.c_void_p", "ctypes.c_void_p") },
            { "System.IntPtr", ("ctypes.c_size_t", "int") },
            { "System.Byte", ("ctypes.c_ubyte", "int") },
            { "System.Int16", ("ctypes.c_short", "int") },
            { "System.UInt16", ("ctypes.c_ushort", "int") },
            { "System.Int32", ("ctypes.c_int", "int") },
            { "System.UInt32", ("ctypes.c_uint", "int") },
            { "System.Int64", ("ctypes.c_longlong", "int") },
            { "System.UInt64", ("ctypes.c_ulonglong", "int") },
            { "System.Single", ("ctypes.c_float", "float") },
            { "System.Boolean", ("ctypes.c_bool", "bool") },

            { "System.Numerics.Vector2", ("nettypes.CVector2", "nettypes.CVector2") },
            { "System.Numerics.Vector3", ("nettypes.CVector3", "nettypes.CVector3") },
            { "System.Numerics.Vector4", ("nettypes.CVector4", "nettypes.CVector4") },
            { "System.Numerics.Quaternion", ("nettypes.CQuaternion", "nettypes.CQuaternion") },
            { "System.Numerics.Matrix4x4", ("nettypes.CMatrix", "nettypes.CMatrix") },
            { "SharpNeedle.Structs.Vector4Int", ("nettypes.Vector4Int", "nettypes.Vector4Int") },
        };

        static void Main(string[] args)
        {
            GeneratePythonStructs();
        }

        private static string TypeToFileName(string typeName)
        {
            return typeName[1..].ToSnakeCase();
        }

        public static void GeneratePythonStructs()
        {
            const string nameSpace = "HEIO.NET.External.Structs";

            Type[] types = [.. 
                Assembly.GetAssembly(typeof(External.ExternC))!
                .GetTypes()
                .Where(x => x.IsValueType && x.Namespace == nameSpace)
            ];

            // Gonna assume that this is always executed somewhere in the "bin" folder inside the project folder
            string currentDirectory = Directory.GetCurrentDirectory();

            string dotnetDirectory = currentDirectory;
            while(Path.GetFileName(dotnetDirectory) != "dotnet")
            {
                dotnetDirectory = Path.GetDirectoryName(dotnetDirectory)!;
            }

            string repoDirectory = Path.GetDirectoryName(dotnetDirectory)!;
            string outputDirectory = Path.Join(repoDirectory, "blender", "source", "external", "structs");

            if(!Directory.Exists(outputDirectory))
            {
                Directory.CreateDirectory(outputDirectory);
            }

            StringBuilder initBuilder = new();

            HashSet<string> heioTypeNames = [.. types.Select(x => x.FullName!)];

            foreach (Type type in types)
            {
                StringBuilder builder = new();
                builder.AppendLine("# !!! GENERATED USING HEIO.NET.Utils !!!");
                builder.AppendLine("# Please do not touch manually!");

                builder.AppendLine("import ctypes");
                builder.AppendLine("from .. import nettypes");
                builder.AppendLine("from ..typing import TPointer");

                HashSet<string> usedHEIOTypes = [];
                List<(string name, string type, string hint)> fields = [];

                foreach (FieldInfo field in type.GetFields())
                {
                    int pointerLevel = 0;
                    string? pythonType = null;
                    string? pythonHint = null;

                    string typeName = field.FieldType.FullName!;
                    while(true)
                    {
                        if(heioTypeNames.Contains(typeName))
                        {
                            pythonType = field.FieldType.Name[..^pointerLevel];
                            pythonHint = field.FieldType.Name[..^pointerLevel];
                            usedHEIOTypes.Add(typeName);
                            break;
                        }

                        if(_pythonTypeLookup.TryGetValue(typeName, out (string type, string hint) pyType))
                        {
                            pythonType = pyType.type;
                            pythonHint = pyType.hint;
                            break;
                        }

                        if(typeName.EndsWith('*'))
                        {
                            pointerLevel++;
                            typeName = typeName[..^1];
                        }
                        else
                        {
                            break;
                        }
                    }

                    if(pythonType == null || pythonHint == null)
                    {
                        throw new InvalidOperationException($"Could not determine python field type for {type.Name}.{field.Name}: {field.FieldType.FullName}");
                    }

                    for(int i = 0; i < pointerLevel; i++)
                    {
                        pythonType = $"ctypes.POINTER({pythonType})";

                        if(i == 0)
                        {
                            pythonHint = $"TPointer['{pythonHint}']";
                        }
                        else
                        {
                            pythonHint = $"TPointer[{pythonHint}]";
                        }
                    }

                    fields.Add((field.Name.ToSnakeCase(), pythonType, pythonHint));
                }

                foreach (string heioTypeName in usedHEIOTypes)
                {
                    string name = heioTypeName[(heioTypeName.LastIndexOf('.') + 1)..];
                    builder.AppendLine($"from .{TypeToFileName(name)} import {name}");
                }

                builder.AppendLine();
                builder.AppendLine($"class {type.Name}(ctypes.Structure):");

                foreach ((string name, string type, string hint) field in fields)
                {
                    builder.AppendLine($"    {field.name}: {field.hint}");
                }

                builder.AppendLine();
                builder.AppendLine($"{type.Name}.__fields__ = [");

                foreach ((string name, string type, string hint) field in fields)
                {
                    builder.AppendLine($"    (\"{field.name}\", {field.type}),");
                }

                builder.AppendLine("]");
                builder.AppendLine();

                string filename = TypeToFileName(type.Name);
                initBuilder.AppendLine($"from .{filename} import {type.Name}");

                string filepath = Path.Join(outputDirectory, filename + ".py");
                File.WriteAllText(filepath, builder.ToString());
            }

            string initFilepath = Path.Join(outputDirectory, "__init__.py");
            File.WriteAllText(initFilepath, initBuilder.ToString());
        }
    }
}
