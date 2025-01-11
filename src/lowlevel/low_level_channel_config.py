from src.commands import Commands
from src.utils.byte_builder import ByteBuilder
from src.packet import Packet, PacketAck

class LowLevelChannelPoint():
    duration: int
    current: int


    def __init__(self, _duration: int, _current: int):
        self.duration = _duration
        self.current = _current


    def getData(self) -> bytes:
        c = 2 * self.current + 300
        
        bb = ByteBuilder()
        bb.setToPosition(0, 0, 10)
        bb.setToPosition(c, 10, 10)
        bb.setToPosition(self.duration, 20, 12)
        bb.swap(0, 4)
        return bb.getBytes()


class PacketLowLevelChannelConfig(Packet):

    executionStimulation: int
    # 0: red, 1: blue, 2: black, 3: white
    channelSelection: int
    points: list[LowLevelChannelPoint]


    def __init__(self):
        self.command = Commands.LowLevelChannelConfig
        self.executionStimulation = 0
        self.channelSelection = 0
        self.points = []


    def getData(self) -> bytes:
        bb = ByteBuilder()
        # Todo: check if is there at least one point
        bb.setToPosition(len(self.points) - 1, 0, 4)
        bb.setToPosition(0, 4, 1)
        bb.setToPosition(self.channelSelection, 5, 2)
        bb.setToPosition(self.executionStimulation, 7, 1)
        [(bb.extend(x.getData())) for x in self.points]

        return bb.getBytes()


class PacketLowLevelChannelConfigAck(PacketAck):

    result: int


    def __init__(self, data: bytes):
        self.command = Commands.LowLevelChannelConfigAck
        if data:
            self.result = data
