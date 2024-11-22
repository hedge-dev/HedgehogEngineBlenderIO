class UserException(Exception):
    pass

class HEIOException(Exception):

    message: str

    def __init__(self, message: str, *args: object):
        self.message = message
        super().__init__(message, *args)