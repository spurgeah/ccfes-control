"""Test program how to use library without installing the library,
DO NOT USE THIS FILE, USE EXAMPLES INSTEAD"""

from timeit import default_timer as timer

import logging
import sys
import asyncio

from science_mode_4.device_i24 import DeviceI24
from science_mode_4.device_p24 import DeviceP24
from science_mode_4.dyscom.ads129x.ads129x_config_register_1 import Ads129xOutputDataRate, Ads129xPowerMode
from science_mode_4.dyscom.dyscom_get_operation_mode import PacketDyscomGetAckOperationMode
from science_mode_4.dyscom.dyscom_send_live_data import PacketDyscomSendLiveData
from science_mode_4.dyscom.dyscom_types import DyscomFilterType, DyscomGetType, DyscomInitParams, DyscomPowerModulePowerType, DyscomPowerModuleType, DyscomSignalType
from science_mode_4.protocol.commands import Commands
from science_mode_4.protocol.types import ResultAndError
from science_mode_4.utils import logger
from science_mode_4.utils.serial_port_connection import SerialPortConnection
from science_mode_4.utils.usb_connection import UsbConnection



async def main() -> int:
    """Main function"""

    logger().disabled = True

    logger().setLevel(logging.DEBUG)
    # devices = SerialPortConnection.list_science_mode_device_ports()
    # connection = SerialPortConnection(devices[0].device)
    devices = UsbConnection.list_science_mode_devices()
    connection = UsbConnection(devices[0])
    # connection = NullConnection()
    connection.open()

    device = DeviceI24(connection)
    await device.initialize()
    # get dyscom layer to call dyscom level commands
    dyscom = device.get_layer_dyscom()

    # call enable measurement power module for measurement
    await dyscom.power_module(DyscomPowerModuleType.MEASUREMENT, DyscomPowerModulePowerType.SWITCH_ON)
    # call init with 4k sample rate and enable signal types
    init_params = DyscomInitParams()
    init_params.filter = DyscomFilterType.PREDEFINED_FILTER_2
    init_params.signal_type = [DyscomSignalType.BI, DyscomSignalType.EMG_1,\
                            DyscomSignalType.EMG_2, DyscomSignalType.BREATHING, DyscomSignalType.TEMPERATURE]
    init_params.register_map_ads129x.config_register_1.output_data_rate = Ads129xOutputDataRate.HR_MODE_4_KSPS__LP_MODE_2_KSPS
    init_params.register_map_ads129x.config_register_1.power_mode = Ads129xPowerMode.HIGH_RESOLUTION
    await dyscom.init(init_params)

    # start dyscom measurement
    await dyscom.start()

    start_time = timer()
    total_count = 0

    # loop for some time
    for x in range(1000):
        # check operation mode from time to time, this function is not waiting for response
        # so we have to handle it by ourself later
        if x % 100 == 0:
            dyscom.send_get_operation_mode()

        live_data_counter = 0
        while True:
            # process all available packages
            ack = dyscom.packet_buffer.get_packet_from_buffer(live_data_counter == 0)
            if ack:
                # because there are multiple get commands, we need to additionally check kind,
                # which is always associated DyscomGetType
                if ack.command == Commands.DL_GET_ACK and ack.kind == DyscomGetType.OPERATION_MODE:
                    om_ack: PacketDyscomGetAckOperationMode = ack
                    print(f"Operation mode {om_ack.operation_mode.name}")
                    # check if measurement is still active
                    if om_ack.result_error != ResultAndError.NO_ERROR:
                        break
                elif ack.command == Commands.DL_SEND_LIVE_DATA:
                    live_data_counter += 1
                    total_count += 1

                    sld: PacketDyscomSendLiveData = ack
                    if sld.status_error:
                        print(f"SendLiveData status error {sld.samples}")
                        break

            else:
                # print(f"Live data acknowledges per iteration {live_data_counter}")
                break

        # await asyncio.sleep(0.01)

    # print stats
    end_time = timer()
    print(f"Samples: {total_count}, duration: {end_time - start_time}, sample rate: {total_count / (end_time - start_time)}")

    # stop measurement
    await dyscom.stop()
    # turn power module off
    await dyscom.power_module(DyscomPowerModuleType.MEASUREMENT, DyscomPowerModulePowerType.SWITCH_OFF)

    connection.close()

    return 0


if __name__ == "__main__":
    res = asyncio.run(main())
    sys.exit(res)
