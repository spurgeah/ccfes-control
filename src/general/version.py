from protocol import Protocol
from commands import Commands
from packet import Packet, PacketAck

class PacketVersion(Packet):

    def __init__(self):
        self.command = Commands.GetVersionMain


class PacketVersionAck(PacketAck):
    
    def __init__(self, data: bytes):
        self.command = Commands.GetVersionMainAck

        
