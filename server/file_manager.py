import os
import uuid
from dataclasses import dataclass
from datetime import datetime, timezone
from server.util.consts import MIME_TYPES
from server.exceptions import FileNotFoundException, DirectoryAccessForbiddenException, NotModifiedException, FileOperationException
from hashlib import md5

@dataclass(frozen=True) #frozen for read-only
class File:
    path: str
    mime_type: str
    last_modified: datetime
    data: bytes | None
    size: int
    etag: str # for if-matching and cacheing
    is_directory: bool = False


class FileManager:
    def __init__(self, base_dir='public'):
        self.base_dir = os.path.abspath(base_dir)
        self.DEFAULT_FILES = ("index.html", "index.htm")

    def _resolve(self, path: str) -> str: # idk correct path?
        full_path = self._sanitize(path)
        full_path = os.path.abspath(os.path.join(self.base_dir, full_path))
        
        if not full_path.startswith(self.base_dir):
            raise PermissionError('backward traversal not allowed')  # 403
        
        if os.path.isdir(full_path):
            full_path = self._resolve_index(full_path)

        return full_path
    
    def _sanitize(self, path: str) -> str:
        temp_path = path.lstrip('/')
        temp_path = os.path.normcase(temp_path)
        temp_path = os.path.normpath(temp_path)
        return temp_path

    def _resolve_index(self, path: str) -> str:
        for filename in self.DEFAULT_FILES:
            temp_path = os.path.join(path, filename)
            if os.path.exists(temp_path):
                return temp_path  # 200
        
        raise DirectoryAccessForbiddenException(f'No index file found in {path}')  # 404
    
    def _get_mime_type(self, path: str, human_readable: bool = False) -> str:
        ext = os.path.splitext(path)[1].lower()
        default = 'text/plain' if human_readable else 'application/octet-stream'
        return MIME_TYPES.get(ext, default)
        
    
    def get_metadata(self, path: str) -> File: # aka HEAD
        full_path = self._resolve(path)
        metadata = self._stat(full_path)  # prolly gonna change the call stuck, creating a dict then obj is ugly
        return File(
            path=full_path,
            mime_type=metadata['mime_type'],
            last_modified=metadata['last_modified'],
            data=None,
            size=metadata['size'],
            etag=metadata['etag'],
            is_directory=metadata['is_directory']
        )  # 200

    def get_file(self, path: str, if_modified_since: datetime | None = None) -> File:
        full_path = self._resolve(path)
        metadata = self._stat(full_path)

        if if_modified_since and if_modified_since >= metadata['last_modified']:
            raise NotModifiedException()  # 304

        # get_file adds the actual file data
        data = self._read_file(full_path)
        return File(
            path=full_path,
            mime_type=metadata['mime_type'],
            last_modified=metadata['last_modified'],
            data=data,
            size=metadata['size'],
            etag=metadata['etag'],
            is_directory=metadata['is_directory']
        )  # 200

    def _read_file(self, path: str) -> bytes:
        try:
            with open(path, 'rb') as file:
                data = file.read()
                return data 
        except OSError as e:
            raise OSError(f'Failed to read file {path}: {str(e)}')  # 500
        
    def _has_access(self, path: str) -> None: # TODO: implement xD
        if not os.access(path, os.R_OK):
            raise DirectoryAccessForbiddenException(f'Access denied to {path}')  # 403 or 404 for security


    def _get_last_modified(self, path: str) -> str:
        full_path = self._resolve(path)
        
        if not os.path.exists(full_path):
            raise FileNotFoundException()  # 404
        
        try:
            mtime = os.path.getmtime(full_path)
            dt = datetime.fromtimestamp(mtime, tz=timezone.utc)
            
            # Http header format section 3.3.1
            return dt.strftime('%a, %d %b %Y %H:%M:%S GMT')  # 200
        
        except OSError as e:
            raise OSError(f'Failed to get last modified time for {path}: {str(e)}')  # 500
    
    def delete_file(self, path: str) -> None:
        full_path = self._resolve(path)
        
        if not os.path.exists(full_path):
            raise FileNotFoundException()  # 404
        
        if not os.path.isfile(full_path):
            raise FileOperationException()  # 400
        
        try:
            os.remove(full_path)  # 204
        
        except OSError as e:
            raise OSError(f'Failed to delete file {path}: {str(e)}')  # 500

    def put_file(self, path: str, data: bytes) -> bool: #not sure what alse
        full_path = self._resolve(path)
        
        try:
            os.makedirs(os.path.dirname(full_path), exist_ok=True)
            with open(full_path, 'wb') as f:
                f.write(data)
            return True  # 201 or 204
        
        except OSError as e:
            return False  # 500  / raise Os?

    # def post_file(self, path: str, data: bytes, filename: str = None):
    #     dir_path = self._get_path(path)
    #     if not dir_path or not os.path.isdir(dir_path):
    #         return ""

    #     #uuid 3 i 5 are get same hash for the same input
    #     filename = filename or str(uuid.uuid5())
    #     full_path = os.path.join(dir_path, filename)

    #     with open(full_path, 'wb') as f:
    #         f.write(data)
        
    #     return os.path.basename(full_path)

    def _stat(self, path: str) -> dict:
        try:
            stat_info = os.stat(path)
            size = stat_info.st_size
            mtime = stat_info.st_mtime
            is_dir = os.path.isdir(path)
            mime_type = self._get_mime_type(path)
            etag = self._generate_etag(size, mtime)
            
            last_modified = datetime.fromtimestamp(mtime, tz=timezone.utc)
            
            return {
                'size': size,
                'mime_type': mime_type,
                'last_modified': last_modified,
                'etag': etag,
                'is_directory': is_dir
            }  # 200
        
        except OSError as e:
            raise FileNotFoundException(f'Failed to stat file {path}: {str(e)}')  # 404
    
    def _generate_etag(self, size: int, mtime: float) -> str:
        return md5(f"{size}-{mtime}".encode()).hexdigest()  # 200
