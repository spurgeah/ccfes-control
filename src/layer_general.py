import asyncio
from typing import NamedTuple

from src.commands import StimStatus
from src.general.reset import PacketReset
from src.general.stim_status import GetStimStatusResult, PacketGetStimStatus
from .general.device_id import PacketGetDeviceId
from .general.version import PacketGetExtendedVersion
from .packet_factory import PacketFactory
from .utils.connection import Connection
from .layer import Layer
from .protocol import Protocol


class LayerGeneral(Layer):

    deviceId: str | None
    firmwareVersion: str | None
    scienceModeVersion: str | None


    def __init__(self, conn: Connection, packet_factory: PacketFactory):
        super().__init__(conn, packet_factory)
        

    async def initialize(self):
        await self.getDeviceId()
        await self.getVersion()


    async def getDeviceId(self):
        p = PacketGetDeviceId()
        ack = await Protocol.sendPacket(p, 0, self.connection, self.factory)
        if ack:
            self.deviceId = ack.deviceId


    async def reset(self):
        p = PacketReset()
        ack = await Protocol.sendPacket(p, 0, self.connection, self.factory)
        if ack:
            # ToDo: check error
            pass


    async def getStimStatus(self) -> GetStimStatusResult:
        p = PacketGetStimStatus()
        ack = await Protocol.sendPacket(p, 0, self.connection, self.factory)
        if ack:
            return GetStimStatusResult(ack.stimStatus, ack.highVoltageOn)


    async def getVersion(self):       
        p = PacketGetExtendedVersion()
        ack = await Protocol.sendPacket(p, 0, self.connection, self.factory)
        if ack:
            self.firmwareVersion = ack.firmwareVersion
            self.scienceModeVersion = ack.scienceModeVersion
