import datetime
import os
import uuid
from server.consts import MIME_TYPES
from server.parser import Response

class FileManager:
    def __init__(self, base_dir='public'):
        self.base_dir = os.path.abspath(base_dir)
        self.DEFAULT_FILES = ("index.html", "index.htm")
        # self.full_path = ''

    def _get_path(self, path: str) -> str: # idk correct path?
        full_path = self._sanitize(path)
        full_path = os.path.abspath(os.path.join(self.base_dir, full_path))
        
        if not path.startswith(self.base_dir):
            raise PermissionError('backward traversal not allowed')
        
        return full_path
    
    def _sanitize(self, path: str) -> str:
        temp_path = path.lstrip('/')
        temp_path = os.path.normcase(temp_path)
        temp_path = os.path.normpath(temp_path)
        return temp_path

    
    def _get_mime_type(self, path: str, human_readable: bool = False) -> str:
        ext = os.path.splitext(path)[1].lower()
        default = 'text/plain' if human_readable else 'application/octet-stream'
        return MIME_TYPES.get(ext, default)
        
    
    def get_file(self, path: str, if_modified_since: datetime = None) -> Response: # not sure on the return type
        full_path = self._get_path(path)
        
        if not self.path_exist(full_path):
            return self._handle_error(404)
        
        file_size, file_mtime = self._get_file_metadata
        
        if if_modified_since is not None and if_modified_since >= file_mtime:
            return self._handle_error(304)

        if os.path.isdir(full_path):
            
            for filename in self.DEFAULT_FILES:
                temp_path = os.path.join(full_path, filename)
                if os.path.exists(temp_path):
                    full_path = temp_path
                    break
            
            if os.path.isdir(full_path):
                return self._handle_error(403) # moze 404?

        data = self.read_file(full_path, file_size) # dunno if we need size where

        # zawsze zwraca z wyjątkiek metoda HEAD
        return '200', self._get_mime_type(full_path), data

    def _get_file_metadata(self, path: str) -> int:
        try:
            stats = os.stat(path)
            return stats.st_size, stats.st_mtime
        except OSError as e:
            #log tutaj
            return None

    def read_file(self, path: str, size: int) -> bytes: # i can call get_fize_size idk what would be better
        # chunkowanie na potem z yield ?
        with open(path, 'rb') as file:
            data = file.read(size)
            return data
        
    def _has_access(self, path:str) -> bool: #TODO
        
        return True

    def _handle_error(self, error_code:int) -> Response: #TODO
        
        return None

    def get_last_modified(self, path:str):
        
        full_path = self._get_path(path)
    
        if not full_path or not os.path.exists(full_path):
            return None

        try:
            mtime = os.path.getmtime(full_path)
            dt = datetime.fromtimestamp(mtime)
            
            # Http header format section 3.3.1
            return dt.strftime('%a, %d %b %Y %H:%M:%S GMT')
            
        except OSError:
            return None
    
    def delete_file(self, path: str) -> bool:
        full_path = self._get_path(path)
        
        if os.path.isfile(full_path):
            os.remove(full_path)
            return True
        
        return False

    def put_file(self,path:str, data:bytes) -> bool:
        full_path = self._get_path(path)
        if not full_path:
            return False 
        
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        
        with open(full_path, 'wb') as f:
            f.write(data)
        return True

    def post_file(self, path: str, data: bytes, filename: str = None):
        dir_path = self._get_path(path)
        if not dir_path or not os.path.isdir(dir_path):
            return ""

        #uuid 3 i 5 are get same hash for the same input
        filename = filename or str(uuid.uuid5())
        full_path = os.path.join(dir_path, filename)

        with open(full_path, 'wb') as f:
            f.write(data)
        
        return os.path.basename(full_path)