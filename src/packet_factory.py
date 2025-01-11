from src.packet import Packet, PacketAck

class PacketFactory:

    data = {}


    def __init__(self):
        for x in Packet.__subclasses__():
            print(f"Register type {x.__name__}")
            self.registerPacket(x())

        for x in PacketAck.__subclasses__():
            print(f"Register type {x.__name__}")
            self.registerPacket(x(None))


    def registerPacket(self, packet: Packet):
        self.data[packet.getCommand()] = packet


    def createPacket(self, command: int) -> Packet:
        return self.data[command].createCopy()


    def createPacketWithData(self, command: int, data: bytes) -> Packet:
        # return copy.deepcopy(self.data[command])
        return self.data[command].createCopyWithData(data)
