from src.commands import Commands, ResultAndError
from src.packet import Packet, PacketAck
from src.utils.byte_builder import ByteBuilder

class PacketMidLevelInit(Packet):

    doStopOnAllErrors: bool


    def __init__(self):
        self.command = Commands.MidLevelInit


    def getData(self) -> bytes:
        bb = ByteBuilder()
        bb.append(1 if self.doStopOnAllErrors else 0)
        return bb.getBytes()
    

class PacketMidLevelInitAck(PacketAck):

    resultError: ResultAndError


    def __init__(self, data: bytes):
        self.command = Commands.MidLevelInitAck

        if (data):
            self.resultError = ResultAndError(data[0])

        
