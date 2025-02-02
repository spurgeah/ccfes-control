"""Provides helper class for ScienceMode protocol"""

import asyncio
from src.protocol.commands import Commands
from src.general.general_error import PacketGeneralError
from src.general.general_unknown_command import PacketGeneralUnknownCommand
from src.protocol.packet_factory import PacketFactory
from src.utils.byte_builder import ByteBuilder
from src.utils.crc16 import Crc16
from src.protocol.packet import Packet, PacketAck
from src.utils.connection import Connection


class Protocol:
    """Helper class for ScienceMode protocol"""

    START_BYTE = 0xF0
    STOP_BYTE = 0x0F
    STUFFING_BYTE = 0x81
    STUFFING_KEY = 0x55


    @staticmethod
    def send_packet(packet: Packet, packet_number: int, connection: Connection) -> PacketAck:
        """Send a packet and returns immediately"""
        packet.number = packet_number
        connection.write(Protocol.packet_to_bytes(packet))


    @staticmethod
    async def send_packet_and_wait(packet: Packet, packet_number: int, connection: Connection, factory: PacketFactory) -> PacketAck:
        """Send a packet and wait for response"""

        Protocol.send_packet(packet, packet_number, connection)

        counter = 1000
        while counter > 0:
            incoming_data = connection.read()
            if Protocol.is_valid_packet_data(incoming_data):
                ack_data = Protocol.extract_packet_data(incoming_data)
                if packet_number != ack_data[1]:
                    raise ValueError(f"Packet number mismatch {packet_number} - {ack_data[1]}")

                ack = factory.create_packet_with_data(ack_data[0], ack_data[1], ack_data[2])
                if ack.command == Commands.GeneralError:
                    ge: PacketGeneralError = ack
                    raise ValueError(f"General error packet {ge.error}")
                elif ack.command == Commands.UnkownCommand:
                    uc: PacketGeneralUnknownCommand = ack
                    raise ValueError(f"Unknown command packet {uc.error}")
                elif ack.command != packet.command + 1:
                    raise ValueError(f"Wrong answer command packet {ack.command}")

                return ack

            await asyncio.sleep(0.01)
            counter -= 1

        raise ValueError(f"No answer for packet {packet.command}")


    @staticmethod
    def packet_to_bytes(packet: Packet) -> bytes:
        """Builds bytes from a packet"""
        # build payload
        bb = ByteBuilder()
        # command and packet number
        bb.set_bit_to_position(packet.command, 0, 10)
        bb.set_bit_to_position(packet.number, 10, 6)
        # swap command and packet number to ensure little endianess
        bb.swap(0, 2)
        # append packet data
        bb.append_bytes(packet.get_data())
        # stuff packet data
        stuffed_packet_data = Protocol.stuff(bb.get_bytes())

        bb.clear()

        # stop byte
        bb.append_byte(Protocol.START_BYTE)
        # packet length
        packet_length: int = len(stuffed_packet_data) + 10
        bb.append_bytes(Protocol.stuff_byte(packet_length >> 8))
        bb.append_bytes(Protocol.stuff_byte(packet_length))
        # crc
        crc_16 = Crc16.crc16_xmodem(stuffed_packet_data)
        bb.append_bytes(Protocol.stuff_byte(crc_16 >> 8))
        bb.append_bytes(Protocol.stuff_byte(crc_16))
        # payload
        bb.append_bytes(stuffed_packet_data)
        # stop byte
        bb.append_byte(Protocol.STOP_BYTE)

        print(f"Outgoing {bb}")
        result = bb.get_bytes()
        return bytes(result)


    @staticmethod
    def is_valid_packet_data(buffer: bytes) -> bool:
        """Checks if buffer might contain a valid packet structure, does not check if payload is valid """
        if len(buffer) == 0:
            return False

        result = True

        result &= len(buffer) > 10
        result &= buffer[0] == Protocol.START_BYTE
        result &= buffer[-1] == Protocol.STOP_BYTE
        # packet_length = int.from_bytes([Protocol.unstuffByte(data[2]), Protocol.unstuffByte(data[4])])
        crc = int.from_bytes([Protocol.unstuff_byte(buffer[6]), Protocol.unstuff_byte(buffer[8])])
        result &= crc == Crc16.crc16_xmodem(buffer[9:-1])
        return result


    @staticmethod
    def find_packet_in_buffer(buffer: bytes) -> tuple[int, int] | None:
        """Tries to find a valid packet in buffer, return start and stop index of packet if found or None otherwise"""
        start = 0
        while True:
            # Find start of packet
            # (0xF0 does not always indicate a packet start, so check additionally for stuffing byte)
            start = buffer.find([Protocol.START_BYTE, Protocol.STUFFING_BYTE], start)
            if start != -1:
                # we found a start, so use minimal packet length as starting index to find stop
                stop = buffer.find([Protocol.STOP_BYTE], start + 12)
                if stop != -1:
                    # we found a packet end, lets check if its valid
                    if Protocol.is_valid_packet_data(buffer[start:stop+1]):
                        return start, stop

                    # found packet is not valid, so check for more packets afterwards
                    start = stop
                else:
                    # we found no stop byte, so there is no complete packet in buffer
                    return None
            else:
                # we found no start byte, so there is no complete packet in buffer
                return None


    @staticmethod
    def extract_packet_data(buffer: bytes) -> tuple[int, int, bytes]:
        """Extract command, packet number and payload from buffer and returns these as tuple, buffer must contain valid packet data"""
        bb = ByteBuilder()
        bb.append_bytes(Protocol.unstuff(buffer[9:11]))
        bb.swap(0, 2)

        command = bb.get_bit_from_position(0, 10)
        nr = bb.get_bit_from_position(10, 6)
        payload = Protocol.unstuff(buffer[11:-1])

        return command, nr, payload


    @staticmethod
    def stuff(packet_data: bytes) -> bytes:
        """Stuff data"""
        result: bytearray = bytearray()
        for b in packet_data:
            if b in [Protocol.START_BYTE, Protocol.STOP_BYTE, Protocol.STUFFING_BYTE]:
                result.extend(Protocol.stuff_byte(b))
            else:
                result.append(b)

        return bytes(result)


    @staticmethod
    def unstuff(stuffed_packet_data: bytes) -> bytes:
        """Unstuff data"""
        result = bytearray()
        index: int = 0
        while index < len(stuffed_packet_data):
            if stuffed_packet_data[index] == Protocol.STUFFING_BYTE:
                index += 1
                result.append(Protocol.unstuff_byte(stuffed_packet_data[index]))
            else:
                result.append(stuffed_packet_data[index])

            index += 1

        return bytes(result)


    @staticmethod
    def stuff_byte(b: int) -> bytes:
        """Stuff a single byte"""
        return bytes([Protocol.STUFFING_BYTE, Protocol.STUFFING_KEY ^ (b & 0xFF)])


    @staticmethod
    def unstuff_byte(b: int) -> int:
        """Unstuff a byte, b must be follower of stuffing byte"""
        return Protocol.STUFFING_KEY ^ (b & 0xFF)
