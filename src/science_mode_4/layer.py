"""Provides base class for all ScienceMode layers"""

from .protocol.protocol_helper import ProtocolHelper
from .protocol.types import ResultAndError
from .protocol.packet import Packet, PacketAck
from .protocol.packet_factory import PacketFactory
from .protocol.packet_number_generator import PacketNumberGenerator
from .utils.connection import Connection
from .utils.packet_buffer import PacketBuffer


class Layer():
    """Base class for all layers"""


    def __init__(self, conn: Connection, packet_factory: PacketFactory, packet_number_generator: PacketNumberGenerator):
        self._connection  = conn
        self._packet_factory = packet_factory
        self._packet_number_generator = packet_number_generator

        self._packet_buffer = PacketBuffer(conn, packet_factory)


    @property
    def packet_buffer(self) -> PacketBuffer:
        """Getter for packet buffer"""
        return self._packet_buffer


    def _send_packet(self, packet: Packet):
        """Generates a new packet number and send packet"""
        ack = ProtocolHelper.send_packet(packet, self._packet_number_generator.get_next_number(),
                                         self._packet_buffer)
        return ack


    async def _send_packet_and_wait(self, packet: Packet) -> PacketAck:
        """Generates a new packet number, send packet and waits for response"""
        ack = await ProtocolHelper.send_packet_and_wait(packet, self._packet_number_generator.get_next_number(),
                                                        self._packet_buffer)
        return ack


    def _check_result_error(self, result_error: ResultAndError, packet_name: str):
        """Check if result_error contains an error and if yes prints packet_name"""
        if result_error != ResultAndError.NO_ERROR:
            raise ValueError(f"Error {packet_name} {result_error}")
