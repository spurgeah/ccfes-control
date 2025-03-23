"""Provices low level layer"""

from ..protocol.channel_point import ChannelPoint
from ..protocol.types import Channel, Connector
from ..utils.packet_buffer import PacketBuffer
from ..protocol.packet_number_generator import PacketNumberGenerator
from ..protocol.packet_factory import PacketFactory
from ..utils.connection import Connection
from ..layer import Layer
from ..protocol.protocol import Protocol
from .dyscom_types import DyscomGetOperationModeType, DyscomPowerModuleType, DyscomPowerModulePowerType
from .dyscom_init import PacketDyscomInit, PacketDyscomInitAck, DyscomInitParams
from .dyscom_get_file_system_status import PacketDyscomGetFileSystemStatus, PacketDyscomGetAckFileSystemStatus, DyscomGetFileSystemStatusResult
from .dyscom_get_file_by_name import PacketDyscomGetFileByName, PacketDyscomGetAckFileByName, DyscomGetFileByNameResult
from .dyscom_get_firmware_version import PacketDyscomGetFirmwareVersion, PacketDyscomGetAckFirmwareVersion
from .dyscom_get_operation_mode import PacketDyscomGetOperationMode, PacketDyscomGetAckOperationMode
from .dyscom_start import PacketDyscomStart, PacketDyscomStartAck
from .dyscom_stop import PacketDyscomStop, PacketDyscomStopAck
from .dyscom_power_module import PacketDyscomPowerModule, PacketDyscomPowerModuleAck, DyscomPowerModuleResult

class LayerDyscom(Layer):
    """
    Class for dyscom layer
    """


    def __init__(self, conn: Connection, packet_factory: PacketFactory, packet_number_generator: PacketNumberGenerator):
        super().__init__(conn, packet_factory, packet_number_generator)
        self._packet_buffer = PacketBuffer(packet_factory)


    @property
    def packet_buffer(self) -> PacketBuffer:
        """Getter for packet buffer"""
        return self._packet_buffer


    async def init(self, params = DyscomInitParams()):
        """Send dyscom init command and waits for response"""
        p = PacketDyscomInit(params)
        ack: PacketDyscomInitAck = await Protocol.send_packet_and_wait(p, self._packet_number_generator.get_next_number(),
                                                                         self._connection, self._packet_factory)
        self.check_result_error(ack.result_error, "DyscomInit")


    async def get_file_system_status(self) -> DyscomGetFileSystemStatusResult:
        """Sends get dyscom get type file system status and waits for response, returns file system ready, used size and free size"""
        p = PacketDyscomGetFileSystemStatus()
        ack: PacketDyscomGetAckFileSystemStatus = await Protocol.send_packet_and_wait(p, self._packet_number_generator.get_next_number(),
                                                        self._connection, self._packet_factory)
        self.check_result_error(ack.result_error, "DyscomGetFileSystemStatus")
        return DyscomGetFileSystemStatusResult(ack.file_system_ready, ack.used_size, ack.free_size)


    async def get_file_by_name(self) -> DyscomGetFileByNameResult:
        """Sends get dyscom get type file by name and waits for response, returns filename, block offset, filesize and number of blocks"""
        p = PacketDyscomGetFileByName()
        ack: PacketDyscomGetAckFileByName = await Protocol.send_packet_and_wait(p, self._packet_number_generator.get_next_number(),
                                                        self._connection, self._packet_factory)
        self.check_result_error(ack.result_error, "DyscomGetFileByName")
        return DyscomGetFileByNameResult(ack.filename, ack.block_offset, ack.filesize, ack.number_of_blocks)


    async def get_firmware_version(self) -> str:
        """Sends get dyscom get type firmware version and waits for response, returns firmware version"""
        p = PacketDyscomGetFirmwareVersion()
        ack: PacketDyscomGetAckFirmwareVersion = await Protocol.send_packet_and_wait(p, self._packet_number_generator.get_next_number(),
                                                        self._connection, self._packet_factory)
        self.check_result_error(ack.result_error, "DyscomGetFirmwareVersion")
        return ack.firmware_version


    async def get_operation_mode(self) -> DyscomGetOperationModeType:
        """Sends get dyscom get type operation mode and waits for response, returns operation mode"""
        p = PacketDyscomGetOperationMode()
        ack: PacketDyscomGetAckOperationMode = await Protocol.send_packet_and_wait(p, self._packet_number_generator.get_next_number(),
                                                        self._connection, self._packet_factory)
        self.check_result_error(ack.result_error, "DyscomGetFirmwareVersion")
        return ack.operation_mode


    async def power_module(self, module: DyscomPowerModuleType, power: DyscomPowerModulePowerType) -> DyscomPowerModuleResult:
        """Sends get dyscom start and waits for response"""
        p = PacketDyscomPowerModule(module, power)
        ack: PacketDyscomPowerModuleAck = await Protocol.send_packet_and_wait(p, self._packet_number_generator.get_next_number(),
                                                        self._connection, self._packet_factory)
        self.check_result_error(ack.result_error, "DyscomStart")
        return DyscomPowerModuleResult(ack.module, ack.power)


    async def start(self):
        """Sends get dyscom start and waits for response"""
        p = PacketDyscomStart()
        ack: PacketDyscomStartAck = await Protocol.send_packet_and_wait(p, self._packet_number_generator.get_next_number(),
                                                        self._connection, self._packet_factory)
        self.check_result_error(ack.result_error, "DyscomStart")


    async def stop(self):
        """Sends get dyscom stop and waits for response"""
        p = PacketDyscomStop()
        ack: PacketDyscomStopAck = await Protocol.send_packet_and_wait(p, self._packet_number_generator.get_next_number(),
                                                        self._connection, self._packet_factory)
        self.check_result_error(ack.result_error, "DyscomStop")


    # async def stop(self):
    #     """Send low level stop command and waits for response"""
    #     p = PacketLowLevelStop()
    #     ack: PacketLowLevelStopAck = await Protocol.send_packet_and_wait(p, self._packet_number_generator.get_next_number(),
    #                                                                     self._connection, self._packet_factory)
    #     self.check_result_error(ack.result_error, "LowLevelStop")


    # def send_init(self, mode: LowLevelMode, high_voltage_source: LowLevelHighVoltageSource):
    #     """Send low level init command"""
    #     p = PacketLowLevelInit()
    #     p.mode = mode
    #     p.high_voltage_source = high_voltage_source
    #     Protocol.send_packet(p, self._packet_number_generator.get_next_number(),
    #                          self._connection,)
    #     self._packet_buffer.add_open_acknowledge(p)


    # def send_channel_config(self, execute_stimulation: bool, channel: Channel,
    #                         connector: Connector, points: list[ChannelPoint]):
    #     """Send low level channel config command"""
    #     p = PacketLowLevelChannelConfig()
    #     p.execute_stimulation = execute_stimulation
    #     p.channel = channel
    #     p.connector = connector
    #     p.points = points
    #     Protocol.send_packet(p, self._packet_number_generator.get_next_number(),
    #                          self._connection)
    #     self._packet_buffer.add_open_acknowledge(p)


    # def send_stop(self):
    #     """Send low level stop command"""
    #     p = PacketLowLevelStop()
    #     Protocol.send_packet(p, self._packet_number_generator.get_next_number(),
    #                          self._connection)
    #     self._packet_buffer.add_open_acknowledge(p)
