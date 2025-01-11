

class Packet():
    
    command: int


    def __init__(self):
        self.command = -1


    def getCommand(self) -> int:
        return self.command


    def getData(self) -> bytes:
        return []
    

    def createCopy(self):
        return type(self)()


    def createCopyWithData(self, data: bytes):
        return type(self)(data)


class PacketAck(Packet):
    
    def setData(self, data: bytes):
        pass
