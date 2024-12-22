from src.commands import Commands
from src.utils.byte_builder import ByteBuilder
from src.packet import Packet, PacketAck

class PacketLowLevelInit(Packet):

    highVoltage: int

    def __init__(self):
        self.command = Commands.LowLevelInit
        self.highVoltage = 0

    def getData(self) -> bytes:
        bb = ByteBuilder()
        bb.setToPosition(0, 0, 1)
        bb.setToPosition(self.highVoltage, 1, 3)
        bb.setToPosition(0, 4, 0)
        return bb.getBytes()


class PacketLowLevelInitAck(PacketAck):

    result: int

    def __init__(self, data: bytes):
        self.command = Commands.LowLevelInitAck
        if data:
            self.result = data
 