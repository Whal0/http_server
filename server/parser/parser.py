"""Module provides util functions that help with parsing individual parts of incoming requests"""

from typing import Optional, Tuple

from server.util.exceptions import InvalidRequestException, VersionNotSupportedException
from server.util.consts import SERVED_HEADER_FIELDS, CORRECT_HEADER_FIELDS
from server.parser.request import RequestHeader, RequestLine

HEADER_FIELDS = SERVED_HEADER_FIELDS.union(CORRECT_HEADER_FIELDS)

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
    
    if len(parts) != 3:
        raise InvalidRequestException("Invalid header line")
    # TODO: move somewhere else, here for now to keep the tests running correctly
    if parts[2] not in ['HTTP/1.1', 'HTTP/1.0', 'HTTP/0.9']:
        raise VersionNotSupportedException("We support requests up to HTTP 1.1")

    return RequestLine(method=parts[0], url=parts[1], version=parts[2])

def parse_body(line: str) -> str: #??
    return line

def extract_request_line(buffer: str) -> Tuple[Optional[RequestLine], str]:
    if "\r\n" in buffer:
        line_str, remaining = buffer.split("\r\n", 1)
        return parse_request_line(line_str), remaining
    return None, buffer

def extract_headers(buffer: str) -> Tuple[Optional[RequestHeader], str, int]:
    # if empty line we skip the line
    if buffer.startswith("\r\n"):
        return None, buffer[2:], 0

    if "\r\n\r\n" in buffer:
        header_block, remaining = buffer.split("\r\n\r\n", 1)
        header_obj = parse_header(header_block)
        
        content_length = 0
        if "content-length" in header_obj.headers:
            try:
                content_length = int(header_obj.headers["content-length"])
            except ValueError:
                content_length = 0
        return header_obj, remaining, content_length
    # no end to header, return the whole buffer back
    return None, buffer, 0

def extract_body(buffer: str, content_length: int) -> Tuple[Optional[str], str]:
    if content_length == 0:
        return "", buffer
    if len(buffer) >= content_length:
        return buffer[:content_length], buffer[content_length:]
    return None, buffer

'''
start-line CRLF
*( field-line CRLF )
CRLF
[ message-body ]
'''