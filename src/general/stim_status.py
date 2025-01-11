from typing import NamedTuple
from src.commands import Commands, StimStatus
from src.packet import Packet, PacketAck

class GetStimStatusResult(NamedTuple):
    stimStatus: StimStatus
    highVoltageOn: bool


class PacketGetStimStatus(Packet):

    def __init__(self):
        self.command = Commands.GetStimStatus


class PacketGetStimStatusAck(PacketAck):

    successful: int
    stimStatus: StimStatus
    highVoltageOn: bool


    def __init__(self, data: bytes):
        self.command = Commands.GetStimStatusAck

        if (data):
            self.successful = data[0] == 0
            self.stimStatus = StimStatus(data[1])
            self.highVoltageOn = data[2] == 6

        
