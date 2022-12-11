class RequestError(Exception):
    "Raised when a request wasn't successfull"

    def __init__(self, message=None):
        super().__init__(message)


class ResponseError(Exception):
    "Raised when the response wasn't successfull"

    def __init__(self, message=None):
        super().__init__(message)
