from src.commands import Commands, ResultAndError
from src.packet import Packet, PacketAck
from src.utils.byte_builder import ByteBuilder
from src.utils.channel_configuration import MidLevelChannelConfiguration



class PacketMidLevelUpdate(Packet):

    channelConfiguration: list[MidLevelChannelConfiguration] = [None] * 8


    def __init__(self):
        self.command = Commands.MidLevelUpdate


    def getData(self) -> bytes:
        bb = ByteBuilder()
        for x in range(8):
            c: MidLevelChannelConfiguration | None = self.channelConfiguration[x] if x < len(self.channelConfiguration) else None
            bb.setToPosition(1 if c and c.isActive else 0, x, 1)

        for x in range(8):
            c: MidLevelChannelConfiguration | None = self.channelConfiguration[x] if x < len(self.channelConfiguration) else None
            if c:
                bb.extendBytes(c.getData())

        return bb.getBytes()
    

class PacketMidLevelUpdateAck(PacketAck):

    resultError: ResultAndError


    def __init__(self, data: bytes):
        self.command = Commands.MidLevelUpdateAck

        if (data):
            self.resultError = ResultAndError(data[0])

        
