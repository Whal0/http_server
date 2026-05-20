from typing import Dict, Optional

class Header:
    def __init__(self, headers : Dict[str, str]):
        self.headers = headers
    
    def __str__(self):
        return "".join(f"{k} : {v}\r\n" for k, v in self.headers.items()) + "\r\n"

    def __eq__(self, other):
        if isinstance(other, Header):
            return self.headers == other.headers

        raise TypeError(f"= not supported between instances of '{self.__class__}' and '{type(other)}'")
        
class Message:
    def __init__(self, line,  header : Header, body : Optional[str]):
        self.line = line
        self.header = header
        self.body = body

    def __str__(self):
        return str(self.line) + str(self.header) + str(self.body)

    def __eq__(self, other):
        if isinstance(other, Message):
            if not self.line == other.line:
                print(f"{self.line} is not equal to {other.line}")
                return False
            if not self.header == other.header:
                print(f"{self.header}\n is not equal to \n\n{other.header}")
                return False
            if not self.body == other.body:
                print(f"{self.body} is not equal to {other.body}")
                return False
            return True
        
        raise TypeError(f"= not supported between instances of '{self.__class__}' and '{type(other)}'")

