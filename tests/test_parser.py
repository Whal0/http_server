import unittest
from server.exceptions import InvalidRequestException, VersionNotSupportedException
from parser import RequestHeader, RequestLine, parse_request_line, parse_header

class TestParser(unittest.TestCase):

    def test_valid_request_line(self):
        line_str = "GET /index.html HTTP/1.1"
        result = parse_request_line(line_str)
        
        self.assertIsInstance(result, RequestLine)
        self.assertEqual(result.method, "GET")
        self.assertEqual(result.url, "/index.html")
        self.assertEqual(result.version, "HTTP/1.1")

    def test_invalid_request_line_format(self):
        with self.assertRaises(InvalidRequestException):
            parse_request_line("GET /index.html")

    def test_unsupported_http_version(self):
        with self.assertRaises(VersionNotSupportedException):
            parse_request_line("GET /index.html HTTP/2.0")


    def test_valid_headers(self):
        header_str = "Host: localhost\r\nContent-Length: 123\r\nConnection: keep-alive\r\n"
        result = parse_header(header_str)
        
        self.assertIsInstance(result, RequestHeader)
        self.assertEqual(result.headers["host"], "localhost")
        self.assertEqual(result.headers["content-length"], "123")
        self.assertEqual(result.headers["connection"], "keep-alive")

    def test_case_insensitive_and_spacing(self):
        header_str = "HOST:   localhost\r\n"
        result = parse_header(header_str)
        
        self.assertIn("host", result.headers)
        self.assertEqual(result.headers["host"], "localhost")

    def test_field_order_and_multiple_values(self):
        header_str = "Host: localhost, test\r\n"
        result = parse_header(header_str)
        
        self.assertEqual(result.headers['host'], 'localhost, test')

    def test_ignores_unknown_headers(self):
        # If a header is not in consts.HEADER_FIELDS, it should be ignored
        header_str = "X-Custom-Header: secret\r\nHost: localhost\r\n"
        result = parse_header(header_str)
        
        self.assertNotIn("x-custom-header", result.headers)
        self.assertIn("host", result.headers)



    def test_parsing_with_body_boundary(self):
        request_line_str = "POST /submit HTTP/1.1"
        header_str = "Host: localhost\r\nContent-Length: 11\r\n"
        
        line_obj = parse_request_line(request_line_str)
        header_obj = parse_header(header_str)
        
        self.assertEqual(line_obj.method, "POST")
        self.assertEqual(header_obj.headers["content-length"], "11")

    # not allowed by the spec, but it works
    
    def test_whitespace_handling(self):
        request_line = "  GET /index.html HTTP/1.1  "
        result = parse_request_line(request_line)
        self.assertEqual(result.method, "GET")



if __name__ == "__main__":
    unittest.main()