"""
This module handles session, completes requests and passess responses to Connection object.

Uses parser module to parse request contents and ResponseHandler construct proper responses. 

It provides session management class HTTPSession that holds session state and coordinates communication logic.
"""
import socket

from server.parser.parser import extract_request_line, extract_headers, extract_body
from server.parser.request import Request, RequestHeader, RequestLine
from server.parser.response import Response
from server.response_handler import ResponseHandler
from server.util.logger import logger

class HTTPSession:
    """Manages the request lifecycle for a single client connection."""
    
    def __init__(self, conn, response_handler = None):        
        self.conn = conn
        self.read_buffer : str = ""
        self.write_buffer : str = ""
        self.request_line : RequestLine = None
        self.request_header : RequestHeader = None 
        self.request_body : str = ""
        self.content_length : int = 0
        self.phase : int = 0
        self.requests : list[Request] = []
        self.response_handler : ResponseHandler = response_handler
    
    def read(self) -> None:    
        """
        method reads and processes request
        
        parses them, creates response and sets up to be send using connection object
        """
    
        new_data : str = self.conn.read().decode()
        if not new_data:
            self.close_session()
            return
        
        self._get_requests(new_data)

        for request in self.requests:
            logger.info("%s", str(request))
            
            response : Response = self.response_handler.handle_request(request)
            self.conn.write(iter(response))

    def close_session(self) -> None:
        """closes onging session and ensures proper cleanup"""
        
        self.conn.close_conn()
        sessions.pop(self.conn.sock)
        print("closing session")

    def _reset_request(self) -> None:
        # resets request state
        self.request_line = None 
        self.request_header = None 
        self.request_body = ""
        self.content_length = 0

    def _get_requests(self, new_data : str) -> bool:
        
        # add new data to current buffer to have whole context
        self.read_buffer += new_data

        while True:
            # it request line was not parsed in previous call, try to parse
            if self.request_line is None:
                self.request_line, self.read_buffer = extract_request_line(self.read_buffer)
                
                # if still not parsed, return
                if self.request_line is None:
                    return

            # it request header was not parsed in previous call, try to parse
            if self.request_header is None:
                header_obj, remaining, content_length = extract_headers(self.read_buffer)
                
                if header_obj is not None:
                    self.request_header = header_obj
                    self.read_buffer = remaining
                    self.content_length = content_length
                
                # if not parsed and there is nothing left, we knowe there wont be no body so we can create request and reset state
                elif remaining == '':
                    self.read_buffer = remaining
                    
                    request = Request(line=self.request_line, header=self.request_header, body="")
                    self.requests.append(request)
                    self._reset_request()
                    return
                
                # if something left, just return and try to parse header again next time
                else:
                    return

            self.request_body, self.read_buffer = extract_body(self.read_buffer, self.content_length)

            # the body was parsed successfully/there is no content, so we create request and reset state            
            if self.request_body is not None:
                request = Request(line=self.request_line, header=self.request_header, body=self.request_body)
                self.requests.append(request)
                self._reset_request()
            
            # there is not enough content in buffer to be parsed
            elif self.request_body is None and remaining != "":
                return 

# dictionary that holds ongoing sessions                
sessions : dict[socket.socket, HTTPSession] = {}  