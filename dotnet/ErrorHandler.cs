using System;
using System.Runtime.InteropServices;

namespace HEIO.NET
{
    public static unsafe class ErrorHandler
    {
        private static char* _errorMessage;

        public static void HandleError(Exception exception)
        {
            Console.WriteLine("A .NET error occured!");
            Console.WriteLine("Error message:");
            Console.WriteLine(exception.Message);
            Console.WriteLine("Stack trace:");
            Console.WriteLine(exception.StackTrace);
            Console.WriteLine();

            if(_errorMessage != null)
            {
                Util.Free(_errorMessage);
            }

            _errorMessage = exception.Message.ToPointer();
        }

        [UnmanagedCallersOnly(EntryPoint = "error_get")]
        public static char* GetError()
        {
            return _errorMessage;
        }

        [UnmanagedCallersOnly(EntryPoint = "error_free")]
        public static void FreeError()
        {
            if (_errorMessage != null)
            {
                Util.Free(_errorMessage);
                _errorMessage = null;
            }
        }
    }
}
