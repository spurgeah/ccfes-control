"""Provides classes for general GetStimStatus"""

from typing import NamedTuple
from src.commands import Commands, StimStatus
from src.packet import Packet, PacketAck

class GetStimStatusResult(NamedTuple):
    """Helper class for stim result"""
    stim_status: StimStatus
    high_voltage_on: bool


class PacketGeneralGetStimStatus(Packet):
    """Packet for general GetStimStatus"""


    def __init__(self):
        super().__init__()
        self._command = Commands.GetStimStatus


class PacketGeneralGetStimStatusAck(PacketAck):
    """Packet for general GetStimStatus akcnowledge"""


    def __init__(self, data: bytes):
        super().__init__(data)
        self._command = Commands.GetStimStatusAck
        self._successful: bool = False
        self._stim_status = StimStatus.NO_LEVEL_INITIALIZED
        self._high_voltage_on: bool = False

        if data:
            self._successful = data[0] == 0
            self._stim_status = StimStatus(data[1])
            self._high_voltage_on = data[2] == 6


    def get_successful(self) -> bool:
        """Getter for Successful"""
        return self._successful


    def get_stim_status(self) -> StimStatus:
        """Getter for StimStatus"""
        return self._stim_status


    def get_high_voltage_on(self) -> bool:
        """Getter for HighVoltageOn"""
        return self._high_voltage_on


    successful = property(get_successful)
    stim_status = property(get_stim_status)
    high_voltage_on = property(get_high_voltage_on)
