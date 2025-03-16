"""Provices low level layer"""

from ..protocol.channel_point import ChannelPoint
from ..protocol.types import Channel, Connector
from ..utils.packet_buffer import PacketBuffer
from ..protocol.packet_number_generator import PacketNumberGenerator
from ..protocol.packet_factory import PacketFactory
from ..utils.connection import Connection
from ..layer import Layer
from ..protocol.protocol import Protocol
from .dyscom_init import PacketDyscomInit, PacketDyscomInitAck, DyscomInitParams


class LayerDyscom(Layer):
    """
    Class for dyscom layer
    """


    def __init__(self, conn: Connection, packet_factory: PacketFactory, packet_number_generator: PacketNumberGenerator):
        super().__init__(conn, packet_factory, packet_number_generator)
        self._packet_buffer = PacketBuffer(packet_factory)


    @property
    def packet_buffer(self) -> PacketBuffer:
        """Getter for packet buffer"""
        return self._packet_buffer


    async def init(self, params = DyscomInitParams()):
        """Send dyscom init command and waits for response"""
        p = PacketDyscomInit(params)
        ack: PacketDyscomInitAck = await Protocol.send_packet_and_wait(p, self._packet_number_generator.get_next_number(),
                                                                         self._connection, self._packet_factory)
        self.check_result_error(ack.result_error, "DyscomInit")


    # async def stop(self):
    #     """Send low level stop command and waits for response"""
    #     p = PacketLowLevelStop()
    #     ack: PacketLowLevelStopAck = await Protocol.send_packet_and_wait(p, self._packet_number_generator.get_next_number(),
    #                                                                     self._connection, self._packet_factory)
    #     self.check_result_error(ack.result_error, "LowLevelStop")


    # def send_init(self, mode: LowLevelMode, high_voltage_source: LowLevelHighVoltageSource):
    #     """Send low level init command"""
    #     p = PacketLowLevelInit()
    #     p.mode = mode
    #     p.high_voltage_source = high_voltage_source
    #     Protocol.send_packet(p, self._packet_number_generator.get_next_number(),
    #                          self._connection,)
    #     self._packet_buffer.add_open_acknowledge(p)


    # def send_channel_config(self, execute_stimulation: bool, channel: Channel,
    #                         connector: Connector, points: list[ChannelPoint]):
    #     """Send low level channel config command"""
    #     p = PacketLowLevelChannelConfig()
    #     p.execute_stimulation = execute_stimulation
    #     p.channel = channel
    #     p.connector = connector
    #     p.points = points
    #     Protocol.send_packet(p, self._packet_number_generator.get_next_number(),
    #                          self._connection)
    #     self._packet_buffer.add_open_acknowledge(p)


    # def send_stop(self):
    #     """Send low level stop command"""
    #     p = PacketLowLevelStop()
    #     Protocol.send_packet(p, self._packet_number_generator.get_next_number(),
    #                          self._connection)
    #     self._packet_buffer.add_open_acknowledge(p)
