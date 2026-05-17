import pytest
from server.serverd import Connection
from unittest.mock import MagicMock, call
from pytest import MonkeyPatch
from queue import SimpleQueue

from server import serverd

@pytest.fixture
def mockSelector():
    mockSelector = MagicMock()
    yield mockSelector

# in every test we assume that socket sends only one byte of data at the time
@pytest.fixture
def mockSock():
    mockSock = MagicMock()
    mockSock.send.return_value = 1
    yield mockSock

@pytest.fixture
def conn(mockSock):
    conn = Connection(sock=mockSock)
    conn.is_sending = True
    yield conn

@pytest.fixture
def mock_file_iterator_empty():
    
    def gen():
        for _ in []:
            yield _
            
    yield gen()

@pytest.fixture
def mock_file_iterator_filled():
    
    def gen():
        for _ in [b'\x01', b'\x01']:
            yield _
            
    yield gen()

# 0 0 0
def test_send_data_gen_list_empty_curr_gen_empty_buffer_empty(monkeypatch, mockSelector, mockSock, conn : Connection, mock_file_iterator_empty):
    """
    case when connection got first data to send -> the buffer and generator_list are empty
    """
    monkeypatch.setattr(serverd, "sel", mockSelector)   

    conn.curr_generator_buffer = mock_file_iterator_empty
    
    conn._send_data()
    
    assert conn.is_sending == False
    assert conn.send_generator_buffer_queue.empty()
    assert conn.send_buffer == b'' 
    
    assert mockSelector.method_calls == [call.modify(mockSock, 1)]

# 0 1 0
def test_send_data_gen_list_empty_curr_gen_filled_buffer_empty(monkeypatch, mockSelector, mockSock, conn : Connection, mock_file_iterator_filled):
    """
    case when current generator is filled and there is no data in buffer
    """
    
    monkeypatch.setattr(serverd, "sel", mockSelector)   

    conn.curr_generator_buffer = mock_file_iterator_filled
    
    conn._send_data()
    
    assert conn.is_sending == True
    assert conn.send_generator_buffer_queue.empty()
    assert conn.send_buffer == b''
    
    assert mockSock.method_calls == [call.send(b'\x01')]

# 0 1 1
def test_send_data_gen_list_empty_curr_gen_filled_buffer_filled(monkeypatch, mockSelector, mockSock, conn : Connection, mock_file_iterator_filled):
    
    """ 
    case when there is some data already in the buffer and current generator stil has data to send
    """
    
    monkeypatch.setattr(serverd, "sel", mockSelector)   
    
    conn.curr_generator_buffer = mock_file_iterator_filled
    conn.send_buffer = b'\x01' 
    
    conn._send_data()
    
    assert conn.is_sending == True
    assert conn.send_generator_buffer_queue.empty()
    assert conn.send_buffer == b'\x01'
    
    assert mockSock.method_calls == [call.send(b'\x01\x01')]

# 1 0 0 
def test_send_data_gen_list_filled_curr_gen_empty_buffer_empty(monkeypatch, mockSelector, mockSock, conn : Connection, mock_file_iterator_filled, mock_file_iterator_empty):
    """
    case when all data from buffer have been send, the current generator is empty but there is new generator in the q
    """
    
    monkeypatch.setattr(serverd, "sel", mockSelector)   

    conn.curr_generator_buffer = mock_file_iterator_empty
    conn.send_generator_buffer_queue = SimpleQueue()
    conn.send_generator_buffer_queue.put(mock_file_iterator_filled)
    
    conn._send_data()
    
    assert conn.is_sending == True
    assert conn.send_generator_buffer_queue.empty()
    assert conn.send_buffer == b''
    
    assert mockSock.method_calls == [call.send(b'\x01')]

# 1 0 1
def test_send_data_gen_list_filled_curr_gen_empty_buffer_filled(monkeypatch, mockSelector, mockSock, conn : Connection, mock_file_iterator_filled, mock_file_iterator_empty):
    """
    case when current generator has no more data to send, but the buffer is filled and there are more generators in queue
    """

    monkeypatch.setattr(serverd, "sel", mockSelector)   

    conn.curr_generator_buffer = mock_file_iterator_empty
    conn.send_buffer = b'\x01'
    conn.send_generator_buffer_queue = SimpleQueue()
    conn.send_generator_buffer_queue.put(mock_file_iterator_filled)
    
    conn._send_data()
    
    assert conn.is_sending == True
    assert conn.send_generator_buffer_queue.empty()
    assert conn.send_buffer == b'\x01' 
    
    assert mockSock.method_calls == [call.send(b'\x01\x01')]