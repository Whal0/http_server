class BaseHTTPException(Exception):
    pass

class InvalidRequestException(BaseHTTPException):
    pass

class VersionNotSupportedException(BaseHTTPException):
    pass

class FileNotFoundException(BaseHTTPException):
    pass

class DirectoryAccessForbiddenException(BaseHTTPException):
    pass

class NotModifiedException(BaseHTTPException):
    pass

class FileOperationException(BaseHTTPException):
    pass

class BadHeaderException(BaseHTTPException):
    pass

class BadLineException(BaseHTTPException):
    pass

class MalformedResponseException(BaseHTTPException):
    pass