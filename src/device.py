from packet_factory import PacketFactory
from utils.connection import Connection

class Device:

    connection: Connection
    factory: PacketFactory

    def __init__(self, conn: Connection):
        self.connection  = conn
        self.factory = PacketFactory()

    def f(self):
        return 'hello world'