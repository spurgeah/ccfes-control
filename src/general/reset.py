from src.commands import Commands, Errors
from src.packet import Packet, PacketAck

class PacketReset(Packet):

    def __init__(self):
        self.command = Commands.Reset


class PacketResetAck(PacketAck):

    error: int


    def __init__(self, data: bytes):
        self.command = Commands.ResetAck

        if (data):
            self.error = Errors(data[0])

        
