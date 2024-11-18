class HEIO_NET:
    '''HEIO.NET library types'''

    IMAGE: any = None
    '''class HEIO.NET.Image'''

    PYTHON_HELPERS: any = None
    '''class HEIO.NET.PythonHelpers'''

    @classmethod
    def load(cls):

        from HEIO.NET import (
            Image,
            PythonHelpers
        )

        cls.IMAGE = Image
        cls.PYTHON_HELPERS = PythonHelpers