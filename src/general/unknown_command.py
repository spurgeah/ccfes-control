from src.commands import Commands
from src.packet import PacketAck


class PacketUnknownCommand(PacketAck):

    error: int

    def __init__(self, data: bytes):
        self.command = Commands.UnkownCommand

        if (data):
            self.error = data[0]