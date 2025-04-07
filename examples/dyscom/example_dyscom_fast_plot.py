"""Example how to use dyscom with fastplotlib for fast plotting of values"""

import asyncio
import threading

import fastplotlib as fpl

from science_mode_4 import DeviceI24
from science_mode_4 import Commands
from science_mode_4 import SerialPortConnection
from science_mode_4.dyscom.ads129x.ads129x_config_register_1 import Ads129xOutputDataRate, Ads129xPowerMode
from science_mode_4.dyscom.dyscom_get_operation_mode import PacketDyscomGetAckOperationMode
from science_mode_4.dyscom.dyscom_send_live_data import PacketDyscomSendLiveData
from science_mode_4.dyscom.dyscom_types import DyscomInitParams, DyscomPowerModulePowerType, DyscomPowerModuleType, DyscomSignalType
from examples.utils.example_utils import ExampleUtils
from examples.utils.example_fast_plot_utils import FastPlotHelper

ph = FastPlotHelper({0: ["BI", "b"], 1: ["EMG1", "r"], 2: ["EMG2", "y"],\
                     3: ["Breathing", "g"], 4: ["Temperature", "w"]}, 250)

async def main() -> int:
    """Communication with science mode device"""

    # get comport from command line argument
    com_port = ExampleUtils.get_comport_from_commandline_argument()
    # create serial port connection
    connection = SerialPortConnection(com_port)
    # open connection, now we can read and write data
    connection.open()

    # create science mode device
    device = DeviceI24(connection)
    # call initialize to get basic information (serial, versions) and stop any active stimulation/measurement
    # to have a defined state
    await device.initialize()

    # get dyscom layer to call low level commands
    dyscom = device.get_layer_dyscom()

    # call enable measurement power module for measurement
    await dyscom.power_module(DyscomPowerModuleType.MEASUREMENT, DyscomPowerModulePowerType.SWITCH_ON)
    # call init with lowest sample rate (because of performance issues with plotting values)
    init_params = DyscomInitParams()
    init_params.signal_type = [DyscomSignalType.BI, DyscomSignalType.EMG_1,\
                               DyscomSignalType.EMG_2, DyscomSignalType.BREATHING, DyscomSignalType.TEMPERATURE]
    init_params.register_map_ads129x.config_register_1.output_data_rate = Ads129xOutputDataRate.HR_MODE_500_SPS__LP_MODE_250_SPS
    init_params.register_map_ads129x.config_register_1.power_mode = Ads129xPowerMode.LOW_POWER
    await dyscom.init(init_params)

    # start dyscom measurement
    await dyscom.start()

    for x in range(1000):
        # check operation mode from time to time
        if x % 100 == 0:
            dyscom.send_get_operation_mode()

        while True:
            ack = dyscom.packet_buffer.get_packet_from_buffer()
            if ack:
                if ack.command == Commands.DlGetAck:
                    om_ack: PacketDyscomGetAckOperationMode = ack
                    print(f"Operation mode {om_ack.operation_mode}")
                elif ack.command == Commands.DlSendLiveData:
                    sld: PacketDyscomSendLiveData = ack
                    if sld.status_error:
                        print(f"SendLiveData status error {sld.samples}")
                        break
                    if sld.number % 10 == 0:
                        # print(f"Append {sld.value} {sld.signal_type}")
                        ph.append_value(0, sld.samples[0].value)
                        ph.append_value(1, sld.samples[1].value)
                        ph.append_value(2, sld.samples[2].value)
                        ph.append_value(3, sld.samples[3].value)
                        ph.append_value(4, sld.samples[4].value)
                        # for s in sld.samples:
                        #     ph.append_value(int(s.signal_type), s.value)

                        ph.update()
            else:
                break

        await asyncio.sleep(0.01)

    # wait until all acknowledges are received
    await asyncio.sleep(0.5)

    # stop measurement
    await dyscom.stop()
    # turn power module off
    await dyscom.power_module(DyscomPowerModuleType.MEASUREMENT, DyscomPowerModulePowerType.SWITCH_OFF)

    # close serial port connection
    connection.close()

    return 0


def data_generator():
    """Background function"""
    asyncio.run(main())


# Create and start the data generator thread (aka background threa)
data_thread = threading.Thread(target=data_generator, daemon=True)
data_thread.start()

if __name__ == "__main__":
    # fastplotlib requires a main loop to draw everything
    fpl.loop.run()
