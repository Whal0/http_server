#from serverd import Connection
from server.parser import Request, RequestHeader, RequestLine, extract_request_line, extract_headers, extract_body
import socket
from typing import Tuple

class HTTPSession:
    def __init__(self, conn, request_handler = None):
        self.conn = conn
        self.read_buffer : str = ""
        self.write_buffer : str = ""
        self.request_line : RequestLine = None
        self.request_header : RequestHeader = None 
        self.request_body : str = ""
        self.content_length : int = 0
        self.phase : int = 0
        self.requests : list[Request] = []
        self.request_handler = request_handler

    def send_response(self, response):
        self.conn.send()
    
    def read(self) -> None:
        new_data = self.conn.read().decode()
        self.get_requests(new_data)
        
        for request in self.requests:
            print(request)

        for request in self.requests:
            self.handle_request(request)
            print("request served")
        
        self.close_session()

    def handle_request(self, request):
        #print(request)
        response = "HTTP/1.1 200 OK"
        self.send_response(response=response)
    
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
        
        
        
        
            
        
        