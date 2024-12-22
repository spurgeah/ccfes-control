from src.commands import Commands
from src.packet import Packet, PacketAck

class PacketGetDeviceId(Packet):

    def __init__(self):
        self.command = Commands.GetDeviceId


class PacketGetDeviceIdAck(PacketAck):

    error: int
    deviceId: str


    def __init__(self, data: bytes):
        self.command = Commands.GetDeviceIdAck

        if (data):
            self.error = data[0]
            self.deviceId = data[1:11].decode()

        
