"""Test program how to use library without installing the library,
DO NOT USE THIS FILE, USE EXAMPLES INSTEAD"""

import sys
import asyncio

from science_mode_4.device_i24 import DeviceI24
from science_mode_4.dyscom.dyscom_get_operation_mode import PacketDyscomGetAckOperationMode
from science_mode_4.dyscom.dyscom_send_file import PacketDyscomSendFile
from science_mode_4.dyscom.dyscom_types import DyscomGetType, DyscomPowerModulePowerType, DyscomPowerModuleType
from science_mode_4.protocol.commands import Commands
from science_mode_4.utils.serial_port_connection import SerialPortConnection


async def main() -> int:
    """Main function"""

    # create serial port connection
    connection = SerialPortConnection(SerialPortConnection.list_science_mode_device_ports()[0].device)
    # open connection, now we can read and write data
    connection.open()

    # create science mode device
    device = DeviceI24(connection)
    # call initialize to get basic information (serial, versions) and stop any active stimulation/measurement
    # to have a defined state
    await device.initialize()

    # get general layer to access general commands
    general = device.get_layer_general()
    # get dyscom layer to access dyscom commands
    dyscom = device.get_layer_dyscom()

    pm = await dyscom.power_module(DyscomPowerModuleType.MEMORY_CARD,
                        DyscomPowerModulePowerType.SWITCH_ON)
    print(pm)

    #####
    # dyscom layer provides a get command for device id, it is redundant to general layer device id
    # both values should be identical
    device_id = await dyscom.get_device_id()
    print(f"Device id from general layer: {general.device_id}, from dyscom layer: {device_id}")

    #####
    # dyscom layer provides a get command for firmware version, it is redundant to general layer firmware verion
    # both values should be identical
    firmware_version = await dyscom.get_firmware_version()
    print(f"Firmware version from general layer: {general.firmware_version}, from dyscom layer: {firmware_version}")

    #####
    # get command for file system status
    file_system_status = await dyscom.get_file_system_status()
    print(file_system_status)

    om = await dyscom.get_operation_mode()
    print(om)

    ####
    calibration_filename = f"rehaingest_{device_id}.cal"
    content = await dyscom.get_file_content(calibration_filename)
    print(len(content))
    # get calibration file info
    # file_info = await dyscom.get_file_info(calibration_filename)
    # print(file_info)

    # om = await dyscom.get_operation_mode()
    # print(om)

    # # get calibration file -> does not work
    # # there should be DL_Send_File commands afterwards
    # file_by_name = await dyscom.get_file_by_name(calibration_filename)
    # print(file_by_name)

    # dyscom.send_get_operation_mode()
    # dyscom.send_start()
    # dyscom.send_get_operation_mode()
    # while True:
    #     # process all available packages
    #     ack = dyscom.packet_buffer.get_packet_from_buffer()
    #     if ack:
    #         if ack.command == Commands.DL_GET_ACK and ack.kind == DyscomGetType.OPERATION_MODE:
    #             om_ack: PacketDyscomGetAckOperationMode = ack
    #             print(f"Operation mode {om_ack.operation_mode.name}")
    #         elif ack.command == Commands.DL_SEND_FILE:
    #             sf: PacketDyscomSendFile = ack
    #             print(f"Block number: {sf.block_number}, block size: {sf.block_size}")
    #             print(sf.data)

    #             dyscom.send_send_file_ack(sf.block_number)

    #             if sf.block_number == file_by_name.number_of_blocks:
    #                 break
    #         else:
    #             print(f"Not process command: {ack.command}")

    #     await asyncio.sleep(0.01)

    # await dyscom.stop()
    # close serial port connection
    connection.close()
    return 0


if __name__ == "__main__":
    res = asyncio.run(main())
    sys.exit(res)
