using System;
using System.Runtime.InteropServices;

namespace HEIO.NET.External
{
    public static unsafe class ErrorHandler
    {
        private static char* _errorMessage;

        public static void HandleError(Exception exception)
        {
            Console.WriteLine("A .NET error occured!");
            Console.WriteLine("Error message:");
            Console.WriteLine("\t" + exception.Message);
            Console.WriteLine("Stack trace:");
            Console.WriteLine(exception.StackTrace);
            Console.WriteLine();

            _errorMessage = exception.Message.ToPointer();
        }

        [UnmanagedCallersOnly(EntryPoint = "error_get")]
        public static char* GetError()
        {
            return _errorMessage;
        }
    }
}
