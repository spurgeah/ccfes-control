"""Provides packet classes for low level stop"""

from src.protocol.commands import Commands
from src.protocol.packet import Packet, PacketAck
from src.protocol.types import ResultAndError

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

        if not data is None:
            self._result_error = ResultAndError(data[0])


    @property
    def result_error(self) -> ResultAndError:
        """Getter for ResultError"""
        return self._result_error
