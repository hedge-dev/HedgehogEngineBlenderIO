
class HEIOException(Exception):

    message: str

    def __init__(self, message: str, *args: object):
        self.message = message
        super().__init__(message, *args)


class HEIODevException(HEIOException):

    def __init__(self, message: str, *args: object):
        super().__init__("Developer error, please report:" + message, *args)


class HEIOUserException(HEIOException):

    def __init__(self, message: str, *args: object):
        super().__init__(message, *args)
