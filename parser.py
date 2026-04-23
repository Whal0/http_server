from typing import Optional, Dict
from exceptions import InvalidRequestException, VersionNotSupportedException
import consts

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
 
def parse_header(line: str) -> RequestHeader:
    headers = {}
    
    for header_line in line.split("\r\n"):
        # i hope this doesn't break the field order
        if ": " in header_line:
            key, value = header_line.split(": ", 1)
            key = key.strip().lower()
            value = value.strip()

            if key in consts.HEADER_FIELDS:
                headers[key] = value

    return RequestHeader(headers=headers)


def parse_request_line(line: str) -> RequestLine:
    parts = line.strip().split(" ")
    
    if len(parts) != 3:
        raise InvalidRequestException("Invalid header line")
    
    if parts[2] not in ['HTTP/1.1', 'HTTP/1.0', 'HTTP/0.9']:
        raise VersionNotSupportedException("We support requests up to HTTP 1.1")

    return RequestLine(method=parts[0], url=parts[1], version=parts[2])


def parse_body() -> str:
    pass

class Response:
    def __init__(self, line, header, body):
        self.response_line = line
        self.header = header
        self.body = body
    
class ResponseLine:
    # TODO
    # can we just have a status code and then get the phrase from consts? less overhead
    def __init__(self, version, status_code, phrase):
        self.version = version
        self.status_code = status_code
        self.phrase = phrase

class ResponseHeader:
    def __init__(self):
        pass


'''
start-line CRLF
*( field-line CRLF )
CRLF
[ message-body ]
'''

