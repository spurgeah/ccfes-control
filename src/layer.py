from .packet_factory import PacketFactory
from .utils.connection import Connection


class Layer():

    connection: Connection
    factory: PacketFactory


    def __init__(self, conn: Connection, packet_factory: PacketFactory):
        self.connection  = conn
        self.factory = packet_factory
