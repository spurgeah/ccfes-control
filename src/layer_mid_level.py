from src.mid_level.mid_level_current_data import PacketMidLevelGetCurrentData, PacketMidLevelGetCurrentDataAck
from src.mid_level.mid_level_stop import PacketMidLevelStop, PacketMidLevelStopAck
from src.mid_level.mid_level_update import PacketMidLevelUpdate, PacketMidLevelUpdateAck
from src.utils.bit_vector import BitVector
from src.utils.channel_configuration import MidLevelChannelConfiguration
from .protocol import Protocol
from src.layer import Layer
from src.mid_level.mid_level_init import PacketMidLevelInit, PacketMidLevelInitAck
from src.packet_factory import PacketFactory
from .utils.connection import Connection


class LayerMidLevel(Layer):

    def __init__(self, conn: Connection, packet_factory: PacketFactory):
        super().__init__(conn, packet_factory)

    
    async def init(self, do_stop_on_all_errors: bool):
        p = PacketMidLevelInit()
        p.doStopOnAllErrors = do_stop_on_all_errors
        ack = await Protocol.sendPacket(p, 0, self.connection, self.factory)
        if ack:
            init_ack: PacketMidLevelInitAck = ack
            self.checkResultError(init_ack.resultError, "mid level init")


    async def stop(self):
        p = PacketMidLevelStop()
        ack = await Protocol.sendPacket(p, 0, self.connection, self.factory)
        if ack:
            stop_ack: PacketMidLevelStopAck = ack
            self.checkResultError(stop_ack.resultError, "mid level stop")


    async def update(self, channel_configuration: list[MidLevelChannelConfiguration]):
        p = PacketMidLevelUpdate()
        p.channelConfiguration = channel_configuration
        # Todo packet number
        ack = await Protocol.sendPacket(p, 1, self.connection, self.factory)
        if ack:
            update_ack: PacketMidLevelUpdateAck = ack
            self.checkResultError(update_ack.resultError, "mid level update")


    async def getCurrentData(self) -> list[bool]:
        p = PacketMidLevelGetCurrentData()
        ack = await Protocol.sendPacket(p, 0, self.connection, self.factory)
        if ack:
            current_ack: PacketMidLevelGetCurrentDataAck = ack
            self.checkResultError(current_ack.resultError, "mid level get current data")
            if (True in current_ack.channelError):
                raise ValueError(f"Error mid level get current data channel error {current_ack.channelError}")
            return current_ack.isStimulationActive
