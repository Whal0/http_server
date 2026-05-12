from pytest import fixture
from server.session import HTTPSession
from unittest.mock import MagicMock
import pytest
from server.parser.request import Request, RequestHeader, RequestLine

# tests and pytest.ini is designed for having {working_folder} as http_server,
# if wish to use different one, change the paths in .vscode/launch.json accordingly

@fixture
def dummy_session():
    mock_conn = MagicMock()
    yield HTTPSession()

def test_get_requests_single_request():

    mock_conn = MagicMock()
    session = HTTPSession(conn=mock_conn)

    request = ("GET https://www.grydyk.com/main.py HTTP/1.1\r\n"
                "Connection : close\r\n"
                "Accept : */*\r\n"
                "Accept-Language : dn\r\n"
                "Content-length : 5\r\n\r\n"
                "AAAAA")
    
    expected_line = RequestLine(
        method="GET",
        url="https://www.grydyk.com/main.py",
        version="HTTP/1.1"
    )

    expected_header = RequestHeader(
        headers={
                "connection" : "close",
                "accept" : "*/*",
                "accept-language" : "dn",
                "content-length" : "5"
        }
    )

    expected_body = "AAAAA"

    expected_request = Request(line=expected_line,
                               header=expected_header,
                               body=expected_body)

    session.get_requests(request)

    assert len(session.requests) == 1
    assert session.read_buffer == ""
    assert session.request_line == None
    assert session.request_header == None
    assert session.request_body == ""
    assert session.requests[0].line == expected_line
    assert session.requests[0].header == expected_header
    assert session.requests[0].body == expected_body
    assert session.requests[0] == expected_request
    assert session.content_length == 0

def test_get_requests_partial_request():
        
    mock_conn = MagicMock()
    session = HTTPSession(conn=mock_conn)

    request = ("GET https://www.grydyk.com/main.py HTTP/1.1\r\n"
                "Connection : close\r\n"
                "Accept : */*\r\n")

    expected_line = RequestLine(
        method="GET",
        url="https://www.grydyk.com/main.py",
        version="HTTP/1.1"
    )

    session.get_requests(request)

    assert len(session.requests) == 0
    assert session.read_buffer == "Connection : close\r\nAccept : */*\r\n"
    assert session.request_line == expected_line
    assert session.request_header == None
    assert session.request_body == ""
    assert session.content_length == 0

def test_get_requests_multiple_requests():
        
    mock_conn = MagicMock()
    session = HTTPSession(conn=mock_conn)

    requests = ("GET https://www.grydyk.com/main.py HTTP/1.1\r\n"
                "Connection : close\r\n"
                "Accept : */*\r\n"
                "Accept-Language : dn\r\n"
                "Content-length : 5\r\n\r\n"
                "AAAAA"
                "POST https://www.grydyk10xdev.com/twardowski.py HTTP/1.0\r\n"
                "Connection : close\r\n"
                "Accept : plaintext\r\n"
                "Accept-Language : polska-gurom\r\n"
                "Content-length : 10\r\n\r\n"
                "1234567890")

    expected_line_1 = RequestLine(
        method="GET",
        url="https://www.grydyk.com/main.py",
        version="HTTP/1.1"
    )

    expected_header_1 = RequestHeader(
        headers={
                "connection" : "close",
                "accept" : "*/*",
                "accept-language" : "dn",
                "content-length" : "5"
        }
    )

    expected_body_1 = "AAAAA"

    expected_request_1 = Request(line=expected_line_1,
                               header=expected_header_1,
                               body=expected_body_1)

    expected_line_2 = RequestLine(
        method="POST",
        url="https://www.grydyk10xdev.com/twardowski.py",
        version="HTTP/1.0"
    )

    expected_header_2 = RequestHeader(
        headers={
                "connection" : "close",
                "accept" : "plaintext",
                "accept-language" : "polska-gurom",
                "content-length" : "10"
        }
    )

    expected_body_2 = "1234567890"

    expected_request_2 = Request(line=expected_line_2,
                               header=expected_header_2,
                               body=expected_body_2)

    session.get_requests(requests)

    assert len(session.requests) == 2
    assert session.read_buffer == ""
    assert session.request_line == None
    assert session.request_header == None
    assert session.request_body == ""
    assert session.requests[0].line == expected_line_1
    assert session.requests[0].header == expected_header_1
    assert session.requests[0].body == expected_body_1
    assert session.requests[0] == expected_request_1
    assert session.requests[1].line == expected_line_2
    assert session.requests[1].header == expected_header_2
    assert session.requests[1].body == expected_body_2
    assert session.requests[1] == expected_request_2
    assert session.content_length == 0

def test_get_requests_no_body():
        
    mock_conn = MagicMock()
    session = HTTPSession(conn=mock_conn)

    request = ("GET https://www.grydyk.com/main.py HTTP/1.1\r\n"
                "Connection : close\r\n"
                "Accept : */*\r\n"
                "Accept-Language : dn\r\n\r\n")

    expected_line = RequestLine(
        method="GET",
        url="https://www.grydyk.com/main.py",
        version="HTTP/1.1"
    )

    expected_header = RequestHeader(
        headers={
                "connection" : "close",
                "accept" : "*/*",
                "accept-language" : "dn",
        }
    )

    expected_body = ""

    expected_request = Request(line=expected_line,
                               header=expected_header,
                               body=expected_body)

    session.get_requests(request)

    assert len(session.requests) == 1
    assert session.read_buffer == ""
    assert session.request_line == None
    assert session.request_header == None
    assert session.request_body == ""
    assert session.requests[0].line == expected_line
    assert session.requests[0].header == expected_header
    assert session.requests[0].body == expected_body
    assert session.requests[0] == expected_request
    assert session.content_length == 0
    assert session.phase == 0

def test_get_requests_no_headers_and_body():
        
    mock_conn = MagicMock()
    session = HTTPSession(conn=mock_conn)

    request = ("GET https://www.grydyk.com/main.py HTTP/1.1\r\n\r\n")

    expected_line = RequestLine(
        method="GET",
        url="https://www.grydyk.com/main.py",
        version="HTTP/1.1"
    )

    expected_header = None 
    # RequestHeader(
    #     headers={}
    # )

    expected_body = ""

    expected_request = Request(line=expected_line,
                               header=expected_header,
                               body=expected_body)

    session.get_requests(request)

    assert len(session.requests) == 1
    assert session.read_buffer == ""
    assert session.request_line == None
    assert session.request_header == None
    assert session.request_body == ""
    assert session.requests[0].line == expected_line
    assert session.requests[0].header == expected_header
    assert session.requests[0].body == expected_body
    assert session.requests[0] == expected_request
    assert session.content_length == 0
    assert session.phase == 0

def test_get_requests_full_and_partial_request():
        
    mock_conn = MagicMock()
    session = HTTPSession(conn=mock_conn)

    requests = ("GET https://www.grydyk.com/main.py HTTP/1.1\r\n"
                "Connection : close\r\n"
                "Accept : */*\r\n"
                "Accept-Language : dn\r\n"
                "Content-length : 5\r\n\r\n"
                "AAAAA"
                "POST https://www.grydyk10xdev.com/twardowski.py HTTP/1.0\r\n"
                "Connection : close\r\n"
                "Accept : plaintext\r\n")

    expected_line_1 = RequestLine(
        method="GET",
        url="https://www.grydyk.com/main.py",
        version="HTTP/1.1"
    )

    expected_header_1 = RequestHeader(
        headers={
                "connection" : "close",
                "accept" : "*/*",
                "accept-language" : "dn",
                "content-length" : "5"
        }
    )

    expected_body_1 = "AAAAA"

    expected_request_1 = Request(line=expected_line_1,
                               header=expected_header_1,
                               body=expected_body_1)

    expected_line_2 = RequestLine(
        method="POST",
        url="https://www.grydyk10xdev.com/twardowski.py",
        version="HTTP/1.0"
    )

    session.get_requests(requests)

    assert len(session.requests) == 1
    assert session.read_buffer == "Connection : close\r\nAccept : plaintext\r\n"
    assert session.request_line == expected_line_2
    assert session.request_header == None
    assert session.request_body == ""
    assert session.requests[0].line == expected_line_1
    assert session.requests[0].header == expected_header_1
    assert session.requests[0].body == expected_body_1
    assert session.requests[0] == expected_request_1
    assert session.content_length == 0

def test_get_requests_partial_body():

    mock_conn = MagicMock()
    session = HTTPSession(conn=mock_conn)

    request = ("GET https://www.grydyk.com/main.py HTTP/1.1\r\n"
                "Connection : close\r\n"
                "Accept : */*\r\n"
                "Accept-Language : dn\r\n"
                "Content-length : 5\r\n\r\n"
                "AAA")
    
    expected_line = RequestLine(
        method="GET",
        url="https://www.grydyk.com/main.py",
        version="HTTP/1.1"
    )

    expected_header = RequestHeader(
        headers={
                "connection" : "close",
                "accept" : "*/*",
                "accept-language" : "dn",
                "content-length" : "5"
        }
    )

    expected_body = ""

    expected_request = Request(line=expected_line,
                               header=expected_header,
                               body=expected_body)

    session.get_requests(request)

    assert len(session.requests) == 0
    assert session.read_buffer == "AAA"
    assert session.request_line == expected_line
    assert session.request_header == expected_header
    assert session.request_body == None
    assert session.content_length == 5