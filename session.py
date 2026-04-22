from serverd import Connection

sessions = {}

def create_session(conn : Connection):
    sessions[conn] = HTTPSession(conn)

class HTTPSession:
    
    def __init__(self, conn):
        self.conn : Connection = conn
        self.read_buffer = None
        self.write_buffer = None
    
    def send_response():
        pass
    
    def read(self):
        new_data = self.conn.read()
        # ?
        get_request(new_data)

def get_request() -> Request:
    
    request_line_data = ''
    header_data = ''
    body_data = ''
    
    # this looks ugly, make simpler
    while True:
        data = ''
        
        while True:
            new_data : str = read().decode()
            
            if '\r\n' in new_data:
                data += new_data
                request_line_data, data = data.split('\r\n')[0], data.split('\r\n')[1]
            
                request_line : RequestLine = parse_request_line(request_line_data)
                break
            else:
                data += new_data

        while True:
            new_data : str = read().decode()
            
            if '\r\n' in new_data:
                data += new_data
                request_line_data, data = data.split('\r\n')[0], data.split('\r\n')[1]
            
                request_header = RequestHeader(header_data)
                break
            else:
                data += new_data

        while True:
            new_data : str = read().decode()
            
            if '\r\n\r\n' in new_data:
                data += new_data
                request_line_data, data = data.split('\r\n')[0], data.split('\r\n')[1]
            
                request_header = RequestHeader(header_data)
                break
            else:
                data += new_data

        return Request(line = request_line, header = request_header, body = request_body)


# mental draft
# def session():
    
#     while True:
        
#         request = get_request()
        
#         response = handle_request(request)
        
#         send_response(response)
        
        
        
        
            
        
        