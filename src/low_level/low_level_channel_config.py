from src.commands import Commands, ResultAndError
from src.utils.byte_builder import ByteBuilder
from src.packet import Packet, PacketAck
from src.utils.channel_point import ChannelPoint



class PacketLowLevelChannelConfig(Packet):

    executionStimulation: int
    # 0: red, 1: blue, 2: black, 3: white
    channelSelection: int
    points: list[ChannelPoint]


    def __init__(self):
        self.command = Commands.LowLevelChannelConfig
        self.executionStimulation = 0
        self.channelSelection = 0
        self.points = []


    def get_data(self) -> bytes:
        bb = ByteBuilder()
        # Todo: check if is there at least one point
        bb.set_bit_to_position(len(self.points) - 1, 0, 4)
        bb.set_bit_to_position(0, 4, 1)
        bb.set_bit_to_position(self.channelSelection, 5, 2)
        bb.set_bit_to_position(self.executionStimulation, 7, 1)
        [(bb.extend(x.getData())) for x in self.points]

        return bb.get_bytes()


class PacketLowLevelChannelConfigAck(PacketAck):

    # resultError: ResultAndError


    def __init__(self, data: bytes):
        self.command = Commands.LowLevelChannelConfigAck
        # ToDo
        # if data:
        #     self.result = ResultAndError(data[0])
