import socket
import selectors
from typing import Dict
from server.session import  HTTPSession, sessions

sel = selectors.DefaultSelector()

class Connection:
    def __init__(self, sock : socket.socket):
        self.sock = sock
    
    def __hash__(self):
        return hash(self.sock)
    
    def read(self):
        try:
            message = self.sock.recv(1024)
            return message
        
        except Exception: 
            self.sock.close()
        except KeyboardInterrupt:
            sel.unregister(self.sock)
            self.sock.close()
        except BrokenPipeError:
            sel.unregister(self.sock)
            self.sock.close()
    
    def close_conn(self):
        print("closing connection")
        sel.unregister(self.sock)
        self.sock.close()
    
    def send(self, data = "HTTP/1.1 200 OK\r\nConnection : close\r\n\r\n"):

        try:
            self.sock.send(data.encode())
        except BrokenPipeError:
            sel.unregister(self.sock)
            self.sock.close()
        except KeyboardInterrupt:
            sel.unregister(self.sock)
            self.sock.close()
        except Exception: 
            self.sock.close()

        print("responded to client")

            
def accept(serverSocket : socket.socket):

    clientSocket, addr = serverSocket.accept()    
    clientSocket.setblocking(False)
    
    conn = Connection(clientSocket)

    sessions[clientSocket] = HTTPSession(conn)

    sel.register(clientSocket, selectors.EVENT_READ, "read")

class SelectServer:
    HOST =  "127.0.0.1"
    PORT = 65432
        
    def __init__(self):
        self.serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
        self.serverSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.serverSocket.bind((self.HOST, self.PORT))

    def run_server(self):
        self.serverSocket.listen(100)
        sel.register(self.serverSocket, selectors.EVENT_READ, "accept")

        print("server started")
        ## loop has to handle read,accept events
        try:
            print("start event loop")
            while True:
                events = sel.select()
                for key, mask in events:
                    
                    if key.data == "read":
                        print("read data")

                        sessions[key.fileobj].read()

                    elif key.data == "accept":
                        print("accept connetion")
                        accept(key.fileobj)
                
        finally:
            print("close server")
            self.serverSocket.close()
                    
    def stop_server(self):
        print("close server")
        self.serverSocket.close()

if __name__ == "__main__":
    server = SelectServer()
    server.run_server()