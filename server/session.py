#from serverd import Connection
from server.parser import Request, RequestHeader, RequestLine, parse_header, parse_request_line
import socket
from typing import Tuple

class HTTPSession:
    def __init__(self, conn):
        self.conn = conn
        self.read_buffer : str = ""
        self.write_buffer : str = ""
        self.request_line : RequestLine = None
        self.request_header : RequestHeader = None 
        self.request_body : str = ""
        self.content_length : int = 0
        self.phase : int = 0
        self.requests : list[Request] = []

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
            if not self.request_line:
                is_ready = self.line()
                if not is_ready:
                    return
                
            if not self.request_header:
                is_ready = self.header()
                if not is_ready:
                    return 
            
            if not self.request_body:
                is_ready = self.parse_body()
                if not is_ready:
                    return 
                else:
                    request = Request(line = self.request_line, header = self.request_header, body = self.request_body)
                    self.requests.append(request)
                    self.reset_request()

    def parse_body(self):
        if self.content_length == 0:
            return True
        elif self.content_length <= len(self.read_buffer): 
            self.request_body, self.read_buffer = self.read_buffer[:self.content_length], self.read_buffer[self.content_length:]
            return True
        else: 
            return False

    # temp name, cant use parse_line duo to name collision
    def line(self):
        if "\r\n" in self.read_buffer:
            data_to_parse, self.read_buffer = self.read_buffer.split('\r\n', maxsplit=1)[0], self.read_buffer.split('\r\n', maxsplit=1)[1]
            self.request_line = parse_request_line(data_to_parse)
            return True

    # temp name, cant use parse_line duo to name collision
    def header(self):
        if self.read_buffer[0:2] == "\r\n":
            self.read_buffer = self.read_buffer[2:]

            request = Request(line = self.request_line, header = self.request_header, body = self.request_body)
            self.requests.append(request)
            self.reset_request()
            self.content_length = 0

            if self.read_buffer:
                return True
            else:
                return False
        
        elif "\r\n\r\n" in self.read_buffer:
            data_to_parse, self.read_buffer = self.read_buffer.split('\r\n\r\n', maxsplit=1)[0], self.read_buffer.split('\r\n\r\n', maxsplit=1)[1]
            self.request_header = parse_header(data_to_parse)
            
            if "content-length" in self.request_header.headers.keys():
                self.content_length = int(self.request_header.headers["content-length"])
            return True
         
        return False

sessions = {}
        
        
        
        
            
        
        