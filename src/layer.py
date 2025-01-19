from src.commands import ResultAndError
from .packet_factory import PacketFactory
from .utils.connection import Connection


class Layer():

    connection: Connection
    factory: PacketFactory


    def __init__(self, conn: Connection, packet_factory: PacketFactory):
        self.connection  = conn
        self.factory = packet_factory


    def checkResultError(self, result_error: ResultAndError, packet: str):
        if result_error != ResultAndError.NO_ERROR:
            raise ValueError(f"Error {packet} {result_error}")