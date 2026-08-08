

import socket
from server.parser.request import Request, RequestHeader, RequestLine

class ClientSocket:
    """Minimal socket client used for end-to-end HTTP request testing."""
    
    def __init__(self, host = "127.0.0.1", port=65432):
        self._socket = socket.socket(family=socket.AF_INET, type=socket.SOCK_STREAM)
        self._server_host = host
        self._server_port = port
            
    def send(self, request : str):
        self._socket.connect((self._server_host, self._server_port))
        self._socket.sendall(bytes(request, encoding="utf-8"))
        
        response = b''
        res = self._socket.recv(1024)
        
        while res != b'':
            response += res
            res = self._socket.recv(1024)
            
        return response.decode()
        
    def close(self):
        self._socket.close()
        


    