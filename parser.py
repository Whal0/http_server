from typing import Optional, Dict

# there are 19 header fields -> dict or explicit, if dict just degrade to request field
class RequestHeader:
    def __init__(self, headers : Dict[str, str | int]):
        self.headers = headers

class RequestLine:
    def __init__(self, method, url, version):
        self.method = method
        self.url = url
        self.version = version

class Request:
    def __init__(self, line : RequestLine,  header : RequestHeader, body : Optional[str]):
        self.line = line
        self.header = header
        self.body = body
 
def parse_header() -> RequestHeader:
    pass

def parse_request_line() -> RequestLine:
    pass

def parse_data() -> str:
    pass

class Response:
    def __init__(self, line, header, body):
        self.response_line = line
        self.header = header
        self.body = body
    
class ResponseLine:
    def __init__(self, version, status_code, phrase):
        self.version = version
        self.status_code = status_code
        self.phrase = phrase

class ResponseHeader:
    def __init__(self):
        pass


