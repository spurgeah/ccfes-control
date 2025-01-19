from src.protocol import Protocol
from src.commands import Commands, ResultAndError
from src.packet import Packet, PacketAck

class PacketLowLevelStop(Packet):

    def __init__(self):
        self.command = Commands.LowLevelStop


class PacketLowLevelStopAck(PacketAck):

    resultError: ResultAndError


    def __init__(self, data: bytes):
        self.command = Commands.LowLevelStopAck
        if data:
            self.resultError = ResultAndError(data[0])


        
