from pathlib import Path
import subprocess
import time

from tests.e2e_test.client import ClientSocket
import pytest
import os
from datetime import datetime, timezone

@pytest.fixture
def client():
    client_sock = ClientSocket()
    yield client_sock
    client_sock.close()
    
@pytest.fixture
def base_dir(tmp_path : Path):
    base_d = tmp_path / "kulawykonfident"
    base_d.mkdir()
    f = base_d / "komendaplock.txt"
    f.write_text("co byś zrobił?")
    
    forbidden = base_d / "piekarz"
    
    forbidden.mkdir(mode=0o777)
    f = forbidden / "komendaplock.txt"
    f.write_text("co byś zrobił?")
    
    forbidden.chmod(mode=0o700)
    
    config = tmp_path / "config.yaml"
    config.write_text(f"base_d: {str(base_d)}")
    
    yield base_d
    
    forbidden.chmod(0o777)
    
@pytest.fixture
def server():
    process = subprocess.Popen(["python3", "-m", "server.serverd", "--config", "tests/config.yaml",  '--logfile', 'tests/logs', "--base_dir", "tests/test_public"], stdin=subprocess.PIPE, stdout=subprocess.PIPE, text=True)
    yield process
    process.terminate()
    process.wait(timeout=5)

@pytest.fixture
def server_tempdir(base_dir):
    process = subprocess.Popen(["python3", "-m", "server.serverd", "--config", "tests/config.yaml",  '--logfile', 'tests/logs', "--base_dir", str(base_dir)], stdin=subprocess.PIPE, stdout=subprocess.PIPE, text=True)
    yield process
    process.kill()
    
def test_put_e2e(client : ClientSocket, base_dir : Path, server_tempdir):
    
    request = ("PUT /kulawykonfident2.txt HTTP/1.1\r\n"
        "Connection : close\r\n"
        "Content-Length : 9\r\n\r\n"
        "pykpykpyk")
    
    expected_response = (
        "HTTP/1.1 201 Created\r\n"
        "Content-Location : /kulawykonfident2.txt\r\n\r\n"
    )
    
    time.sleep(0.5)
    
    response = client.send(request)
    
    assert response == expected_response

    assert next(base_dir.glob('kulawykonfident2.txt')).name


def test_get_e2e(client : ClientSocket, base_dir : Path, server_tempdir : subprocess.Popen):
    
    request = ("GET /komendaplock.txt HTTP/1.1\r\n"
            "Connection : close\r\n"
            "Accept : */*\r\n"
            "Accept-Language : dn\r\n\r\n")
    
    expected_response = ("HTTP/1.1 200 OK\r\n"
            "Content-Type : text/plain\r\n"
            "Content-Length : 16\r\n"
            f"Last-Modified : {datetime.fromtimestamp(os.stat(next(base_dir.glob('komendaplock.txt'))).st_mtime, tz=timezone.utc)}\r\n\r\n"
            "co byś zrobił?")
    
    time.sleep(0.5)
    
    response = client.send(request)
    
    assert response == expected_response
    

def test_head_e2e(client : ClientSocket, server_tempdir : subprocess.Popen, base_dir : Path):
    
    request = ("HEAD /komendaplock.txt HTTP/1.1\r\n"
            "Connection : close\r\n"
            "Accept : */*\r\n"
            "Accept-Language : dn\r\n\r\n")

    expected_response = ("HTTP/1.1 200 OK\r\n"
            "Content-Type : text/plain\r\n"
            "Content-Length : 16\r\n"
            f"Last-Modified : {datetime.fromtimestamp(os.stat(next(base_dir.glob('komendaplock.txt'))).st_mtime, tz=timezone.utc)}\r\n\r\n"
            )
    
    time.sleep(0.5)
    
    response = client.send(request)
    
    assert response == expected_response
    
def test_options_e2e(client : ClientSocket, server_tempdir : subprocess.Popen):
    
    request = ("OPTIONS /komendaplockt.txt HTTP/1.1\r\n"
            "Connection : close\r\n"
            "Accept : */*\r\n"
            "Accept-Language : dn\r\n\r\n")

    expected_response = ("HTTP/1.1 204 No Content\r\n"
            "Allow : GET, POST, OPTIONS, HEAD\r\n\r\n")
    
    time.sleep(0.5)
    
    response = client.send(request)
    
    assert response == expected_response

def test_unknown_method(client : ClientSocket, server_tempdir : subprocess.Popen):

    request = ("MAMMON /komendaplock.txt HTTP/1.1\r\n"
            "Connection : close\r\n"
            "Accept : */*\r\n"
            "Accept-Language : dn\r\n\r\n")

    expected_response = "HTTP/1.1 501 Not Implemented\r\n\r\n"
    
    time.sleep(0.5)
    
    response = client.send(request)
    
    assert response == expected_response
    
# def test_get_forbidden(client : ClientSocket, server_tempdir : subprocess.Popen):
    
#     request = ("GET /piekarz HTTP/1.1\r\n"
#         "Connection : close\r\n"
#         "Accept : */*\r\n"
#         "Accept-Language : dn\r\n\r\n")
    
#     expected_response = "HTTP/1.1 400 Bad Request\r\n\r\n"
    
#     time.sleep(0.5)
    
#     response = client.send(request)
    
#     assert response == expected_response
    
    
def test_get_backwardpath(client : ClientSocket, server_tempdir : subprocess.Popen):
    
    request = ("GET /../../komendaplock.txt HTTP/1.1\r\n"
        "Connection : close\r\n"
        "Accept : */*\r\n"
        "Accept-Language : dn\r\n\r\n")
    
    expected_response = "HTTP/1.1 400 Bad Request\r\n\r\n"
    
    time.sleep(0.5)
    
    response = client.send(request)
    
    assert response == expected_response
    
def test_get_nonexistent_file(client : ClientSocket, server_tempdir : subprocess.Popen):
    
    request = ("GET kulawykonfident3.txt HTTP/1.1\r\n"
        "Connection : close\r\n"
        "Accept : */*\r\n"
        "Accept-Language : dn\r\n\r\n")
    
    expected_response = "HTTP/1.1 404 Not Found\r\n\r\n"
    
    time.sleep(0.5)
    
    response = client.send(request)
    
    assert response == expected_response
    