"""Provides a ByteBuilder class for easier creation of a byte stream"""

from src.utils.bit_vector import BitVector


class ByteBuilder():
    """ByteBuilder class"""


    def __init__(self, data: int = 0, byte_length: int = 0):
        self.data = BitVector.init_from_int(data, byte_length * 8)


    def get_bit_from_position(self, bit_position: int, bit_length: int) -> int:
        """Returns bits starting with bit_position and a count of bit_length"""
        result = 0
        for x in range(bit_length):
            result |= (self.data[bit_position + x] << x) & 0x1
        return result


    def append_byte(self, value: int):
        """Append a byte"""
        self._append_byte(value)


    def append_list(self, value: list[int]):
        """Extends current data with list of values (byte)"""
        for x in value:
            self._append_byte(x)


    def append_bytes(self, value: bytes):
        """Extends current data with value"""
        for x in value:
            self._append_byte(x)


    def extend_byte_builder(self, value: 'ByteBuilder'):
        """Extends current data with value"""
        self.data.extend(value.get_bytes())


    def set_bit_to_position(self, value: int, bit_position: int, bit_length: int):
        """
        Set bits starting with bit_position and a count of bit_length to value
        This method extends data to make room for value
        """
        new_length = max(len(self.data), bit_position + bit_length)
        self.data.set_length(new_length)
        for x in range(bit_length):
            self.data[bit_position + x] = (value >> x) & 0x1


    def swap(self, start: int, count: int):
        """Swap bytes by reversion order from start to start + count"""
        tmp = self.get_bytes()
        for x in range(count):
            self.set_bit_to_position(tmp[start + x], (start + count - x - 1) * 8, 8)


    def get_bytes(self) -> bytes:
        """Returns data as bytes"""
        return self.data.get_bytes()


    def clear(self):
        """Resets data"""
        self.data = BitVector()


    def __repr__(self) -> str:
        b = self.get_bytes()
        return f"{len(b)} - {b.hex(' ').upper()}"


    def __str__(self) -> str:
        b = self.get_bytes()
        return f"{len(b)} - {b.hex(' ').upper()}"


    def _append_byte(self, value: int):
        """Append value at the end of data, value is treated as byte"""
        start = len(self.data)
        self.data.set_length(start + 8)
        for x in range(8):
            self.data[start + x] = (value >> x) & 0x1
            