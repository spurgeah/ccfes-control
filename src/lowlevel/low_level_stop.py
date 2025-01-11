from src.protocol import Protocol
from src.commands import Commands
from src.packet import Packet, PacketAck

class PacketLowLevelStop(Packet):

    def __init__(self):
        self.command = Commands.LowLevelStop


class PacketLowLevelStopAck(PacketAck):

    result: int


    def __init__(self, data: bytes):
        self.command = Commands.LowLevelStopAck



        
