import socket
import selectors
import sys
from typing import Iterator
from server import config

from server.session import  HTTPSession, sessions
from server.response_handler import ResponseHandler
from server.file_manager import FileManager

sel = selectors.DefaultSelector()

import logging
from server.util.logger import logger

logger.setLevel(logging.DEBUG)

class Connection:
    def __init__(self, sock : socket.socket):
        self.sock = sock
        # it will be a simplequeue
        self.send_generator_buffer_queue : list[Iterator] =  []
        self.curr_generator_buffer : Iterator = None
        self.send_buffer : bytes = b''
        self.is_sending : bool = False
        
    def __hash__(self):
        return hash(self.sock)
    
    def read(self):
        try:
            message = self.sock.recv(1024)
            
            if message == b'':    
                sel.unregister(self.sock)
                self.sock.close()
                return None
                
            return message
        
        except BrokenPipeError:
            sel.unregister(self.sock)
            self.sock.close()

    def close_conn(self):
        print("closing connection")
        if self.sock.fileno() != -1:
            sel.unregister(self.sock)
        self.sock.close()
    
    def _fill_buffer(self):
        
        if self.curr_generator_buffer:
            if 0 <= len(self.send_buffer) < 1024:
                try:
                    next_bytes = next(self.curr_generator_buffer)
                    self.send_buffer = self.send_buffer + next_bytes
                    return
                
                except StopIteration:
                    if self.send_generator_buffer_queue:
                        self.curr_generator_buffer = self.send_generator_buffer_queue.pop(0)
                        self.send_buffer += next(self.curr_generator_buffer)
                        return

                if 0 == len(self.send_buffer):
                    self.is_sending = False
                    sel.modify(self.sock, selectors.EVENT_READ)
                    return
        else:
            self.curr_generator_buffer = self.send_generator_buffer_queue.pop(0)
            self.send_buffer += next(self.curr_generator_buffer)
    
    def send_data(self):

        self._fill_buffer()
        
        if self.is_sending:
            try:
                bytes_send = self.sock.send(self.send_buffer)
                self.send_buffer = self.send_buffer[bytes_send:]
                
            except BrokenPipeError:
                sel.unregister(self.sock)
                self.sock.close()
        else:
            sessions[self.sock].close_session()
                    
    def write(self, get_data : Iterator) -> None:
        
        if not self.is_sending:
            self.is_sending = True
            sel.modify(self.sock, selectors.EVENT_READ | selectors.EVENT_WRITE)
            
        self.send_generator_buffer_queue.append(get_data)
        
class SelectServer:
    HOST =  "127.0.0.1"
    PORT = 65432
        
    def __init__(self):
        logger.info(f"starting server with config {config.CONFIG}")
    
        self.serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
        self.serverSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.serverSocket.bind((self.HOST, self.PORT))
        self.running = False
        
    def _accept(self):

        clientSocket, addr = self.serverSocket.accept()    
        clientSocket.setblocking(False)
        
        conn = Connection(clientSocket)

        sessions[clientSocket] = HTTPSession(conn, response_handler=ResponseHandler(file_manager=FileManager()))
        
        try:
            sel.get_key(clientSocket.fileno())
            sel.unregister(clientSocket.fileno())
        except KeyError:
            pass

        sel.register(clientSocket, selectors.EVENT_READ, "read")
        
    def serve_read(self, sock : socket.socket):
        # if sock.fileno()    == -1:
        #     sessions[sock].close_session()
        #     return 
        
        if not sessions.get(sock):
            self._accept()
        else:
            sessions[sock].read()
   
    def serve_write(self, sock):
        sessions[sock].conn.send_data()

    def run_server(self):
        self.serverSocket.listen(100)
        sel.register(self.serverSocket, selectors.EVENT_READ, "accept")
        self.running = True

        logger.info("server started")
        while self.running:

            events = sel.select()
            for key, mask in events:
                if key.fd == -1:
                    sessions[key.fileobj].close_session()
                    continue

                if mask == selectors.EVENT_READ:
                    self.serve_read(key.fileobj)

                elif mask == selectors.EVENT_WRITE:                
                    self.serve_write(key.fileobj)
   
    def _stop_server(self):
        for session in sessions.copy().values():
            session.close_session() 
         
        sel.unregister(self.serverSocket)
        logger.info("close server")
        self.serverSocket.close()
        self.running = False

if __name__ == "__main__":
    
    server = SelectServer()
    
    try:
        server.run_server()
    except Exception as e:
        logger.error(f"server stopped - %s", e)
    except KeyboardInterrupt:
        logger.info("Sever stopped by SIGKILL")
        server._stop_server()