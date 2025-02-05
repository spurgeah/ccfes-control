"""Provides a packet buffer functionality for more async handling of packets and acknowledges"""

from ..protocol.packet import Packet
from ..protocol.packet_factory import PacketFactory
from ..protocol.protocol import Protocol

class PacketBuffer():
    """Class for handling a buffer and provides methods to take care of arriving acknowledges"""

    def __init__(self, packet_factory: PacketFactory):
        self._buffer: bytes = []
        self._open_acknowledges: dict[tuple[int, int], int] = {}
        self._packet_factory = packet_factory


    def append_bytes_to_buffer(self, buffer: bytes):
        """Appends buffer to internal buffer"""
        self._buffer += buffer


    def add_open_acknowledge(self, packet: Packet):
        """Adds packet to list of packets, that are waiting for a acknowledge"""
        self._open_acknowledges[packet.command, packet.number] += 1


    def get_packet_from_buffer(self) -> Packet | None:
        """
        Search for a valid packet in buffer and returns found packet. Does adjust internal buffer accordingly.
        Returns None if no valid packet was found
        """
        start_stop = Protocol.find_packet_in_buffer(self._buffer)
        if start_stop is None:
            return None

        packet_data = self._buffer[start_stop[0]: start_stop[1] + 1]
        ack_data = Protocol.extract_packet_data(packet_data)
        # check if we wait for this acknowledge
        wait_ack = self._open_acknowledges.get([ack_data[0], ack_data[1]])
        if wait_ack is None:
            print(f"Unexpected acknowledge command {wait_ack[0]}, number {wait_ack[1]}")
        else:
            self._open_acknowledges[ack_data[0], ack_data[1]] -= 1

        ack = self._packet_factory.create_packet_with_data(ack_data[0], ack_data[1], ack_data[2])
        return ack
