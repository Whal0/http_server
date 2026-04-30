# HTTP Server

## Overview

HTTP Server is a lightweight, HTTP/1.1-compliant server designed only with Python's built-in libraries. It provides a foundation for building web applications, APIs, or serving static content. It uses Python's `socket` module for low-level network communication and `selectors` for efficient I/O multiplexing.

## Features

- **HTTP/1.1 Compliance**: Fully compliant with the HTTP/1.1 specification.
- **Built-in Session Management**: Manage user sessions seamlessly.
- **File Management**: Serve static files with ease.
- **Lightweight and Dependency-Free**: Built entirely with Python's standard library, eliminating the need for external dependencies.
- **Concurrency Support**: Efficiently handles multiple client connections using non-blocking I/O.

## Installation and Setup

1. Clone the repository:

   ```bash
   git clone https://github.com/yourusername/http_server.git
   ```

2. Navigate to the project directory:

   ```bash
   cd http_server
   ```


3. To start the server, run:

    ```bash
    python server/serverd.py
    ```

The server will start on `http://localhost:8000` by default. You can configure the port and other settings in the `serverd.py` file.

## Testing

Testing is handled using the `pytest` framework. The test suite includes unit tests for individual components and integration tests to ensure the server functions correctly as a whole.

Run the test suite using:

```bash
pytest
```

Ensure all tests pass before deploying or making changes.

## Roadmap

- Keep-alive connections and HTTP pipelining support. 
- Chunked transfer encoding support.
- Implement logging and monitoring features.
- Enhance error handling and reporting.
- Provide detailed documentation and examples.

