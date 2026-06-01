import unittest
from server.util.exceptions import InvalidRequestException, VersionNotSupportedException
from server.parser.parser import parse_request_line, parse_header, extract_request_line, extract_headers, extract_body
from server.parser.request import RequestHeader, RequestLine, Request
from server.parser.response import ResponseLine, ResponseHeader, Response

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

#################################################
#EXTRACTS
    def test_extract_request_line_complete(self):
        buffer = "GET /index.html HTTP/1.1\r\nHost: localhost"
        line, remaining = extract_request_line(buffer)
        self.assertIsNotNone(line)
        self.assertEqual(line.method, "GET")
        self.assertEqual(remaining, "Host: localhost")

    def test_extract_request_line_incomplete(self):
        buffer = "GET /index.html HTTP/1.1"
        line, remaining = extract_request_line(buffer)
        self.assertIsNone(line)
        self.assertEqual(remaining, buffer)

    def test_extract_headers_complete(self):
        buffer = "Host: localhost\r\nContent-Length: 10\r\n\r\nBodyContent"
        header, remaining, length = extract_headers(buffer)
        self.assertIsNotNone(header)
        self.assertEqual(header.headers["host"], "localhost")
        self.assertEqual(length, 10)
        self.assertEqual(remaining, "BodyContent")

    def test_extract_headers_incomplete(self):
        buffer = "Host: localhost\r\nContent-Length: 10\r\n"
        header, remaining, length = extract_headers(buffer)
        self.assertIsNone(header)
        self.assertEqual(remaining, buffer)

    def test_extract_headers_no_headers(self):
        buffer = "\r\nBody"
        header, remaining, length = extract_headers(buffer)
        self.assertIsNone(header)
        self.assertEqual(remaining, "Body")

    def test_extract_headers_invalid_content_length(self):
        buffer = "Content-Length: abc\r\n\r\n"
        header, remaining, length = extract_headers(buffer)
        self.assertEqual(length, 0)

    def test_extract_body_complete(self):
        buffer = "0123456789Remaining"
        body, remaining = extract_body(buffer, 10)
        self.assertEqual(body, "0123456789")
        self.assertEqual(remaining, "Remaining")

    def test_extract_body_incomplete(self):
        buffer = "01234"
        body, remaining = extract_body(buffer, 10)
        self.assertIsNone(body)
        self.assertEqual(remaining, buffer)


##################
###EQ
    
    #NOT IMPLEMENTED
    # def test_responses_eq(self):
    #     response_line1 = ResponseLine("HTTP/1.1", 200)
    #     response_header1 = ResponseHeader({"Content-Type": "text/plain"})
    #     response1 = Response(response_line1, response_header1, "Response Body")

    #     response_line2 = ResponseLine("HTTP/1.1", 404)
    #     response_header2 = ResponseHeader({"Content-Type": "text/html"})
    #     response2 = Response(response_line2, response_header2, "Not Found")

    #     self.assertNotEqual(response1, response2)

    def test_requests_eq(self):
        request_line1 = RequestLine("GET", "/", "HTTP/1.1")
        request_header1 = RequestHeader({"Host": "localhost"})
        request1 = Request(request_line1, request_header1, "Request Body")

        request_line2 = RequestLine("POST", "/submit", "HTTP/1.1")
        request_header2 = RequestHeader({"Host": "localhost"})
        request2 = Request(request_line2, request_header2, "Request Body")

        self.assertNotEqual(request1, request2)

    def test_cross_eq(self):
        request_line = RequestLine("GET", "/", "HTTP/1.1")
        request_header = RequestHeader({"Host": "localhost"})
        request = Request(request_line, request_header, "Request Body")

        response_line = ResponseLine("HTTP/1.1", 200)
        response_header = ResponseHeader({"Content-Type": "text/plain"})
        response = Response(response_line, response_header, "Response Body")

        with self.assertRaises(TypeError):
            self.assertNotEqual(request, response)
    
    def test_request_eq_correct(self):
        request_line1 = RequestLine("GET", "/", "HTTP/1.1")
        request_header1 = RequestHeader({"Host": "localhost"})
        request1 = Request(request_line1, request_header1, "Request Body")

        request_line2 = RequestLine("GET", "/", "HTTP/1.1")
        request_header2 = RequestHeader({"Host": "localhost"})
        request2 = Request(request_line2, request_header2, "Request Body")

        self.assertEqual(request1, request2)

    #TODO: tu bug
    # def test_request_eq_correct_v2(self):
    #     request_line1 = RequestLine("GET", "/", "HTTP/1.1")
    #     request_header1 = RequestHeader({"Host": "localhost"})
    #     request1 = Request(request_line1, request_header1, "Request Body")

    #     request_line2 = RequestLine("GET", "/", "HTTP/1.1")
    #     request_header2 = RequestHeader({"Host": "localhost", "Content-Length": "42", "Connection": "keep-alive"})
    #     request2 = Request(request_line2, request_header2, "Request Body")

    #     self.assertEqual(request1, request2)

    #NOT IMPLEMENTED
    # def test_response_eq_correct(self):
    #     response_line1 = ResponseLine("HTTP/1.1", 200)
    #     response_header1 = ResponseHeader({"Content-Type": "text/plain"})
    #     response1 = Response(response_line1, response_header1, "Response Body")

    #     response_line2 = ResponseLine("HTTP/1.1", 200)
    #     response_header2 = ResponseHeader({"Content-Type": "text/plain"})
    #     response2 = Response(response_line2, response_header2, "Response Body")

    #     self.assertEqual(response1, response2)

if __name__ == "__main__":
    unittest.main()