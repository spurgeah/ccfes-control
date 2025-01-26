"""Provides classes for mid level Stop"""

from src.commands import Commands, ResultAndError
from src.packet import Packet, PacketAck

class PacketMidLevelStop(Packet):
    """Packet for mid level Stop"""

    def __init__(self):
        super().__init__()
        self._command = Commands.MidLevelStop


class PacketMidLevelStopAck(PacketAck):
    """Packet for mid level Stop acknowledge"""


    def __init__(self, data: bytes):
        super().__init__(data)
        self._command = Commands.MidLevelStopAck
        self._result_error = ResultAndError.NO_ERROR

        if data:
            self._result_error = ResultAndError(data[0])


    def get_result_error(self) -> ResultAndError:
        """Getter for ResultError"""
        return self._result_error


    result_error = property(get_result_error)
