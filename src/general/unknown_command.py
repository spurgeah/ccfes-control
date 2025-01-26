"""Provides classes for general UnkownCommand"""

from src.commands import Commands, ResultAndError
from src.packet import PacketAck


class PacketGeneralUnknownCommand(PacketAck):
    """Packet for general UnknownCommand"""


    def __init__(self, data: bytes):
        super().__init__(data)
        self._command = Commands.UnkownCommand
        self._result_error = ResultAndError.NO_ERROR

        if data:
            self._result_error = ResultAndError(data[0])


    def get_result_error(self) -> ResultAndError:
        """Getter for ResultError"""
        return self._result_error


    result_error = property(get_result_error)
