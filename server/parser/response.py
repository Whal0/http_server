from server.parser.message import Header, Message
from server.util.consts import STATUS_CODE

class ResponseHeader(Header):
    def add_header(self, header, value):
        self.headers[header] = value

class ResponseLine:
    def __init__(self, version, status_code):
        self.version = version
        self.status_code = status_code
        self.phrase = STATUS_CODE[int(status_code)]

class Response(Message):
    line: ResponseLine 
    header: ResponseHeader
    
    def __init__(self, line : ResponseLine, header : ResponseHeader, body : str): #czemu tu był Line?
        super().__init__(line, header, body)