"""Provides a class for a serial connection"""

import serial
from src.utils.connection import Connection

class SerialPortConnection(Connection):
    """Serial connection class"""


    def __init__(self, port: str):
        self._ser = serial.Serial(timeout = 0)
        self._ser.port = port


    def open(self):
        self._ser.open()


    def close(self):
        self._ser.close()


    def is_open(self) -> bool:
        return self._ser.is_open


    def write(self, data: bytes):
        self._ser.write(data)


    def read(self) -> bytes:
        result = []
        if self._ser.in_waiting > 0:
            result = self._ser.read_all()
            print(f"Incoming {len(result)} - {result.hex(' ').upper()}")
        return bytes(result)
