import asyncio
"""
This script demonstrates live data acquisition from a Dyscom device using the ScienceMode4Python library.
It connects to the device via a serial port, initializes the device for measurement, and records live data
from multiple channels. The data is plotted in real-time using fastplotlib and saved to a CSV file.
Main Features:
- Auto-detects or accepts a serial port from the command line.
- Initializes the Dyscom device and prints device information.
- Waits for user input to start and stop recording.
- Acquires live data from 5 channels, plots the first 4 channels in real-time, and saves all 5 channels to CSV.
- Allows the user to specify the output CSV filename after recording.
- Handles device power management and clean shutdown.
Dependencies:
- science_mode_4 (Hasomed Science Mode 4 Python library)
- fastplotlib
- Custom utility modules: example_utils, csv_utils, fastplotlib_utils
Usage:
Run the script, follow the prompts to start and stop recording, and specify the filename for saving the data.
"""
import threading
import shutil
import os

from science_mode_4 import DeviceI24, Commands, SerialPortConnection
from science_mode_4.dyscom.ads129x.ads129x_config_register_1 import Ads129xOutputDataRate, Ads129xPowerMode
from science_mode_4.dyscom.dyscom_get_operation_mode import PacketDyscomGetAckOperationMode
from science_mode_4.dyscom.dyscom_send_live_data import PacketDyscomSendLiveData
from science_mode_4.dyscom.dyscom_types import DyscomGetType, DyscomInitParams, DyscomPowerModulePowerType, DyscomPowerModuleType, DyscomSignalType
from science_mode_4.protocol.types import ResultAndError
from science_mode_4.utils.logger import logger

from examples.utils.example_utils import ExampleUtils, KeyboardInputThread
from examples.utils.csv_utils import CsvHelper
from examples.utils.fastplotlib_utils import FastPlotLibHelper

def get_device_info(device):
    general = device.get_layer_general()
    print(f"Device id: {general.device_id}")
    print(f"Firmware version: {general.firmware_version}")
    print(f"Science mode version: {general.science_mode_version}")

def prompt_filename(default="values.csv"):
    name = input(f"Enter filename to save (default: {default}): ").strip()
    name = name + ".csv" if not name.endswith(".csv") else name
    return name if name else default

def main():
    logger().disabled = True

    # Get comport from command line or auto-detect
    com_port = ExampleUtils.get_comport_from_commandline_argument()
    connection = SerialPortConnection(com_port)
    connection.open()

    # Create device and print info
    device = DeviceI24(connection)
    asyncio.run(device.initialize())
    get_device_info(device)

    # Wait for user to start recording
    input("Press Enter to start recording...")

    # Setup plotting
    plot_helper = FastPlotLibHelper({
        0: ["Channel 1", "b"],
        1: ["Channel 2", "r"],
        2: ["Channel 3", "y"],
        3: ["Channel 4", "g"]
    }, 1000)

    # Setup CSV recording
    temp_csv = "temp_values.csv"
    csv_helper = CsvHelper(temp_csv, ["package_nr", "Channel 1", "Channel 2", "Channel 3", "Channel 4", "Channel 5", "time_delta"])
    csv_helper.start()

    # Device communication and data acquisition
    stop_event = threading.Event()

    def keyboard_listener():
        input("Press Enter to stop recording...")
        stop_event.set()

    def data_acquisition():
        async def run():
            dyscom = device.get_layer_dyscom()
            await dyscom.power_module(DyscomPowerModuleType.MEASUREMENT, DyscomPowerModulePowerType.SWITCH_ON)
            init_params = DyscomInitParams()
            init_params.signal_type = [
                DyscomSignalType.BI, DyscomSignalType.EMG_1,
                DyscomSignalType.EMG_2, DyscomSignalType.BREATHING
            ]
            init_params.register_map_ads129x.config_register_1.output_data_rate = Ads129xOutputDataRate.HR_MODE_4_KSPS__LP_MODE_2_KSPS
            init_params.register_map_ads129x.config_register_1.power_mode = Ads129xPowerMode.HIGH_RESOLUTION
            await dyscom.init(init_params)
            await dyscom.start()

            try:
                while not stop_event.is_set():
                    ack = dyscom.packet_buffer.get_packet_from_buffer()
                    if ack and ack.command == Commands.DL_SEND_LIVE_DATA:
                        sld: PacketDyscomSendLiveData = ack
                        # Plot 4 channels
                        for ch in range(4):
                            plot_helper.append_value(ch, sld.samples[ch].value)
                        plot_helper.update()
                        # Save to CSV
                        csv_helper.append_values(
                            ack.number,
                            [sld.samples[0].value, sld.samples[1].value, sld.samples[2].value, sld.samples[3].value, sld.samples[4].value],
                            sld.time_offset
                        )
                    else:
                        await asyncio.sleep(0.001)
            finally:
                await dyscom.stop()
                await dyscom.power_module(DyscomPowerModuleType.MEASUREMENT, DyscomPowerModulePowerType.SWITCH_OFF)

        asyncio.run(run())

    # Start keyboard listener and data acquisition in threads
    t1 = threading.Thread(target=keyboard_listener, daemon=True)
    t2 = threading.Thread(target=data_acquisition, daemon=True)
    t1.start()
    t2.start()

    # fastplotlib main loop (blocks until window closed)
    import fastplotlib as fpl
    fpl.loop.run()
    stop_event.set()

    t1.join()
    t2.join()

    # Stop CSV writing
    csv_helper.stop()
    connection.close()

    # Prompt for filename and save
    final_csv = prompt_filename("values.csv")
    shutil.move(temp_csv, final_csv)
    print(f"Data saved to {final_csv}")

if __name__ == "__main__":
    main()