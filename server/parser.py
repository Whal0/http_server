from typing import Optional, Dict
from server.exceptions import InvalidRequestException, VersionNotSupportedException
from server.consts import HEADER_FIELDS

class RequestHeader:
    def __init__(self, headers : Dict[str, str]):
        self.headers = headers

    def __str__(self):
        return "".join(f"{k} : {v}\r\n" for k, v in self.headers.items())

    def __eq__(self, other):
        if isinstance(other, RequestHeader):
            for self_d, other_d in zip(self.headers.items(), other.headers.items()):

                if not self_d == other_d:
                    print(self_d)
                    print(other_d)
                    print(f"{self_d[0]} : {self_d[1]} is not equal to {other_d[0]} : {other_d[1]}") 
                    return False
                    
            return True
        raise TypeError(f"= not supported between instances of '{self.__class__}' and '{type(other)}'")
        
class RequestLine:
    def __init__(self, method, url, version):
        self.method = method
        self.url = url 
        self.version = version
    
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

class Request:
    def __init__(self, line : RequestLine,  header : RequestHeader, body : Optional[str]):
        self.line = line
        self.header = header
        self.body = body

    def __str__(self):
        return str(self.line) + str(self.header) + self.body

    def __eq__(self, other):
        if isinstance(other, Request):
            if not self.line == other.line:
                print(f"{self.line} is not equal to {other.line}")
                return False
            if not self.header == other.header:
                print(f"{self.header} is not equal to {other.header}")
                return False
            if not self.body == other.body:
                print(f"{self.body} is not equal to {other.body}")
                return False
            return True
        
        raise TypeError(f"= not supported between instances of '{self.__class__}' and '{type(other)}'")

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
 
def parse_header(line: str) -> RequestHeader:
    headers = {}
    
    for header_line in line.split("\r\n"):
        # i hope this doesn't break the field order
        if ": " in header_line:
            key, value = header_line.split(": ", 1)
            key = key.strip().lower()
            value = value.strip()

            if key in HEADER_FIELDS:
                headers[key] = value

    return RequestHeader(headers=headers)

def parse_request_line(line: str) -> RequestLine:
    parts = line.strip().split(" ")
    
    # this is part of parsing process - THUMB UP
    if len(parts) != 3:
        raise InvalidRequestException("Invalid header line")
    
    # not part of parsing process -> focus on breaklines, formatting 
    if parts[2] not in ['HTTP/1.1', 'HTTP/1.0', 'HTTP/0.9']:
        raise VersionNotSupportedException("We support requests up to HTTP 1.1")

    return RequestLine(method=parts[0], url=parts[1], version=parts[2])

'''
start-line CRLF
*( field-line CRLF )
CRLF
[ message-body ]
'''

