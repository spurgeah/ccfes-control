"""Provides packet classes for low level stop"""

from src.commands import Commands, ResultAndError
from src.packet import Packet, PacketAck

class PacketLowLevelStop(Packet):
    """Packet for low level stop"""


    def __init__(self):
        super().__init__()
        self._command = Commands.LowLevelStop


class PacketLowLevelStopAck(PacketAck):
    """Packet for low level stop acknowledge"""


    def __init__(self, data: bytes):
        super().__init__(data)
        self._command = Commands.LowLevelStopAck
        self._result_error = ResultAndError.NO_ERROR

        if data:
            self._result_error = ResultAndError(data[0])


    @property
    def result_error(self) -> ResultAndError:
        """Getter for ResultError"""
        return self._result_error
