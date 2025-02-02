"""Provides classes for mid level Update"""

from src.protocol.commands import Commands
from src.protocol.packet import Packet, PacketAck
from src.protocol.types import ResultAndError
from src.utils.byte_builder import ByteBuilder
from src.mid_level.mid_level_types import MidLevelChannelConfiguration


class PacketMidLevelUpdate(Packet):
    """Packet for mid level Update"""


    def __init__(self):
        super().__init__()
        self._command = Commands.MidLevelUpdate
        self._channel_configuration: list[MidLevelChannelConfiguration] = [None] * 8


    @property
    def channel_configuration(self) -> list[MidLevelChannelConfiguration]:
        """Getter for channel configuration"""
        return self._channel_configuration


    @channel_configuration.setter
    def channel_configuration(self, channel_configuration: list[MidLevelChannelConfiguration]):
        """Setter for channel configuration"""
        self._channel_configuration = channel_configuration


    def get_data(self) -> bytes:
        bb = ByteBuilder()
        for x in range(8):
            c: MidLevelChannelConfiguration | None = self._channel_configuration[x] if x < len(self._channel_configuration) else None
            bb.set_bit_to_position(1 if c and c.is_active else 0, x, 1)

        for x in range(8):
            c: MidLevelChannelConfiguration | None = self._channel_configuration[x] if x < len(self._channel_configuration) else None
            if c:
                bb.append_bytes(c.get_data())

        return bb.get_bytes()


class PacketMidLevelUpdateAck(PacketAck):
    """Packet for mid level Update acknowledge"""


    def __init__(self, data: bytes):
        super().__init__(data)
        self._command = Commands.MidLevelUpdateAck
        self._result_error = ResultAndError.NO_ERROR

        if not data is None:
            self._result_error = ResultAndError(data[0])


    @property
    def result_error(self) -> ResultAndError:
        """Getter for ResultError"""
        return self._result_error
