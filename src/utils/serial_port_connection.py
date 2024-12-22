import serial

from src.utils.connection import Connection

class SerialPortConnection(Connection):

    ser: serial.Serial

    def __init__(self, port: str):
        self.ser = serial.Serial(port, timeout = 0)

    def open(self):
        # self.ser.open()
        pass

    def close(self):
        self.ser.close()

    def isOpen(self):
        return self.ser.is_open
    
    def write(self, data: bytes):
        self.ser.write(data)

    def read(self) -> bytes:
        result = self.ser.read_all()
        if not result:
            result = []
        return result