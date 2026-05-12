from server.parser.message import Header, Line, Message
from util.consts import STATUS_CODE

class ResponseHeader(Header):
    def add_header(self, header, value):
        self.headers[header] = value

class ResponseLine(Line):
    def __init__(self, version, status_code):
        super().__init__(version)
        self.status_code = status_code
        self.phrase = STATUS_CODE[int(status_code)]

class Request(Message):
    def __init__(self, line : ResponseLine, header : ResponseHeader, body : Line):
        super().__init__(line, header, body)