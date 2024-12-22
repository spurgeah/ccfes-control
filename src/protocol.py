import asyncio
from src.packet_factory import PacketFactory
from src.utils.byte_builder import ByteBuilder
from src.utils.crc16 import Crc16
from src.packet import Packet, PacketAck
from src.utils.connection import Connection



class Protocol:

    StartByte = 0xF0
    StopByte: int = 0x0F
    StuffingByte: int = 0x81
    StuffingKey: int = 0x55

    async def sendPacket(packet: Packet, packet_number: int, connection: Connection, factory: PacketFactory) -> PacketAck | None:

        connection.write(Protocol.packetToBytes(packet, packet_number))

        counter = 100
        while counter > 0:
            incoming_data = connection.read()
            if Protocol.isValidPackageData(incoming_data):
                ack_data = Protocol.extractData(incoming_data)
                return factory.createPacketWithData(ack_data[0], ack_data[1])

            await asyncio.sleep(0.1)
            counter -= 1

        return None


    def packetToBytes(packet: Packet, packet_number: int) -> bytes:
        # build payload
        bb = ByteBuilder()
        # command and packet number
        bb.setToPosition(packet.getCommand(), 0, 10)
        bb.setToPosition(packet_number, 10, 6)
        # swap command and packet number to ensure little endianess
        bb.swap(0, 2)
        # append packet data
        bb.extend(packet.getData())
        # stuff packet data
        stuffed_packet_data = Protocol.stuff(bb.getBytes())

        bb.clear()

        # stop byte
        bb.append(Protocol.StartByte)
        # packet length
        packet_length: int = len(stuffed_packet_data) + 10
        bb.append(Protocol.stuffByte(packet_length >> 8))
        bb.append(Protocol.stuffByte(packet_length))
        # crc
        crc_16 = Crc16.crc16xmodem(stuffed_packet_data)
        bb.append(Protocol.stuffByte(crc_16 >> 8))
        bb.append(Protocol.stuffByte(crc_16))
        # payload
        bb.append(stuffed_packet_data)
        # stop byte
        bb.append(Protocol.StopByte)

        bb.print()
        result = bb.getBytes()
        return bytes(result)


    def isValidPackageData(data: bytes) -> bool:
        if len(data) == 0:
            return False
        
        result = True
    
        result &= len(data) > 10
        result &= data[0] == Protocol.StartByte
        result &= data[-1] == Protocol.StopByte
        packet_length = int.from_bytes([Protocol.unstuffByte(data[2]), Protocol.unstuffByte(data[4])])
        crc = int.from_bytes([Protocol.unstuffByte(data[6]), Protocol.unstuffByte(data[8])])
        result &= crc == Crc16.crc16xmodem(data[9:-1])
        return result


    def extractData(data: bytes) -> tuple[int, bytes]:
        # ToDo: take care of packet number
        command: int = int.from_bytes(Protocol.unstuff(data[9:11]))
        payload: bytes = Protocol.unstuff(data[11:-1])

        return command, payload


    def stuff(packet_data: bytes) -> bytes:
        result: bytearray = bytearray()
        for b in packet_data:
            if (b == Protocol.StartByte) or (b == Protocol.StopByte) or (b == Protocol.StuffingByte):
                result.extend(Protocol.stuffByte(b))
            else:
                result.append(b)
        
        return bytes(result)
    

    def unstuff(stuffed_packet_data: bytes) -> bytes:
        result: bytearray = bytearray()
        index: int = 0
        while index < len(stuffed_packet_data):
            if stuffed_packet_data[index] == Protocol.StuffingByte:
                index += 1
                result.append(Protocol.stuffByte(stuffed_packet_data[index]))
            else:
                result.append(stuffed_packet_data[index])

            index += 1
        
        return bytes(result)


    def stuffByte(b: int) -> bytes:
        return bytes([Protocol.StuffingByte, Protocol.StuffingKey ^ (b & 0xFF)])


    def unstuffByte(b: int) -> int:
        return Protocol.StuffingKey ^ (b & 0xFF) 
