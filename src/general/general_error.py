from src.commands import Commands
from src.packet import PacketAck


class PacketGeneralError(PacketAck):

    error: int

    def __init__(self, data: bytes):
        self.command = Commands.GeneralError

        if (data):
            self.error = data[0]


