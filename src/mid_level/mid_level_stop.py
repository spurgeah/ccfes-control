from src.commands import Commands, ResultAndError
from src.packet import Packet, PacketAck

class PacketMidLevelStop(Packet):

    def __init__(self):
        self.command = Commands.MidLevelStop


class PacketMidLevelStopAck(PacketAck):

    resultError: ResultAndError


    def __init__(self, data: bytes):
        self.command = Commands.MidLevelStopAck

        if (data):
            self.resultError = ResultAndError(data[0])


        
