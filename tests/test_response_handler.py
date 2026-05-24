import pytest
from unittest.mock import MagicMock
from server.response_handler import ResponseHandler
from server.parser.request import Request, RequestHeader, RequestLine
from server.parser.response import Response, ResponseHeader, ResponseLine

@pytest.fixture
def mock_file(mock_metadata):
    file = mock_metadata
    file.data = bytes("pykpykpyk", encoding="utf-8")
    yield file

@pytest.fixture
def mock_metadata():
    metadata = MagicMock()
    metadata.path = "kulawykonfident.com/komendapłock.html"
    metadata.mime_type = "text/html"
    metadata.last_modified = "Fri, 15 May 2026 21:08:42 GMT"
    metadata.data = "Fri, 15 May 2026 22:08:42 GMT"
    metadata.size = "9"
    metadata.is_directory = False
    yield metadata

@pytest.fixture
def mock_file_manager(mock_file, mock_metadata):
    file_manager = MagicMock()
    file_manager.get_file.return_value = mock_file
    file_manager.get_metadata.return_value = mock_metadata
    file_manager.put_file.return_value = None
    yield file_manager

def test_handle_request_get(mock_file_manager):

    handler = ResponseHandler(file_manager=mock_file_manager)

    request = Request(line=RequestLine(
        method="GET",
        url="http://kulawykonfident.com/komendapłock.html",
        version="HTTP/1.1",
    ), header=RequestHeader(headers={})
    )

    expected_response = Response(line=ResponseLine(
        version="HTTP/1.1",
        status_code=200,
    ), header=ResponseHeader(
        headers={
            "Content-Type" : "text/html",
            "Content-Length" : "9",
            "Last-Modified" : "Fri, 15 May 2026 21:08:42 GMT",
        }
    ), body=bytes("pykpykpyk", encoding="utf-8")
    )

    response = handler.handle_request(request)

    assert response == expected_response
    
def test_handle_request_head(mock_file_manager):

    handler = ResponseHandler(file_manager=mock_file_manager)

    request = Request(line=RequestLine(
        method="HEAD",
        url="http://kulawykonfident.com/komendapłock",
        version="HTTP/1.1",
    ), header=RequestHeader(headers={})
    )

    expected_response = Response(line=ResponseLine(
        version="HTTP/1.1",
        status_code=200,
    ), header=ResponseHeader(
        headers={
            "Content-Type" : "text/html",
            "Content-Length" : "9",
            "Last-Modified" : "Fri, 15 May 2026 21:08:42 GMT",
        }
    ))

    response = handler.handle_request(request)

    assert response == expected_response

def test_handle_request_put(mock_file_manager):

    handler = ResponseHandler(file_manager=mock_file_manager)

    request = Request(line=RequestLine(
        method="PUT",
        url="http://kulawykonfident.com/komendapłock",
        version="HTTP/1.1",
    ), header=RequestHeader(headers={"Content-Length : 9"}),
    body="pykpykpyk"
    )

    expected_response = Response(line=ResponseLine(
        version="HTTP/1.1",
        status_code=201,
    ), header=ResponseHeader(
        headers={
            "Content-Location" : "http://kulawykonfident.com/komendapłock",
        }
    ))

    response = handler.handle_request(request)

    assert response == expected_response
    
def test_handle_request_options(mock_file_manager):    

    handler = ResponseHandler(file_manager=mock_file_manager)

    request = Request(line=RequestLine(
        method="OPTIONS",
        url="http://kulawykonfident.com/komendapłock",
        version="HTTP/1.1",
    ), header=RequestHeader(headers={})
    )
    
    expected_response = Response(line=ResponseLine(
        version="HTTP/1.1",
        status_code=204,
    ), header=ResponseHeader(
        headers={
            "Allow" : "GET, POST, OPTIONS, HEAD",
        }
    ))

    response = handler.handle_request(request=request)

    assert response == expected_response




