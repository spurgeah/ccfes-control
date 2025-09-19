"""
adds
- press enter to start recording
- convert ADC values to respective units

"""

import asyncio
import threading
import fastplotlib as fpl
from timeit import default_timer as timer
import shutil

from science_mode_4 import DeviceI24, Commands, SerialPortConnection
from science_mode_4.dyscom.ads129x.ads129x_config_register_1 import Ads129xOutputDataRate, Ads129xPowerMode
from science_mode_4.dyscom.dyscom_get_operation_mode import PacketDyscomGetAckOperationMode
from science_mode_4.dyscom.dyscom_send_live_data import PacketDyscomSendLiveData
from science_mode_4.dyscom.dyscom_types import DyscomGetType, DyscomInitParams, DyscomPowerModulePowerType, DyscomPowerModuleType, DyscomSignalType
from science_mode_4.protocol.types import ResultAndError
from science_mode_4.utils.logger import logger

from examples.utils.fastplotlib_utils import FastPlotLibHelper
from examples.utils.example_utils import ExampleUtils
from examples.utils.csv_utils import CsvHelper


def main():
    """Main function"""

    # Setup plot helper
    plot_helper = FastPlotLibHelper(
        {0: ["Channel 1", "b"], 1: ["Channel 2", "r"], 2: ["Channel 3", "y"], 3: ["Channel 4", "g"]},
        2000
    )
    is_window_open = True

    # Setup CSV writer with temporary name (will rename later)
    csv_helper = CsvHelper("temp_recording.csv", ["package_nr", "Channel 1", "Channel 2", "Channel 3", "Channel 4", "Channel 5", "time_delta"])
    csv_helper.start()

    async def device_communication() -> int:
        """Communication with science mode device"""
        nonlocal is_window_open

        logger().disabled = True  # Disable logger for performance

        com_port = ExampleUtils.get_comport_from_commandline_argument()
        connection = SerialPortConnection(com_port)
        connection.open()

        device = DeviceI24(connection)
        await device.initialize()

        dyscom = device.get_layer_dyscom()

        await dyscom.power_module(DyscomPowerModuleType.MEASUREMENT, DyscomPowerModulePowerType.SWITCH_ON)

        # Configure signal types and sample rate
        init_params = DyscomInitParams()
        init_params.signal_type = [DyscomSignalType.BI, DyscomSignalType.EMG_1, DyscomSignalType.EMG_2, DyscomSignalType.BREATHING]
        init_params.register_map_ads129x.config_register_1.output_data_rate = Ads129xOutputDataRate.HR_MODE_500_SPS__LP_MODE_250_SPS
        init_params.register_map_ads129x.config_register_1.power_mode = Ads129xPowerMode.LOW_POWER

       
        VREF = 4.0  # volts, automatically set at 4.0 unless add init_param
        GAIN = 6 #automatically set at 6 unless add init_param
        CURRENT = 30e-6  # 30 uA injected - page 15 of ads129x chip manual

        await dyscom.init(init_params)

#added press enter to start recording ---------------------
        input("Press Enter to start recording...")  # waits for user to start data collection

        await dyscom.start()

        start_time = timer()
        total_count = 0

        for x in range(1000):
            if not is_window_open:
                break

            if x % 500 == 0:
                dyscom.send_get_operation_mode()

            live_data_counter = 0
            while True:
                ack = dyscom.packet_buffer.get_packet_from_buffer(live_data_counter == 0)
                if ack:
                    if ack.command == Commands.DL_GET_ACK and ack.kind == DyscomGetType.OPERATION_MODE:
                        om_ack: PacketDyscomGetAckOperationMode = ack
                        print(f"Operation mode {om_ack.operation_mode.name}")
                        if om_ack.result_error != ResultAndError.NO_ERROR:
                            break
                    elif ack.command == Commands.DL_SEND_LIVE_DATA:
                        live_data_counter += 1
                        total_count += 1

                        sld: PacketDyscomSendLiveData = ack
                        if sld.status_error:
                            print(f"SendLiveData status error {sld.samples}")
                            break

                        for i in range(4):
 #convert to respective channel units
                            if i ==0:
                                raw = sld.samples[0].value
                                #converted = (raw / (2**23)) * (VREF / GAIN) / CURRENT # convert to current in Amperes
                                converted = raw
                            else:
                                raw = sld.samples[i].value
                                #converted = (raw / (2**23)) * (VREF / GAIN) * 1e6  # convert to microvolts
                                converted = raw

                            plot_helper.append_value(i, converted)
                        plot_helper.update()

                        csv_helper.append_values(ack.number, [
                            sld.samples[0].value, sld.samples[1].value,
                            sld.samples[2].value, sld.samples[3].value,
                            sld.samples[4].value
                        ], sld.time_offset)
                else:
                    break

            await asyncio.sleep(0.001)

        end_time = timer()
        print(f"Samples: {total_count}, duration: {end_time - start_time}, sample rate: {total_count / (end_time - start_time)}")

        await dyscom.stop()
        await dyscom.power_module(DyscomPowerModuleType.MEASUREMENT, DyscomPowerModulePowerType.SWITCH_OFF)
        connection.close()
        csv_helper.stop()

        # Rename file
        new_filename = input("Enter a filename to save the CSV as (e.g., 'my_data.csv'): ").strip()
        import os
        folder = os.path.join(".", "csv_files")  # Folder: ./csv_files
        os.makedirs(folder, exist_ok=True) 

        if new_filename:
            if not new_filename.endswith(".csv"):
                new_filename += ".csv"
            os.rename("temp_recording.csv", new_filename)
            final_path = os.path.join(folder, new_filename) # Use current directory if nothing entered
            shutil.move(new_filename, final_path)
            print(f"Saved data to '{new_filename}'")
        else:
            print("No filename provided. Data saved as 'temp_recording.csv'.")

        return 0

    def data_generator():
        return asyncio.run(device_communication())

    data_thread = threading.Thread(target=data_generator, daemon=True)
    data_thread.start()

    fpl.loop.run()
    is_window_open = False


if __name__ == "__main__":
    main()
