"""Provides classes for mid level Update"""

from src.commands import Commands, ResultAndError
from src.packet import Packet, PacketAck
from src.utils.byte_builder import ByteBuilder
from src.utils.channel_configuration import MidLevelChannelConfiguration


class PacketMidLevelUpdate(Packet):
    """Packet for mid level Update"""


    def __init__(self):
        super().__init__()
        self._command = Commands.MidLevelUpdate
        self._channel_configuration: list[MidLevelChannelConfiguration] = [None] * 8


    def get_data(self) -> bytes:
        bb = ByteBuilder()
        for x in range(8):
            c: MidLevelChannelConfiguration | None = self._channel_configuration[x] if x < len(self._channel_configuration) else None
            bb.set_bit_to_position(1 if c and c.isActive else 0, x, 1)

        for x in range(8):
            c: MidLevelChannelConfiguration | None = self._channel_configuration[x] if x < len(self._channel_configuration) else None
            if c:
                bb.append_bytes(c.getData())

        return bb.get_bytes()


    def get_channel_configuration(self) -> list[MidLevelChannelConfiguration]:
        """Getter for channel configuration"""
        return self._channel_configuration


    def set_channel_configuration(self, channel_configuration: list[MidLevelChannelConfiguration]):
        """Setter for channel configuration"""
        self._channel_configuration = channel_configuration


    channel_configuration = property(get_channel_configuration, set_channel_configuration)


class PacketMidLevelUpdateAck(PacketAck):
    """Packet for mid level Update acknowledge"""


    def __init__(self, data: bytes):
        super().__init__(data)
        self._command = Commands.MidLevelUpdateAck
        self._result_error = ResultAndError.NO_ERROR

        if data:
            self._result_error = ResultAndError(data[0])


    def get_result_error(self) -> ResultAndError:
        """Getter for ResultError"""
        return self._result_error


    result_error = property(get_result_error)
