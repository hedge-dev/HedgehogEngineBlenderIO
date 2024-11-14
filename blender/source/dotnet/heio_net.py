class HEIO_NET:
    '''HEIO.NET library types'''

    IMAGE: any = None
    '''class HEIO.NET.Image'''

    @classmethod
    def load(cls):

        from HEIO.NET import (
            Image
        )

        cls.IMAGE = Image