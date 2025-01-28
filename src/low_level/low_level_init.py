"""Provides packet classes for low level init"""

from src.commands import Commands, ResultAndError
from src.utils.byte_builder import ByteBuilder
from src.packet import Packet, PacketAck

class PacketLowLevelInit(Packet):
    """Packet for low level init"""


    def __init__(self):
        super().__init__()
        self._command = Commands.LowLevelInit
        self._high_voltage = 0


    @property
    def high_voltage(self) -> int:
        """Getter for high voltage"""
        return self._high_voltage


    @high_voltage.setter
    def high_voltage(self, value: int):
        """Setter for high voltage"""
        self._high_voltage = value


    def get_data(self) -> bytes:
        bb = ByteBuilder()
        bb.set_bit_to_position(0, 0, 1)
        bb.set_bit_to_position(self._high_voltage, 1, 3)
        bb.set_bit_to_position(0, 4, 0)
        return bb.get_bytes()


class PacketLowLevelInitAck(PacketAck):
    """Packet for low level init acknowledge"""


    def __init__(self, data: bytes):
        super().__init__(data)
        self._command = Commands.LowLevelInitAck
        self._result_error = ResultAndError.NO_ERROR

        if data:
            self._result_error = ResultAndError(data[0])


    @property
    def result_error(self) -> ResultAndError:
        """Getter for ResultError"""
        return self._result_error
