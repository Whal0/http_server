class BaseHTTPException(Exception):
    pass

class InvalidRequestException(BaseHTTPException):
    pass

class VersionNotSupportedException(BaseHTTPException):
    pass