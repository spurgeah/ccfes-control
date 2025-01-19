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

    deviceId: str | None
    firmwareVersion: str | None
    scienceModeVersion: str | None


    def __init__(self, conn: Connection, packet_factory: PacketFactory):
        super().__init__(conn, packet_factory)
        

    async def initialize(self):
        await self.getDeviceId()
        await self.getVersion()


    async def getDeviceId(self):
        p = PacketGeneralGetDeviceId()
        ack = await Protocol.sendPacket(p, 0, self.connection, self.factory)
        if ack:
            dgi_ack: PacketGeneralGetDeviceIdAck = ack
            self.checkResultError(dgi_ack.resultError, "GetDeviceId")
            self.deviceId = dgi_ack.deviceId


    async def reset(self):
        p = PacketGeneralReset()
        ack = await Protocol.sendPacket(p, 0, self.connection, self.factory)
        if ack:
            reset_ack: PacketGeneralResetAck = ack
            self.checkResultError(reset_ack.resultError, "Reset")
            pass


    async def getStimStatus(self) -> GetStimStatusResult:
        p = PacketGeneralGetStimStatus()
        ack = await Protocol.sendPacket(p, 0, self.connection, self.factory)
        if ack:
            gss_ack: PacketGeneralGetStimStatusAck = ack
            if not gss_ack.successful:
                raise ValueError(f"Error get stim status")
            return GetStimStatusResult(gss_ack.stimStatus, gss_ack.highVoltageOn)


    async def getVersion(self):       
        p = PacketGeneralGetExtendedVersion()
        ack = await Protocol.sendPacket(p, 0, self.connection, self.factory)
        if ack:
            gev_ack: PacketGeneralGetExtendedVersionAck = ack
            if not gev_ack.successful:
                raise ValueError(f"Error get extended version")
            self.firmwareVersion = gev_ack.firmwareVersion
            self.scienceModeVersion = gev_ack.scienceModeVersion
