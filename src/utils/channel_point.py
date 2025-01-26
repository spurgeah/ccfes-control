
from src.utils.byte_builder import ByteBuilder


class ChannelPoint():
    
    durationMicroSeconds: int
    currentMilliAmpere: int


    def __init__(self, duration_micro_seconds: int, current_milli_amper: int):
        self.durationMicroSeconds = duration_micro_seconds
        self.currentMilliAmpere = current_milli_amper


    def getData(self) -> bytes:
        c = 2 * self.currentMilliAmpere + 300
        
        bb = ByteBuilder()
        bb.set_bit_to_position(0, 0, 10)
        bb.set_bit_to_position(c, 10, 10)
        bb.set_bit_to_position(self.durationMicroSeconds, 20, 12)
        bb.swap(0, 4)
        return bb.get_bytes()
