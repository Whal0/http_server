import shutil
import unittest
import os
import datetime
import tempfile
from server.file_manager import FileManager
from server.parser import Response

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
            f.write(b"test content")

    def tearDown(self):
        for item in os.listdir(self.base_test_dir):
            item_path = os.path.join(self.base_test_dir, item)
            if os.path.isfile(item_path) or os.path.islink(item_path):
                os.unlink(item_path)
            elif os.path.isdir(item_path):
                shutil.rmtree(item_path)
    
    

    def test_get_file_success(self):
        status, mime, data = self.file_manager.get_file(self.test_filename)
        
        self.assertEqual(status, '200')
        self.assertEqual(mime, 'text/plain')
        self.assertEqual(data, b"test content")

    def test_get_file_not_found(self):
        result = self.file_manager.get_file("ghost_file.txt")
        self.assertEqual(result, 404)

    def test_get_file_forbidden_directory(self):
        sub_dir_name = "empty_dir"
        os.mkdir(os.path.join(self.base_test_dir, sub_dir_name))
        
        result = self.file_manager.get_file(sub_dir_name)
        self.assertEqual(result, 403)

    def test_get_file_modified_since(self):
        stats = os.stat(self.test_file_path)
        mtime = stats.st_mtime
        
        # Test 304
        future_date = mtime + 10000 
        result = self.file_manager.get_file(self.test_filename, if_modified_since=future_date)
        self.assertEqual(result, 304)

    def test_put_file(self):
        data = b"updated"
        filename = "put_test.txt"
        
        success = self.file_manager.put_file(filename, data)
        self.assertTrue(success)
        
        with open(os.path.join(self.base_test_dir, filename), "rb") as f:
            self.assertEqual(f.read(), data)

    def test_delete_file(self):
        self.assertTrue(self.file_manager.delete_file(self.test_filename))
        self.assertFalse(os.path.exists(self.test_file_path))
        
        self.assertFalse(self.file_manager.delete_file("already_gone.txt"))

    def test_post_file(self):
        data = b"posted data"
        custom_name = "data.bin"
        
        returned_name = self.file_manager.post_file(".", data, filename=custom_name)
        
        self.assertEqual(returned_name, custom_name)
        full_path = os.path.join(self.base_test_dir, returned_name)
        self.assertTrue(os.path.exists(full_path))

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
            
        status, mime, data = self.file_manager.get_file(sub_dir_name)
        self.assertEqual(status, '200')
        self.assertEqual(data, index_content)

    def test_get_file_modified_since_is_older(self):
        stats = os.stat(self.test_file_path)
        mtime = stats.st_mtime
        
        past_date = mtime - 10000 
        status, mime, data = self.file_manager.get_file(self.test_filename, if_modified_since=past_date)
        
        self.assertEqual(status, '200')
        self.assertEqual(data, b"test content")

    def test_get_last_modified_format(self):
        last_modified = self.file_manager.get_last_modified(self.test_filename)
        
        self.assertIsNotNone(last_modified)
        self.assertTrue(last_modified.endswith("GMT"))
        self.assertIn(",", last_modified) 

    def test_get_last_modified_not_found(self):
        last_modified = self.file_manager.get_last_modified("ullululu.jpg")
        self.assertIsNone(last_modified)

    def test_put_file_nested_directories(self):
        nested_filename = "a/b/c/file.txt"
        data = b"nested data"
        
        success = self.file_manager.put_file(nested_filename, data)
        self.assertTrue(success)
        
        expected_path = os.path.join(self.base_test_dir, "a", "b", "c", "file.txt")
        self.assertTrue(os.path.exists(expected_path))
        with open(expected_path, "rb") as f:
            self.assertEqual(f.read(), data)

if __name__ == "__main__":
    unittest.main()