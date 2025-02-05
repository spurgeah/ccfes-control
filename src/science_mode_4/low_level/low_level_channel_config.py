"""Provides packet classes for low level channel config"""

from ..protocol.commands import Commands
from .low_level_types import LowLevelMode, LowLevelResult
from ..types.types import Connector, Channel
from ..utils.byte_builder import ByteBuilder
from ..protocol.packet import Packet, PacketAck
from ..types.channel_point import ChannelPoint

class PacketLowLevelChannelConfig(Packet):
    """Packet for low level channel config"""


    def __init__(self):
        super().__init__()
        self._command = Commands.LowLevelChannelConfig
        self._execute_stimulation = False
        self._channel: Channel = Channel.RED
        self._connector: Connector = Connector.YELLOW
        self._points: list[ChannelPoint] = []


    @property
    def execute_stimulation(self) -> bool:
        """Getter for execute stimulation"""
        return self._execute_stimulation


    @execute_stimulation.setter
    def execute_stimulation(self, value: bool):
        """Setter for execute stimulation"""
        self._execute_stimulation = value


    @property
    def channel(self) -> Channel:
        """Getter for channel selection"""
        return self._channel


    @channel.setter
    def channel(self, value: Channel):
        """Setter for channel selection"""
        self._channel = value


    @property
    def connector(self) -> Connector:
        """Getter for connector"""
        return self._connector


    @connector.setter
    def connector(self, value: Connector):
        """Setter for connector"""
        self._connector = value


    @property
    def points(self) -> list[ChannelPoint]:
        """Getter for points"""
        return self._points


    @points.setter
    def points(self, value: list[ChannelPoint]):
        """Setter for points"""
        self._points = value


    def get_data(self) -> bytes:
        if (len(self._points) == 0) or (len(self._points) > 16):
            raise ValueError(f"Low level channel config must have at least 1 point and maximum 16 points {len(self._points)}")

        bb = ByteBuilder()
        bb.set_bit_to_position(len(self._points) - 1, 0, 4)
        bb.set_bit_to_position(self._connector, 4, 1)
        bb.set_bit_to_position(self._channel, 5, 2)
        bb.set_bit_to_position(1 if self._execute_stimulation else 0, 7, 1)
        for x in self._points:
            bb.append_bytes(x.get_data())

        return bb.get_bytes()


class PacketLowLevelChannelConfigAck(PacketAck):
    """Packet for low level channel config acknowledge"""

    def __init__(self, data: bytes):
        super().__init__(data)
        self._command = Commands.LowLevelChannelConfigAck
        self._result = LowLevelResult.SUCCESSFUL
        self._connector = 0
        self._channel = 0
        self._mode = LowLevelMode.NO_MEASUREMENT
        # only present when measurement is active
        self._sampling_time_in_microseconds = 0
        self._measurement_samples: list[int] = None

        if not data is None:
            bb = ByteBuilder()
            bb.append_bytes(data)
            self._result = LowLevelResult(data[0])
            self._channel = bb.get_bit_from_position(8, 4)
            self._connector = bb.get_bit_from_position(12, 4)
            self._mode = LowLevelMode(data[2])
            # only present when measurement is active
            if self._mode != LowLevelMode.NO_MEASUREMENT:
                self._sampling_time_in_microseconds = bb.get_bit_from_position(16, 16)
                self._measurement_samples = [0] * 128
                for index, _ in enumerate(self._measurement_samples):
                    self._measurement_samples[index] = bb.get_bit_from_position(32 + index * 16, 16)



    @property
    def result(self) -> LowLevelResult:
        """Getter for result"""
        return self._result


    @property
    def connector(self) -> int:
        """Getter for connector"""
        return self._connector


    @property
    def channel(self) -> int:
        """Getter for channel"""
        return self._channel


    @property
    def mode(self) -> LowLevelMode:
        """Getter for mode"""
        return self._mode
