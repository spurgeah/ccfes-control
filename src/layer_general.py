"""Provices general layer"""

import asyncio
from typing import NamedTuple

from src.commands import StimStatus
from src.general.reset import PacketGeneralReset, PacketGeneralResetAck
from src.general.stim_status import GetStimStatusResult, PacketGeneralGetStimStatus, PacketGeneralGetStimStatusAck
from .general.device_id import PacketGeneralGetDeviceId, PacketGeneralGetDeviceIdAck
from .general.version import PacketGeneralGetExtendedVersion, PacketGeneralGetExtendedVersionAck
from .packet_factory import PacketFactory
from .utils.connection import Connection
from .layer import Layer
from .protocol import Protocol


class LayerGeneral(Layer):
    """Class for general layer"""


    def __init__(self, conn: Connection, packet_factory: PacketFactory):
        super().__init__(conn, packet_factory)
        self._device_id: str | None = None
        self._firmware_version: str | None = None
        self._science_mode_version: str | None = None


    @property
    def device_id(self) -> str | None:
        """Getter for device id"""
        return self._device_id


    @property
    def firmware_version(self) -> str | None:
        """Getter for firmware version"""
        return self._firmware_version


    @property
    def science_mode_version(self) -> str | None:
        """Getter for science mode version"""
        return self._science_mode_version


    async def initialize(self):
        """Calls initialze commands"""
        await self.get_device_id()
        await self.get_version()


    async def get_device_id(self) -> str:
        """Send get device id command and waits for response"""
        p = PacketGeneralGetDeviceId()
        ack = await Protocol.send_packet(p, 0, self._connection, self._factory)
        if ack:
            dgi_ack: PacketGeneralGetDeviceIdAck = ack
            self.check_result_error(dgi_ack.result_error, "GetDeviceId")
            self._device_id = dgi_ack.device_id
            return self._device_id


    async def reset(self):
        """Sends reset command and waits for response"""
        p = PacketGeneralReset()
        ack = await Protocol.send_packet(p, 0, self._connection, self._factory)
        if ack:
            reset_ack: PacketGeneralResetAck = ack
            self.check_result_error(reset_ack.resultError, "Reset")


    async def get_stim_status(self) -> GetStimStatusResult:
        """Sends get stim status and waits for response"""
        p = PacketGeneralGetStimStatus()
        ack = await Protocol.send_packet(p, 0, self._connection, self._factory)
        if ack:
            gss_ack: PacketGeneralGetStimStatusAck = ack
            if not gss_ack.successful:
                raise ValueError("Error get stim status")
            return GetStimStatusResult(gss_ack.stim_status, gss_ack.high_voltage_on)


    async def get_version(self) -> tuple[str, str]:
        """Sends get extended version and waits for response, returns firmware and science mode version"""      
        p = PacketGeneralGetExtendedVersion()
        ack = await Protocol.send_packet(p, 0, self._connection, self._factory)
        if ack:
            gev_ack: PacketGeneralGetExtendedVersionAck = ack
            if not gev_ack.successful:
                raise ValueError("Error get extended version")
            self._firmware_version = gev_ack.firmware_version
            self._science_mode_version = gev_ack.science_mode_version
            return self._firmware_version, self._science_mode_version
