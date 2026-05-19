import shutil
import unittest
import os
import datetime
import tempfile
from server.file_manager import FileManager
from server.exceptions import FileNotFoundException, DirectoryAccessForbiddenException, NotModifiedException

class TestFileManager(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.base_test_dir = os.path.abspath("test_dir")
        if not os.path.exists(cls.base_test_dir):
            os.makedirs(cls.base_test_dir)

    @classmethod
    def tearDownClass(cls):
        if os.path.exists(cls.base_test_dir):
            shutil.rmtree(cls.base_test_dir)

    def setUp(self):
        self.file_manager = FileManager(base_dir=self.base_test_dir)
        
        self.test_filename = "test_file.txt"
        self.test_file_path = os.path.join(self.base_test_dir, self.test_filename)
        with open(self.test_file_path, "wb") as f:
            f.write(b"test")

    def tearDown(self):
        for item in os.listdir(self.base_test_dir):
            item_path = os.path.join(self.base_test_dir, item)
            if os.path.isfile(item_path) or os.path.islink(item_path):
                os.unlink(item_path)
            elif os.path.isdir(item_path):
                shutil.rmtree(item_path)
    
    

    def test_get_file_success(self):
        file = self.file_manager.get_file(self.test_filename)
        
        self.assertEqual(file.mime_type, 'text/plain')
        self.assertEqual(b''.join(file.data), b"test")
        self.assertEqual(file.size, len(b"test"))
        self.assertFalse(file.is_directory)

    def test_get_file_large_file_chunks(self):
        large_filename = "large_file.txt"
        large_file_path = os.path.join(self.base_test_dir, large_filename)
        # Create a file larger than default chunk size (8192)
        large_data = b"A" * 10000
        with open(large_file_path, "wb") as f:
            f.write(large_data)
        
        file = self.file_manager.get_file(large_filename)
        
        self.assertEqual(file.mime_type, 'text/plain')
        self.assertEqual(b''.join(file.data), large_data)
        self.assertEqual(file.size, len(large_data))

    def test_get_file_not_found(self):
        with self.assertRaises(FileNotFoundException):
            self.file_manager.get_file("ghost_file.txt")

    def test_get_file_forbidden_directory(self):
        sub_dir_name = "empty_dir"
        os.mkdir(os.path.join(self.base_test_dir, sub_dir_name))
        
        with self.assertRaises(DirectoryAccessForbiddenException):
            self.file_manager.get_file(sub_dir_name)

    def test_get_file_modified_since(self):
        stats = os.stat(self.test_file_path)
        mtime = stats.st_mtime
        
        # Test 304 - file not modified
        future_date = datetime.datetime.fromtimestamp(mtime + 10000, tz=datetime.timezone.utc)
        with self.assertRaises(NotModifiedException):
            self.file_manager.get_file(self.test_filename, if_modified_since=future_date)

    def test_put_file(self):
        data = b"updated"
        filename = "put_test.txt"
        
        # Should not raise exception
        self.file_manager.put_file(filename, data)
        
        with open(os.path.join(self.base_test_dir, filename), "rb") as f:
            self.assertEqual(f.read(), data)

    def test_delete_file(self):
        # Should not raise exception
        self.file_manager.delete_file(self.test_filename)
        self.assertFalse(os.path.exists(self.test_file_path))
        
        # Should raise exception for non-existent file
        with self.assertRaises(FileNotFoundException):
            self.file_manager.delete_file("already_gone.txt")

    def test_path_traversal_prevention(self):
        with self.assertRaises(PermissionError):
            self.file_manager.get_file("../../../sekret/sekrest")

    def test_get_file_directory_index_success(self):
        sub_dir_name = "www"
        sub_dir_path = os.path.join(self.base_test_dir, sub_dir_name)
        os.mkdir(sub_dir_path)
        
        index_content = b"<h1>Hello World</h1>"
        with open(os.path.join(sub_dir_path, "index.html"), "wb") as f:
            f.write(index_content)
            
        file_obj = self.file_manager.get_file(sub_dir_name)
        self.assertEqual(b''.join(file_obj.data), index_content)

    def test_get_file_modified_since_is_older(self):
        stats = os.stat(self.test_file_path)
        mtime = stats.st_mtime
        
        past_date = datetime.datetime.fromtimestamp(mtime - 10000, tz=datetime.timezone.utc)
        file_obj = self.file_manager.get_file(self.test_filename, if_modified_since=past_date)
        
        self.assertEqual(b''.join(file_obj.data), b"test")

    def test_get_last_modified_format(self):
        path = self.file_manager._resolve(self.test_filename)
        last_modified = self.file_manager._get_last_modified(path)
        
        self.assertIsNotNone(last_modified)
        self.assertTrue(last_modified.endswith("GMT"))
        self.assertIn(",", last_modified) 

    def test_get_last_modified_not_found(self):
        with self.assertRaises(FileNotFoundException):
            self.file_manager._get_last_modified("ullululu.jpg")

    def test_put_file_nested_directories(self):
        nested_filename = "a/b/c/file.txt"
        data = b"nested data"
        
        # Should not raise exception
        self.file_manager.put_file(nested_filename, data)
        
        expected_path = os.path.join(self.base_test_dir, "a", "b", "c", "file.txt")
        self.assertTrue(os.path.exists(expected_path))
        with open(expected_path, "rb") as f:
            self.assertEqual(f.read(), data)

    def test_get_metadata(self):
        metadata = self.file_manager.get_metadata(self.test_filename)
        
        self.assertEqual(metadata.mime_type, 'text/plain')
        self.assertEqual(metadata.size, len(b"test"))
        self.assertIsNone(metadata.data)
        self.assertFalse(metadata.is_directory)

if __name__ == "__main__":
    unittest.main()