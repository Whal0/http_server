#from serverd import Connection
from server.parser.parser import extract_request_line, extract_headers, extract_body
from server.parser.request import Request, RequestHeader, RequestLine
import socket
from typing import Tuple
from server.response_handler import ResponseHandler

class HTTPSession:
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
        new_data = self.conn.read().decode()
        self.get_requests(new_data)

        for request in self.requests:
            print(request)
            response = self.response_handler.handle_request(request)
            self.conn.write(iter(response))

    def close_session(self):
        self.conn.close_conn()
        sessions.pop(self.conn.sock)
        print("closing session")

    def reset_request(self):
        self.request_line : RequestLine = None 
        self.request_header : RequestHeader = None 
        self.request_body : str = ""
        self.content_length : int = 0

    def get_requests(self, new_data) -> bool:
        self.read_buffer += new_data

        while True:
            if self.request_line is None:
                self.request_line, self.read_buffer = extract_request_line(self.read_buffer)
                if self.request_line is None:
                    return

            if self.request_header is None:
                header_obj, remaining, content_length = extract_headers(self.read_buffer)
                # reszte nie musimy bo zawsze jeśli obj jest reszta też
                if header_obj is not None:
                    self.request_header = header_obj
                    self.read_buffer = remaining
                    self.content_length = content_length
                
                elif remaining == '':
                    self.read_buffer = remaining
                    
                    request = Request(line=self.request_line, header=self.request_header, body="")
                    self.requests.append(request)
                    self.reset_request()
                    return
                
                else:
                    return

            self.request_body, self.read_buffer = extract_body(self.read_buffer, self.content_length)

            if self.request_body is not None:
                request = Request(line=self.request_line, header=self.request_header, body=self.request_body)
                self.requests.append(request)
                self.reset_request()

            elif self.request_body is None and remaining != "":
                return 
                    
sessions = {}  