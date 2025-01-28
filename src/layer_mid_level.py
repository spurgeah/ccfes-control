"""Provices mid level layer"""

from src.mid_level.mid_level_current_data import PacketMidLevelGetCurrentData, PacketMidLevelGetCurrentDataAck
from src.mid_level.mid_level_stop import PacketMidLevelStop, PacketMidLevelStopAck
from src.mid_level.mid_level_update import PacketMidLevelUpdate, PacketMidLevelUpdateAck
from src.mid_level.mid_level_types import MidLevelChannelConfiguration
from src.layer import Layer
from src.mid_level.mid_level_init import PacketMidLevelInit, PacketMidLevelInitAck
from .protocol.protocol import Protocol


class LayerMidLevel(Layer):
    """Class for mid level layer"""


    async def init(self, do_stop_on_all_errors: bool):
        """Send mid level init command and waits for response"""
        p = PacketMidLevelInit()
        p.do_stop_on_all_errors = do_stop_on_all_errors
        ack = await Protocol.send_packet(p, self._packet_number_generator.get_next_number(), self._connection, self._packet_factory)
        if ack:
            init_ack: PacketMidLevelInitAck = ack
            self.check_result_error(init_ack.result_error, "mid level init")


    async def stop(self):
        """Send mid level stop command and waits for response"""
        p = PacketMidLevelStop()
        ack = await Protocol.send_packet(p, self._packet_number_generator.get_next_number(), self._connection, self._packet_factory)
        if ack:
            stop_ack: PacketMidLevelStopAck = ack
            self.check_result_error(stop_ack.result_error, "mid level stop")


    async def update(self, channel_configuration: list[MidLevelChannelConfiguration]):
        """Send mid level update command and waits for response"""
        p = PacketMidLevelUpdate()
        p.channel_configuration = channel_configuration
        ack = await Protocol.send_packet(p, self._packet_number_generator.get_next_number(), self._connection, self._packet_factory)
        if ack:
            update_ack: PacketMidLevelUpdateAck = ack
            self.check_result_error(update_ack.result_error, "mid level update")


    async def get_current_data(self) -> list[bool]:
        """Send mid level get current data command and waits for response"""
        p = PacketMidLevelGetCurrentData()
        ack = await Protocol.send_packet(p, self._packet_number_generator.get_next_number(), self._connection, self._packet_factory)
        if ack:
            current_ack: PacketMidLevelGetCurrentDataAck = ack
            self.check_result_error(current_ack.result_error, "mid level get current data")
            if True in current_ack.channelError:
                raise ValueError(f"Error mid level get current data channel error {current_ack.channel_error}")
            return current_ack.is_stimulation_active
