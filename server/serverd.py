"""
This module handles low level connection management, takes care of handling socket communication and asynchronous event loop.

It provides two classes, SelectServer and Connection.
"""
import socket
import selectors
from typing import Iterator
import logging
from server.util.logger import logger

from server import config
from server.session import  HTTPSession, sessions
from server.response_handler import ResponseHandler
from server.file_manager import FileManager

logger.setLevel(logging.DEBUG)

sel = selectors.DefaultSelector()

# util function for logging
def _get_client_server_socket_address(sock):
    local_ip, local_port = sock.getsockname()
    remote_ip, remote_port = sock.getpeername()

    return f"server socket {local_ip}:{local_port}, client socket {remote_ip}:{remote_port}"

#TODO: make generator_buffer_queue a simplequeue
class Connection:
    """Class takes care of managing connection with peer, it sends/reads bytes and is used to pass them to higher modules"""
    
    def __init__(self, sock : socket.socket):
        self.sock = sock
        self.send_generator_buffer_queue : list[Iterator] =  []
        self.curr_generator_buffer : Iterator = None
        self.send_buffer : bytes = b''
        self.is_sending : bool = False
    
    # needed for session to store it in sessions
    def __hash__(self):
        return hash(self.sock)
    
    def read(self):
        """method reads incoming messages"""
        
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
        """method takes care of cleaning up and closing connection"""
        
        logger.info("closing connection with peer, %s", _get_client_server_socket_address(self.sock))

        if self.sock.fileno() != -1:
            sel.unregister(self.sock)
        self.sock.close()
    
    def _fill_buffer(self):
        """takes care of filling up buffer and managing sending/queue state"""
        
        # we fill as long as there is data in current generator
        if self.curr_generator_buffer:
            
            # we fill only when the buffer has small amount of data
            if 0 <= len(self.send_buffer) < 1024:
                try:
                    # if generator has data, we simply fill it
                    next_bytes = next(self.curr_generator_buffer)
                    self.send_buffer = self.send_buffer + next_bytes
                    return
                
                except StopIteration:
                    # if its empty, we check if there is another generator
                    if self.send_generator_buffer_queue:
                        self.curr_generator_buffer = self.send_generator_buffer_queue.pop(0)
                        self.send_buffer += next(self.curr_generator_buffer)
                        return

                # if the buffer is empty and there is no new generator, we stop sending
                if 0 == len(self.send_buffer):
                    self.is_sending = False
                    sel.modify(self.sock, selectors.EVENT_READ)
                    return
                
        # if there is no present generator, it means there is one waiting for us
        # this is the case when the socket just started sending and its the first _fill_buffer() call
        else:
            self.curr_generator_buffer = self.send_generator_buffer_queue.pop(0)
            self.send_buffer += next(self.curr_generator_buffer)
    
    def send_data(self):
        """sends data if any available, otherwise makes sure to modify connection state accordingly"""
        
        self._fill_buffer()
        
        # its true if there is any data in the buffer
        if self.is_sending:
            try:                
                bytes_send = self.sock.send(self.send_buffer)
                self.send_buffer = self.send_buffer[bytes_send:]
                
                logger.info("sent %i bytes, %s",     
                    bytes_send,  
                    _get_client_server_socket_address(self.sock))
            
            except BrokenPipeError:
                sel.unregister(self.sock)
                self.sock.close()
        else:
            sessions[self.sock].close_session()
       
    def write(self, get_data : Iterator) -> None:
        """gets provided iterator and takes care of sending data"""
        
        if not self.is_sending:
            self.is_sending = True
            sel.modify(self.sock, selectors.EVENT_READ | selectors.EVENT_WRITE)
            
        self.send_generator_buffer_queue.append(get_data)
        
class SelectServer:
    """Class that manages internal server state and its event loop"""
    
    HOST =  "127.0.0.1"
    PORT = 65432
        
    def __init__(self):
        logger.info(f"starting server with config {config.CONFIG}")
    
        self.serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
        self.serverSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.serverSocket.bind((self.HOST, self.PORT))
        self.running = False
        
    def _accept(self):
        """accepts new connection"""
        
        clientSocket, addr = self.serverSocket.accept()    
        clientSocket.setblocking(False)
        
        conn = Connection(clientSocket)

        sessions[clientSocket] = HTTPSession(conn, response_handler=ResponseHandler(file_manager=FileManager()))
        
        logger.info("accepted new connection and started a session %s", _get_client_server_socket_address(clientSocket))
        
        # safe check, we want to know if the current socket is not already registered
        # this can happen when we close socket but not unregister it due to some error
        try:
            logger.warning("socket was closed but not unregistered, %s", _get_client_server_socket_address(clientSocket))
            
            sel.get_key(clientSocket.fileno())
            sel.unregister(clientSocket.fileno())
        except KeyError:
            pass

        sel.register(clientSocket, selectors.EVENT_READ, "read")
        
    def _serve_read(self, sock : socket.socket):
        """serves the READ event"""
        
        # if sock.fileno()    == -1:
        #     sessions[sock].close_session()
        #     return 
        
        # we check if its an ongoing session, yes it means its a simple read, otherwise its new incoming connection
        if not sessions.get(sock):
            self._accept()
        else:
            sessions[sock].read()
   
    def _serve_write(self, sock):
        """serves the WRITE event"""
        sessions[sock].conn.send_data()

    def run_server(self):
        """runs server's event loop"""
        
        self.serverSocket.listen(100)
        sel.register(self.serverSocket, selectors.EVENT_READ, "accept")
        self.running = True

        logger.info("server started")
        
        while self.running:

            events = sel.select()
            for key, mask in events:
                if key.fd == -1:
                    logger.error("the socket was closed unexpectledly, %s, closing session...", _get_client_server_socket_address(key.fileobj))
                    
                    sessions[key.fileobj].close_session()
                    continue

                if mask == selectors.EVENT_READ:
                    self._serve_read(key.fileobj)

                elif mask == selectors.EVENT_WRITE:                
                    self._serve_write(key.fileobj)

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