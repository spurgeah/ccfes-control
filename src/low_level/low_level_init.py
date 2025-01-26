from src.commands import Commands, ResultAndError
from src.utils.byte_builder import ByteBuilder
from src.packet import Packet, PacketAck

class PacketLowLevelInit(Packet):

    highVoltage: int


    def __init__(self):
        self.command = Commands.LowLevelInit
        self.highVoltage = 0


    def get_data(self) -> bytes:
        bb = ByteBuilder()
        bb.set_bit_to_position(0, 0, 1)
        bb.set_bit_to_position(self.highVoltage, 1, 3)
        bb.set_bit_to_position(0, 4, 0)
        return bb.get_bytes()


class PacketLowLevelInitAck(PacketAck):

    resultError: ResultAndError


    def __init__(self, data: bytes):
        self.command = Commands.LowLevelInitAck
        if data:
            self.resultError = ResultAndError(data[0])
 