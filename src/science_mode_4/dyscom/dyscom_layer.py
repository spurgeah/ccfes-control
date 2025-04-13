"""Provices low level layer"""

from science_mode_4.layer import Layer
from .dyscom_types import DyscomGetOperationModeType, DyscomPowerModuleType, DyscomPowerModulePowerType, DyscomSysType
from .dyscom_init import DyscomInitResult, PacketDyscomInit, PacketDyscomInitAck, DyscomInitParams
from .dyscom_get_file_system_status import PacketDyscomGetFileSystemStatus, PacketDyscomGetAckFileSystemStatus,\
    DyscomGetFileSystemStatusResult
from .dyscom_get_file_by_name import PacketDyscomGetFileByName, PacketDyscomGetAckFileByName, DyscomGetFileByNameResult
from .dyscom_get_firmware_version import PacketDyscomGetFirmwareVersion, PacketDyscomGetAckFirmwareVersion
from .dyscom_get_operation_mode import PacketDyscomGetOperationMode, PacketDyscomGetAckOperationMode
from .dyscom_start import PacketDyscomStart, PacketDyscomStartAck
from .dyscom_stop import PacketDyscomStop, PacketDyscomStopAck
from .dyscom_power_module import PacketDyscomPowerModule, PacketDyscomPowerModuleAck, DyscomPowerModuleResult
from .dyscom_get_list_of_measurement_meta_info import PacketDyscomGetAckListOfMeasurementMetaInfo, PacketDyscomGetListOfMeasurementMetaInfo
from .dyscom_get_device_id import PacketDyscomGetAckDeviceId, PacketDyscomGetDeviceId
from .dyscom_get_file_info import DyscomGetFileInfoResult, PacketDyscomGetAckFileInfo, PacketDyscomGetFileInfo
from .dyscom_get_battery_status import DyscomGetBatteryResult, PacketDyscomGetAckBatteryStatus, PacketDyscomGetBatteryStatus
from .dyscom_sys import DyscomSysResult, PacketDyscomSys, PacketDyscomSysAck
from .dyscom_send_file import PacketDyscomSendFileAck


class LayerDyscom(Layer):
    """
    Class for dyscom layer
    """


    async def init(self, params = DyscomInitParams()) -> DyscomInitResult:
        """Send dyscom init command and waits for response"""
        p = PacketDyscomInit(params)
        ack: PacketDyscomInitAck = await self._send_packet_and_wait(p)
        self._check_result_error(ack.result_error, "DyscomInit")
        return DyscomInitResult(ack.register_map_ads129x, ack.init_state, ack.frequency_out)


    async def get_file_system_status(self) -> DyscomGetFileSystemStatusResult:
        """Sends get dyscom get type file system status and waits for response, returns file system ready, used size and free size"""
        p = PacketDyscomGetFileSystemStatus()
        ack: PacketDyscomGetAckFileSystemStatus = await self._send_packet_and_wait(p)
        self._check_result_error(ack.result_error, "DyscomGetFileSystemStatus")
        return DyscomGetFileSystemStatusResult(ack.file_system_ready, ack.used_size, ack.free_size)


    async def get_list_of_measurement_meta_info(self) -> int:
        """Sends get dyscom get type list of measurement meta info and waits for response, returns number of measurements"""
        p = PacketDyscomGetListOfMeasurementMetaInfo()
        ack: PacketDyscomGetAckListOfMeasurementMetaInfo = await self._send_packet_and_wait(p)
        self._check_result_error(ack.result_error, "DyscomGetListOfMeasurementMetaInfo")
        return ack.number_of_measurements


    async def get_file_by_name(self) -> DyscomGetFileByNameResult:
        """Sends get dyscom get type file by name and waits for response, returns filename, block offset,
        filesize, number of blocks and mode"""
        p = PacketDyscomGetFileByName()
        ack: PacketDyscomGetAckFileByName = await self._send_packet_and_wait(p)
        self._check_result_error(ack.result_error, "DyscomGetFileByName")
        return DyscomGetFileByNameResult(ack.filename, ack.block_offset, ack.filesize, ack.number_of_blocks, ack.mode)


    async def get_device_id(self) -> str:
        """Sends get dyscom get type device id and waits for response, returns device id"""
        p = PacketDyscomGetDeviceId()
        ack: PacketDyscomGetAckDeviceId = await self._send_packet_and_wait(p)
        self._check_result_error(ack.result_error, "DyscomGetDeviceId")
        return ack.device_id


    async def get_firmware_version(self) -> str:
        """Sends get dyscom get type firmware version and waits for response, returns firmware version"""
        p = PacketDyscomGetFirmwareVersion()
        ack: PacketDyscomGetAckFirmwareVersion = await self._send_packet_and_wait(p)
        self._check_result_error(ack.result_error, "DyscomGetFirmwareVersion")
        return ack.firmware_version


    async def get_file_info(self) -> DyscomGetFileInfoResult:
        """Sends get dyscom get type file by name and waits for response, returns filename, block offset, filesize and number of blocks"""
        p = PacketDyscomGetFileInfo()
        ack: PacketDyscomGetAckFileInfo = await self._send_packet_and_wait(p)
        self._check_result_error(ack.result_error, "DyscomGetFileInfo")
        return DyscomGetFileInfoResult(ack.filename, ack.filesize, ack.checksum)


    async def get_battery(self) -> DyscomGetBatteryResult:
        """Sends get dyscom get type batter and waits for response, returns voltage, current, percentage, temperature and energy state"""
        p = PacketDyscomGetBatteryStatus()
        ack: PacketDyscomGetAckBatteryStatus = await self._send_packet_and_wait(p)
        self._check_result_error(ack.result_error, "DyscomGetBatteryStatus")
        return DyscomGetBatteryResult(ack.voltage, ack.current, ack.percentage, ack.temperature, ack.energy_state)


    async def get_operation_mode(self) -> DyscomGetOperationModeType:
        """Sends get dyscom get type operation mode and waits for response, returns operation mode"""
        p = PacketDyscomGetOperationMode()
        ack: PacketDyscomGetAckOperationMode = await self._send_packet_and_wait(p)
        self._check_result_error(ack.result_error, "DyscomGetFirmwareVersion")
        return ack.operation_mode


    def send_get_operation_mode(self):
        """Sends get dyscom get type operation mode and returns immediately without waiting for response"""
        p = PacketDyscomGetOperationMode()
        self._send_packet(p)


    async def power_module(self, module: DyscomPowerModuleType, power: DyscomPowerModulePowerType) -> DyscomPowerModuleResult:
        """Sends get dyscom power module and waits for response, returns module and power"""
        p = PacketDyscomPowerModule(module, power)
        ack: PacketDyscomPowerModuleAck = await self._send_packet_and_wait(p)
        self._check_result_error(ack.result_error, "DyscomStart")
        return DyscomPowerModuleResult(ack.module, ack.power)


    async def sys(self, sys_type: DyscomSysType, filename: str = "") -> DyscomSysResult:
        """Sends get dyscom sys and waits for response, returns type, state and filename"""
        p = PacketDyscomSys(sys_type, filename)
        ack: PacketDyscomSysAck = await self._send_packet_and_wait(p)
        self._check_result_error(ack.result_error, "DyscomSys")
        return DyscomSysResult(ack.sys_type, ack.state, ack.filename)


    def send_send_file_ack(self, block_number: int):
        """Sends get dyscom send file ack and returns immediately without waiting for response"""
        p = PacketDyscomSendFileAck(block_number)
        self._send_packet(p)


    async def start(self):
        """Sends get dyscom start and waits for response"""
        p = PacketDyscomStart()
        ack: PacketDyscomStartAck = await self._send_packet_and_wait(p)
        self._check_result_error(ack.result_error, "DyscomStart")


    async def stop(self):
        """Sends get dyscom stop and waits for response"""
        p = PacketDyscomStop()
        ack: PacketDyscomStopAck = await self._send_packet_and_wait(p)
        self._check_result_error(ack.result_error, "DyscomStop")
