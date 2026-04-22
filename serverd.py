import socket
import selectors
import sys

from session import sessions

sel = selectors.DefaultSelector()

class Connection:
    def __init__(self, sock : socket.socket):
        self.sock = sock
    
    def __hash__(self):
        return hash(self.sock)
    
    def read(self):
        try:
            message = self.sock.recv(1024)
            
            # could be faster mby? 
            #self.sock.recv_into
            return message
        except Exception: 
            self.sock.close()
            
            return
        
        except KeyboardInterrupt:
            sel.unregister(self.sock)
            self.sock.close()
        
        except BrokenPipeError:
            sel.unregister(self.sock)
            self.sock.close()

def read(conn : socket.socket, mask):
    
    try:
        message = conn.recv(1024)
        conn.recv_into
        return message
    except Exception: 
        conn.close()
        
        return
    
    except KeyboardInterrupt:
        sel.unregister(conn)
        conn.close()
    
    except BrokenPipeError:
        sel.unregister(conn)
        conn.close()
            
def accept(serverSocket : socket.socket, mask):

    conn, addr = serverSocket.accept()    
    conn.setblocking(False)
    
    # dont like it, needs more thouht
    sel.register(conn, selectors.EVENT_READ, "read")

class SelectServer:
    HOST =  "127.0.0.1"
    PORT = 65433
        
    def __init__(self):
        self.serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
        self.serverSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.serverSocket.bind((self.HOST, self.PORT))

    def run_server(self):
        self.serverSocket.listen(100)
        sel.register(self.serverSocket, selectors.EVENT_READ, accept)

        ## loop has to handle read,accept events
        try:
            while True:
                events = sel.select()
                for key, mask in events:
                    
                    # should work? ugly
                    if key.data == "read":
                        #xd
                        sessions[key.fileobj].read()
                    elif key.data == "accept":
                        accept()
                
        finally:
            self.serverSocket.close()
                    
    def stop_server(self):
        self.serverSocket.close()

if __name__ == "__main__":
    server = SelectServer()
    server.run_server()