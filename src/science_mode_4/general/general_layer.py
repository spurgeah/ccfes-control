"""Provices general layer"""

from ..protocol.packet_number_generator import PacketNumberGenerator
from .general_reset import PacketGeneralReset, PacketGeneralResetAck
from .general_stim_status import GetStimStatusResult, PacketGeneralGetStimStatus, PacketGeneralGetStimStatusAck
from .general_device_id import PacketGeneralGetDeviceId, PacketGeneralGetDeviceIdAck
from .general_version import PacketGeneralGetExtendedVersion, PacketGeneralGetExtendedVersionAck
from ..protocol.packet_factory import PacketFactory
from ..utils.connection import Connection
from ..layer import Layer
from ..protocol.protocol import Protocol


class LayerGeneral(Layer):
    """Class for general layer"""


    def __init__(self, conn: Connection, packet_factory: PacketFactory, packet_number_generator: PacketNumberGenerator):
        super().__init__(conn, packet_factory, packet_number_generator)
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
        ack = await Protocol.send_packet_and_wait(p, self._packet_number_generator.get_next_number(),
                                                  self._connection, self._packet_factory)
        if ack:
            dgi_ack: PacketGeneralGetDeviceIdAck = ack
            self.check_result_error(dgi_ack.result_error, "GetDeviceId")
            self._device_id = dgi_ack.device_id
            return self._device_id


    async def reset(self):
        """Sends reset command and waits for response"""
        p = PacketGeneralReset()
        ack = await Protocol.send_packet_and_wait(p, self._packet_number_generator.get_next_number(),
                                                  self._connection, self._packet_factory)
        if ack:
            reset_ack: PacketGeneralResetAck = ack
            self.check_result_error(reset_ack.resultError, "Reset")


    async def get_stim_status(self) -> GetStimStatusResult:
        """Sends get stim status and waits for response"""
        p = PacketGeneralGetStimStatus()
        ack = await Protocol.send_packet_and_wait(p, self._packet_number_generator.get_next_number(),
                                                  self._connection, self._packet_factory)
        if ack:
            gss_ack: PacketGeneralGetStimStatusAck = ack
            if not gss_ack.successful:
                raise ValueError("Error get stim status")
            return GetStimStatusResult(gss_ack.stim_status, gss_ack.high_voltage_on)


    async def get_version(self) -> tuple[str, str]:
        """Sends get extended version and waits for response, returns firmware and science mode version"""      
        p = PacketGeneralGetExtendedVersion()
        ack = await Protocol.send_packet_and_wait(p, self._packet_number_generator.get_next_number(),
                                                  self._connection, self._packet_factory)
        if ack:
            gev_ack: PacketGeneralGetExtendedVersionAck = ack
            if not gev_ack.successful:
                raise ValueError("Error get extended version")
            self._firmware_version = gev_ack.firmware_version
            self._science_mode_version = gev_ack.science_mode_version
            return self._firmware_version, self._science_mode_version
