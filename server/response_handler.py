"""
This module contains ResponseHandler class that handles incoming methods, creates and returns adequate Response class.
"""

from server.parser.response import Response, ResponseHeader, ResponseLine 
from server.parser.request import Request
from server.file_manager import FileManager, File
from server.util.exceptions import DirectoryAccessForbiddenException, FileNotFoundException
from server.util.logger import logger

class ResponseHandler:

    def __init__(self, file_manager):
        self.file_manager : FileManager = file_manager

    @staticmethod
    def _create_response() -> Response:
        """Creates base Response with default attributes"""
         
        return Response(
            ResponseLine(
                version="HTTP/1.1",
                status_code=200
            ),
            ResponseHeader(
                headers={}
                #"Date" : datetime.datetime.now()
            )
        )
    
    @staticmethod
    def create_response_400() -> Response:
        response = __class__._create_response()        
        response.line.status_code = 400

        return response
    
    @staticmethod
    def _create_response_501() -> Response:
        response = __class__._create_response()        
        response.line.status_code = 501

        return response
    
    def handle_request(self, request : Request) -> Response:
        
        match request.line.method:
            case "GET":
                return self._handle_get(request=request)

            case "HEAD":
                return self._handle_head(request=request) 
            
            case "PUT":
                return self._handle_put(request=request)
            
            case "OPTIONS":
                return self._handle_options(request=request)
            
            case _:
                return self._create_response_501()
        
    def _handle_get(self, request : Request) -> Response:
        response : Response = self._create_response()

        try:
            file : File = self.file_manager.get_file(request.line.url)

            response.line.status_code = 200
            response.header.add_header("Content-Type", file.mime_type)
            response.header.add_header("Content-Length", file.size)
            response.header.add_header("Last-Modified", file.last_modified)
        
            response.body = file.data
        except PermissionError:
            response.line.status_code = 400
        except (DirectoryAccessForbiddenException, FileNotFoundException) as e:
            logger.debug("request not served - %s", str(e))
            
            response.line.status_code = 404
        except Exception:
            response.line.status_code = 500
        
        return response

    def _handle_head(self, request : Request) -> Response:
        response : Response = self._create_response()

        try:
            file : File = self.file_manager.get_metadata(request.line.url)
            response.header.add_header("Content-Type", file.mime_type)
            response.header.add_header("Content-Length", file.size)
            response.header.add_header("Last-Modified", file.last_modified)

        except PermissionError:
            response.line.status_code = 400
        except (DirectoryAccessForbiddenException, FileNotFoundException):
            response.line.status_code = 404

        return response

    def _handle_options(self, request : Request) -> Response:
        response : Response = self._create_response()
        
        response.line.status_code = 204
        response.header.add_header("Allow", "GET, POST, OPTIONS, HEAD")

        return response

    def _handle_put(self, request : Request) -> Response:
        response : Response = self._create_response()

        try:
            self.file_manager.put_file(request.line.url, bytes(request.body, encoding='utf-8'))

            response.line.status_code = 201
            response.header.add_header("Content-Location", request.line.url)

        except OSError:
            response.line.status_code = 500
        except (PermissionError, DirectoryAccessForbiddenException):
            response.line.status_code = 400

        return response