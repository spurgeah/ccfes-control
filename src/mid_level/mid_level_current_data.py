"""Provides packet classes for mid level GetCurrentData"""

from src.commands import Commands, ResultAndError
from src.packet import Packet, PacketAck
from src.utils.bit_vector import BitVector
from src.utils.byte_builder import ByteBuilder

class PacketMidLevelGetCurrentData(Packet):
    """Packet for mid level GetCurrentData"""

    def __init__(self):
        super().__init__()
        self._command = Commands.MidLevelGetCurrentData


    def get_data(self) -> bytes:
        bb = ByteBuilder()
        bb.append_byte(4)
        return bb.get_bytes()


class PacketMidLevelGetCurrentDataAck(PacketAck):
    """Packet for mid level GetCurrentData acknowledge"""


    def __init__(self, data: bytes):
        super().__init__(data)
        self._command = Commands.MidLevelGetCurrentDataAck
        self._result_error = ResultAndError.NO_ERROR
        self._is_stimulation_active = [False] * 8
        self._channel_error = [0] * 8

        if data:
            self._result_error = ResultAndError(data[0])
            self._is_stimulation_active = [0 if x == 0 else 1 for x in BitVector.init_from_int(data[2])]
            bb = ByteBuilder(int.from_bytes(data[3:6], 'little'))
            for x in range(self._channel_error):
                self._channel_error[x] = bb.get_bit_from_position(x * 4, 4)


    def get_result_error(self) -> ResultAndError:
        """Getter for ResultError"""
        return self._result_error


    def get_is_stimulation_active(self) -> list[bool]:
        """Getter for IsStimulationActive"""
        return self._is_stimulation_active


    def get_channel_error(self) -> list[int]:
        """Getter for ChannelError"""
        return self._channel_error


    result_error = property(get_result_error)
    is_stimulation_active = property(get_is_stimulation_active)
    channel_error = property(get_channel_error)
