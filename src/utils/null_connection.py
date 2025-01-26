from src.utils.connection import Connection

class NullConnection(Connection):

    isOpen: bool = False

    def __init__(self):
        pass

    def open(self):
        self.isOpen = True


    def close(self):
        self.isOpen = False


    def isOpen(self):
        return self.isOpen
    

    def write(self, data: bytes):
        pass


    def read(self) -> bytes:
        result = []
        return bytes(result)