from src.commands import Commands, ResultAndError
from src.packet import PacketAck


class PacketGeneralError(PacketAck):

    resultError: ResultAndError

    def __init__(self, data: bytes):
        self.command = Commands.GeneralError

        if (data):
            self.resultError = ResultAndError(data[0])


