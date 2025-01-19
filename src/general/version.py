from ..commands import Commands
from ..packet import Packet, PacketAck

class PacketGeneralGetExtendedVersion(Packet):

    def __init__(self):
        self.command = Commands.GetExtendedVersion


class PacketGeneralGetExtendedVersionAck(PacketAck):
    
    successful: bool
    firmwareVersion: str
    scienceModeVersion: str
    firmwareHash: int
    hashType: int
    isValidHash: bool


    def __init__(self, data: bytes):
        self.command = Commands.GetExtendedVersionAck

        if data:
            self.successful = data[0] == 0
            self.firmwareVersion = f"{data[1]}.{data[2]}.{data[3]}"
            self.scienceModeVersion = f"{data[4]}.{data[5]}.{data[6]}"
            self.firmwareHash = int.from_bytes(data[7:10], 'little')
            self.hashType = data[11]
            self.isValidHash = data[12] == 1

        
