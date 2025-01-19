from src.commands import Commands, ResultAndError
from src.packet import PacketAck


class PacketGeneralUnknownCommand(PacketAck):

    resultError: ResultAndError

    def __init__(self, data: bytes):
        self.command = Commands.UnkownCommand

        if (data):
            self.resultError = ResultAndError(data[0])