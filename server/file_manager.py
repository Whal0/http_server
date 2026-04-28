from server.consts import MIME_TYPES
import os

from server.parser import Response

class FileManager:
    def __init__(self, base_dir='public'):
        self.base_dir = base_dir
        self.DEFAULT_FILES = ["index.html", "index.htm"]
        self.final_path = ''

    def path_exist(self, path: str) -> bool:
        # check na base_dir
        # check czy nie ma ../
        # check czy jest to w ogole scieżka
        # custom exception if it fails here, to change as bad request
        return True
    
    def sanitize(self,path: str) -> str:
        return path
    
    def get_mime_type(self,path: str) -> str:
        '''
            if path[-1] in MIME_TYPES:
                return MIME_TYPES
            else:
                return 'stream/octet'
        
        '''
    # TO WOŁA KAŻDA INNA PEWNIE< RESZTA PRYWATNA
    def get_file(self,path: str) -> Response: # not sure on the return type
        path = FileManager.sanitize() 

        if not FileManager.path_exist():
            return '404'
        
        if os.path.isdir(path):
            if self.DEFAULT_FILES in path:
                self.final_path += self.base_dir + self.DEFAULT_FILES[0]
    

    def get_file_size(self, path: str) -> int:
        return 0

    def read_file(self, path: str) -> bytes:
        return 'rb'
    
    def has_access(self, path:str) -> bool:
        return True

    def handle_error(self, error_code:int) -> Response:
        return None

    def get_last_modified(self, path:str):
        return "dunno"
