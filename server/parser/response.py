from server.parser.message import Header, Message
from server.util.consts import STATUS_CODE

class ResponseHeader(Header):
    def add_header(self, header, value):
        self.headers[header] = value

class ResponseLine:
    def __init__(self, version, status_code):
        self.version = version
        self._status_code = status_code
        self.phrase = STATUS_CODE[int(status_code)]

    @property
    def status_code(self):
        return self._status_code
    
    @status_code.setter
    def status_code(self, code):
        self._status_code = code
        self.phrase = STATUS_CODE[int(code)]

    def __eq__(self, other):
        if isinstance(other, ResponseLine): 
            if not self.version == other.version:
                print(f"{self.version} not equal {other.version}")
                return False
            if not self.status_code == other.status_code:
                print(f"{self.status_code} not equal {other.status_code}")
                return False
            if not self.phrase == other.phrase:
                print(f"{self.phrase} not equal {other.phrase}")
                return False
            return True
        
        raise TypeError(f"= not supported between instances of '{self.__class__}' and '{type(other)}'")


class Response(Message):
    line: ResponseLine 
    header: ResponseHeader
    
    def __init__(self, line : ResponseLine, header : ResponseHeader, body : str = None): #czemu tu był Line?
        super().__init__(line, header, body)