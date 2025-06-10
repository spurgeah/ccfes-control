"""Test program how to use library without installing the library,
DO NOT USE THIS FILE, USE EXAMPLES INSTEAD"""

import struct
import sys
import asyncio

from science_mode_4.device_i24 import DeviceI24
from science_mode_4.dyscom.dyscom_get_operation_mode import PacketDyscomGetAckOperationMode
from science_mode_4.dyscom.dyscom_send_file import PacketDyscomSendFile
from science_mode_4.dyscom.dyscom_types import DyscomFilterType, DyscomGetType, DyscomInitFlag, DyscomInitParams, DyscomPowerModulePowerType, DyscomPowerModuleType, DyscomSignalType
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

    # get dyscom layer to call low level commands
    dyscom = device.get_layer_dyscom()

    # call enable measurement power module and memory card for measurement
    await dyscom.power_module(DyscomPowerModuleType.MEASUREMENT, DyscomPowerModulePowerType.SWITCH_ON)
    await dyscom.power_module(DyscomPowerModuleType.MEMORY_CARD, DyscomPowerModulePowerType.SWITCH_ON)
    # call init with lowest sample rate (because of performance issues with plotting values)
    init_params = DyscomInitParams()
    init_params.signal_type = [DyscomSignalType.BI, DyscomSignalType.EMG_1]
    init_params.filter = DyscomFilterType.PREDEFINED_FILTER_1
    # we want no live data and write all data to memory card
    init_params.flags = [DyscomInitFlag.ENABLE_SD_STORAGE_MODE]
    init_result = await dyscom.init(init_params)

    # start dyscom measurement
    await dyscom.start()

    # wait 10s to have some measurement data
    await asyncio.sleep(10)

    # stop measurement
    await dyscom.stop()
    # turn power module off
    await dyscom.power_module(DyscomPowerModuleType.MEASUREMENT, DyscomPowerModulePowerType.SWITCH_OFF)

    # get all meas data
    measurement = await dyscom.get_meas_file_content(init_result.measurement_file_id)
    print(f"Sample rate: {measurement[0].name}")
    for key, value in measurement[1].items():
        print(f"Signal type: {key.name}, sample count: {len(value)}")

    # turn memory card off
    await dyscom.power_module(DyscomPowerModuleType.MEMORY_CARD, DyscomPowerModulePowerType.SWITCH_OFF)
    # close serial port connection
    connection.close()

    return 0


if __name__ == "__main__":
    res = asyncio.run(main())
    sys.exit(res)


# init
# 00 00 00 00 00 00 00 00 83 00 FC 00 00 00 00 00 00 00 00 00 
# 00 EA EA 02 00 00 12 00 0A 0E 06 13 02 00 A0 00 7D 12 00 0A 
# 0E 06 13 02 00 A0 00 7D 00 00 00 00 00 00 00 00 00 00 00 00 
# 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 
# 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 
# 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 
# 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 
# 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 
# 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 
# 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 
# 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 
# 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 
# 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 
# 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 
# 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 
# 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 
# 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 
# 00 00 00 00 02 00 00 00 00 02 03 00 00 00 00 00 00 00 00 00 
# 02


# 01 03 00 04 00 00 00 00 00 00 02 03 04 00 00 00 00 00 00 00 
# 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 
# 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 
# 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 
# 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 
# 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 
# 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 
# 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 
# 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 
# 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 
# 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 
# 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 
# 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 
# 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 
# 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 
# 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 
# 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 
# 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 
# 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 
# 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 
# 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 
# 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 
# 00 00 00 00 00 00 00 00 83 00 fc 00 00 00 00 00 00 00 00 00 
# 02 ea 00 00 00 00 00 00 00 ea 00 00 00 00 00 00 00 00 00 00 
# 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 
# 00 00 00 00 00 00 00 00 00 00 00 00 

# 00 00 00 00 50 72 08 41 c0 39 ff bd 
# fa 00 00 00 75 a0 09 41 e0 4e f3 bd 
# fa 00 00 00 c9 b7 0c 41 e0 45 e8 bd 
# fb 00 00 00 56 c7 0e 41 a0 06 de bd 
# fa 00 00 00 32 45 11 41 e0 78 d4 bd 
# fa 00 00 00 fa 37 13 41 15 90 cb bd 
# fa 00 00 00 24 4e 14 41 a0 33 c3 bd 
# fb 00 00 00 87 1d 17 41 60 5a bb bd 
# f9 00 00 00 d1 8e 18 41 d5 f9 b3 bd 
# fa 00 00 00 4a 28 19 41 60 04 ad bd 
# fa 00 00 00 2a a3 1a 41 eb 74 a6 bd 
# fb 00 00 00 cd 52 1c 41 c0 40 a0 bd 
# f9 00 00 00 dc f5 1c 41 a0 60 9a bd 
# fa 00 00 00 0c f4 1d 41 75 d1 94 bd 
# fa 00 00 00 5b 4d 1f 41 00 8d 8f bd 
# fa 00 00 00 e8 71 20 41 ab 8b 8a bd 
# fa 00 00 00 4c 6b 21 41 f5 cc 85 bd 
# fa 00 00 00 90 09 22 41 2b 4a 81 bd 
# fa 00 00 00 2c e6 22 41 eb fa 79 bd 