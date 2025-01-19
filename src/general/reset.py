from src.commands import Commands, ResultAndError
from src.packet import Packet, PacketAck

class PacketGeneralReset(Packet):

    def __init__(self):
        self.command = Commands.Reset


class PacketGeneralResetAck(PacketAck):

    resultError: ResultAndError


    def __init__(self, data: bytes):
        self.command = Commands.ResetAck

        if (data):
            self.resultError = ResultAndError(data[0])

        
