import math

class BitVector:

    def __init__(self, value=0):
        self.value = value
        self._length = value.bit_length()


    def __getitem__(self, index):
        return bool((self.value >> index) & 0b01)
    

    def __setitem__(self, index, value):
        if not value in {0, 1}:
            raise ValueError(f"There's no such thing as {value}")
        if value:
            self.value |= 1 << index
        else:
            self.value &= ~(1 << index)

        self._length = max(self._length, index+1)


    def __len__(self):
        'Mostly advisory'
        return self._length
    

    def extend(self, value: bytes):
        start = self._length
        value_len = len(value) * 8

        for x in range(value_len):
            c = math.floor(x / 8)
            shift = x % 8
            self[start + x] = (value[c] >> shift) & 0x1


    def getBytes(self) -> bytes:
        result = bytearray()
        position = 0

        value = 0
        bit_counter = 0
        while position < self._length:
            if bit_counter == 8:
                result.append(value)
                value = 0
                bit_counter = 0

            value |= self[position] << bit_counter
            position += 1
            bit_counter += 1
        
        if bit_counter > 0:
            result.append(value)

        return bytes(result)


    def __repr__(self):
        return f"{type(self).__name__}(0b{self.value: _b})"


    def __str__(self):
        return '0b' + format(self.value, '_b')