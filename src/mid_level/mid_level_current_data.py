from src.commands import Commands, ResultAndError
from src.packet import Packet, PacketAck
from src.utils.bit_vector import BitVector
from src.utils.byte_builder import ByteBuilder

class PacketMidLevelGetCurrentData(Packet):

    def __init__(self):
        self.command = Commands.MidLevelGetCurrentData


    def getData(self) -> bytes:
        bb = ByteBuilder()
        bb.append(4)
        return bb.getBytes()


class PacketMidLevelGetCurrentDataAck(PacketAck):

    resultError: ResultAndError
    isStimulationActive: list[bool] = [False] * 8
    channelError: list[int] = [0] * 8


    def __init__(self, data: bytes):
        self.command = Commands.MidLevelGetCurrentDataAck

        if (data):
            self.resultError = ResultAndError(data[0])
            self.isStimulationActive = [0 if x == 0 else 1 for x in BitVector(data[2])]
            bb = ByteBuilder(int.from_bytes(data[3:6], 'little'))
            for x in range(self.channelError):
                self.channelError[x] = bb.getFromPosition(x * 4, 4)


        
