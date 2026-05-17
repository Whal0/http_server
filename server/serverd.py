import socket
import selectors
from server.session import  HTTPSession, sessions
from typing import Iterator
from queue import SimpleQueue

sel = selectors.DefaultSelector()

class Connection:
    def __init__(self, sock : socket.socket):
        self.sock = sock
        # it will be a simplequeue
        self.send_generator_buffer_queue : SimpleQueue[Iterator] = SimpleQueue()
        self.curr_generator_buffer : Iterator = None
        self.send_buffer : bytes = b''
        self.is_sending : bool = False
        
    def __hash__(self):
        return hash(self.sock)
    
    def read(self):
        try:
            message = self.sock.recv(1024)
            return message
        
        except Exception: 
            sel.unregister(self.sock)
            self.sock.close()
        except KeyboardInterrupt:
            sel.unregister(self.sock)
            self.sock.close()
        except BrokenPipeError:
            sel.unregister(self.sock)
            self.sock.close()
    
    def _close_conn(self):
        print("closing connection")
        sel.unregister(self.sock)
        self.sock.close()
    
    def _fill_buffer(self):
        
        if self.curr_generator_buffer:
            if 0 <= len(self.send_buffer) < 1024:
                try:
                    self.send_buffer += next(self.curr_generator_buffer)
                    return
                
                except StopIteration:
                    if not self.send_generator_buffer_queue.empty():
                        self.curr_generator_buffer = self.send_generator_buffer_queue.get()
                        self.send_buffer += next(self.curr_generator_buffer)
                        return

                if 0 == len(self.send_buffer):
                    self.is_sending = False
                    sel.modify(self.sock, selectors.EVENT_READ)
                    return
        else:
            if not self.send_generator_buffer_queue.empty():
                self.curr_generator_buffer = self.send_generator_buffer_queue.get()
                self.send_buffer += next(self.curr_generator_buffer)
    
    def _send_data(self):

        self._fill_buffer()
        
        if self.is_sending:
            try:
                bytes_send = self.sock.send(self.send_buffer)
                self.send_buffer = self.send_buffer[bytes_send:]
                
            except BrokenPipeError:
                sel.unregister(self.sock)
                self.sock.close()
            except KeyboardInterrupt:
                sel.unregister(self.sock)
                self.sock.close()
            except Exception: 
                sel.unregister(self.sock)
                self.sock.close()
        else:
            self.sock.close()
                    
    def write(self, get_data : Iterator) -> None:
        
        if not self.is_sending:
            self.is_sending = True
            sel.modify(self.sock, selectors.EVENT_READ | selectors.EVENT_WRITE)
            
        self.send_generator_buffer_queue.put(get_data)
        
class SelectServer:
    HOST =  "127.0.0.1"
    PORT = 65432
        
    def __init__(self):
        self.serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
        self.serverSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.serverSocket.bind((self.HOST, self.PORT))
        
    def _accept(self):

        clientSocket, addr = self.serverSocket.accept()    
        clientSocket.setblocking(False)
        
        conn = Connection(clientSocket)

        sessions[clientSocket] = HTTPSession(conn)

        sel.register(clientSocket, selectors.EVENT_READ, "read")

    def run_server(self):
        self.serverSocket.listen(100)
        sel.register(self.serverSocket, selectors.EVENT_READ, "accept")

        print("server started")
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
                        self._accept(key.fileobj)
                        
                    elif key.data == "write":
                        print("sending data")
                        sessions[key.fileobj].write()
                
        finally:
            self._stop_server()
                    
    def _stop_server(self):
        print("close server")
        self.serverSocket.close()

if __name__ == "__main__":
    server = SelectServer()
    server.run_server()