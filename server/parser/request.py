from server.parser.message import Header, Message

class RequestHeader(Header):
    pass

class RequestLine:
    """Represents the start line of an HTTP request."""

    def __init__(self, method, url, version):
        self.version = version
        self.method = method
        self.url = url 
    
    def __str__(self):
        return f"{self.method} {self.url} {self.version}\r\n"

    def __eq__(self, other):
        if isinstance(other, RequestLine): 
            if not self.method == other.method:
                print(f"{self.method} not equal {other.method}")
                return False
            if not self.url == other.url:
                print(f"{self.url} not equal {other.url}")
                return False
            if not self.version == other.version:
                print(f"{self.version} not equal {other.version}")
                return False
            return True
        
        raise TypeError(f"= not supported between instances of '{self.__class__}' and '{type(other)}'")

class Request(Message):
    """Full HTTP request including line, headers, and optional body."""

    line : RequestLine
    header : RequestHeader
    
    def __init__(self, line : RequestLine, header : RequestHeader, body : str = None): # same as response
        super().__init__(line, header, body)