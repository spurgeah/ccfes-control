import asyncio
from time import time
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
# Import required Python libraries and modules for functionality
import asyncio  # Allows handling tasks that run asynchronously, like live data collection
import threading  # Used for running multiple operations at once (e.g., listening for keyboard input while collecting data)
import shutil  # Used to move files around (e.g., renaming the CSV after saving)
import os  # Interacts with the operating system (not directly used in this script)
import time  # Used to track how long the program has been running 
# Import the tools provided by the ScienceMode4Python library
# These manage communication with the Dyscom device and interpret its data
from science_mode_4 import DeviceI24, Commands, SerialPortConnection
from science_mode_4.dyscom.ads129x.ads129x_config_register_1 import Ads129xOutputDataRate, Ads129xPowerMode
from science_mode_4.dyscom.dyscom_get_operation_mode import PacketDyscomGetAckOperationMode
from science_mode_4.dyscom.dyscom_send_live_data import PacketDyscomSendLiveData
from science_mode_4.dyscom.dyscom_types import DyscomGetType, DyscomInitParams, DyscomPowerModulePowerType, DyscomPowerModuleType, DyscomSignalType
from science_mode_4.protocol.types import ResultAndError
from science_mode_4.utils.logger import logger
from scipy.signal import butter, lfilter, lfilter_zi  # Used for filtering the live data to remove noise 

# Import utility modules for keyboard input, CSV saving, and plotting
from examples.utils.example_utils import ExampleUtils, KeyboardInputThread
from examples.utils.csv_utils import CsvHelper
from examples.utils.fastplotlib_utils import FastPlotLibHelper

# Prints basic information about the connected Dyscom device
def get_device_info(device):
    general = device.get_layer_general()
    print(f"Device id: {general.device_id}")
    print(f"Firmware version: {general.firmware_version}")
    print(f"Science mode version: {general.science_mode_version}")

# Asks the user what filename to save the data under
def prompt_filename(default="values.csv"):
    name = input(f"Enter filename to save (default: {default}): ").strip()
    name = name + ".csv" if not name.endswith(".csv") else name # Ensure it ends with .csv
    return name if name else default  # Use default if user enters nothing

# # Design a high-pass filter (>5Hz)
# def butter_highpass(cutoff, fs, order=4):
#     nyq = 0.5 * fs
#     normal_cutoff = cutoff / nyq
#     b, a = butter(order, normal_cutoff, btype='high', analog=False)
#     return b, a

# # Design a notch filter (band-stop) for 58-62Hz
# def butter_bandstop(lowcut, highcut, fs, order=2):
#     nyq = 0.5 * fs
#     low = lowcut / nyq
#     high = highcut / nyq
#     b, a = butter(order, [low, high], btype='bandstop')
#     return b, a

# def apply_filter(data, b, a, zi):
#     y, zo = lfilter(b, a, [data], zi=zi)
#     return y[0], zo

# The main function where everything is set up and run
def main():
    logger().disabled = True  # Turns off internal logging output to keep the screen clean

    # Automatically finds or accepts a COM port to talk to the Dyscom device
    com_port = ExampleUtils.get_comport_from_commandline_argument()
    #com_port = 'COM4'
    connection = SerialPortConnection(com_port)
    print(f"Connecting to {com_port}...")
    connection.open()  # Opens the serial connection

    # Connects to the device and shows its info
    device = DeviceI24(connection)
    asyncio.run(device.initialize())  # Sets up the device for communication
    get_device_info(device)  # Prints out ID and firmware info

    input("Press Enter to start recording...")  # Waits for user to start data collection

    # Set up real-time plotting for the first 4 data channels
    plot_helper = FastPlotLibHelper({
        0: ["Channel 1", "r"],  # 'r' = red line
        1: ["Channel 2", "g"],  # 'g' = green line
        2: ["Channel 3", "y"],  # 'y' = yellow line
        3: ["Channel 4", "b"]   # 'b' = blue line
    }, 1000)  # 1000 samples shown in the plot at a time

    # Set up a temporary file to save incoming data from all 5 channels
    temp_csv = "temp_values.csv"
    csv_helper = CsvHelper(temp_csv, ["package_nr", "Channel 1", "Channel 2", "Channel 3", "Channel 4", "Channel 5", "time_delta"])
    csv_helper.start()

    start_time = time.time() # Record start time before main loop

    # Used to stop recording later
    stop_event = threading.Event()

    # This function waits for the user to press Enter to stop recording
    def keyboard_listener():
        input("Press Enter to stop recording...")
        stop_event.set()  # Signals to stop the recording


    # This function handles receiving and processing live data from the device
    def data_acquisition():
        async def run():
            # Get access to the part of the device that handles physiological signals
            dyscom = device.get_layer_dyscom() # Gets access to Dyscom-specific functions

            # Turn ON the measurement power on the device
            await dyscom.power_module(
                DyscomPowerModuleType.MEASUREMENT,
                DyscomPowerModulePowerType.SWITCH_ON
            )

            # Set up how we want to collect data
            init_params = DyscomInitParams()

            # Choose which signal types we want to collect:
            init_params.signal_type = [
                DyscomSignalType.BI,        # Bipolar channel
                DyscomSignalType.EMG_1,     # Electromyography channel 1
                #DyscomSignalType.EMG_2,     # Electromyography channel 2
                #DyscomSignalType.BREATHING  # Breathing signal
            ]

            # Choose the speed (samples per second) and quality of data
            # HR_MODE_4_KSPS means high resolution at 4000 samples per second
            # LP_MODE_2_KSPS means lower power mode at 2000 samples per second
            # eventually figure out how to edit these    
            init_params.register_map_ads129x.config_register_1.output_data_rate = (
                Ads129xOutputDataRate.HR_MODE_4_KSPS__LP_MODE_2_KSPS
            )
            init_params.register_map_ads129x.config_register_1.power_mode = (
                Ads129xPowerMode.HIGH_RESOLUTION
            )

            # Design filters for the data
            fs = 4000  # Sampling frequency in Hz (adjust if you change output_data_rate)
            # hp_b, hp_a = butter_highpass(5, fs)
            # notch_b, notch_a = butter_bandstop(58, 62, fs)
            # # For each channel, keep filter state (zi)
            # #hp_zi = [lfilter(hp_b, hp_a, [0], zi=None)[1] for _ in range(5)]
            # hp_zi = [lfilter_zi(hp_b, hp_a) * 0 for _ in range(5)]
            # #notch_zi = [lfilter(notch_b, notch_a, [0], zi=None)[1] for _ in range(5)]
            # notch_zi = [lfilter_zi(notch_b, notch_a) * 0 for _ in range(5)]
            # # Apply those settings to the device
            await dyscom.init(init_params)

            # Start sending live data from the device
            await dyscom.start()

            try:
                # Keep looping until the stop button is pressed
                while not stop_event.is_set():
                    # Try to get the latest data packet from the device
                    ack = dyscom.packet_buffer.get_packet_from_buffer()
                    #duration = time.time() - start_time  # Total duration of program in seconds
                    # If the packet is valid and contains live data
                    if ack and ack.command == Commands.DL_SEND_LIVE_DATA:
                        sld: PacketDyscomSendLiveData = ack

                        # Apply filters to the raw data from each channel
                        filtered_values = [] # List to hold filtered values for each channel
                        for ch in range(5): 
                            raw = sld.samples[ch].value
                            # # High-pass filter
                            # hp_out, hp_zi[ch] = apply_filter(raw, hp_b, hp_a, hp_zi[ch])
                            # # Notch filter
                            # notch_out, notch_zi[ch] = apply_filter(hp_out, notch_b, notch_a, notch_zi[ch])
                            # #notch_out.append(duration)
                            # filtered_values.append(notch_out)
                            # This approach uses simple IIR filters and maintains filter state for real-time streaming. 
                            filtered_values.append(raw)  # For now, just use raw values
                        
                        # Plot first 4 channels
                        for ch in range(4):
                            plot_helper.append_value(ch, filtered_values[ch])
                        plot_helper.update()
                        # Save all 5 channels to CSV
                        csv_helper.append_values(
                            ack.number,
                            filtered_values,
                            sld.time_offset,  # along with the time offset from the packet
                            
                        )

                    else:
                        # If no valid packet, just pause very briefly to reduce CPU use
                        await asyncio.sleep(0.001)

            finally:
                # Clean shutdown: stop data stream and turn off power
                await dyscom.stop()
                await dyscom.power_module(
                    DyscomPowerModuleType.MEASUREMENT,
                    DyscomPowerModulePowerType.SWITCH_OFF
                )

        asyncio.run(run())  # Actually start the process


    # Start the keyboard listener and data collection in separate threads
    t1 = threading.Thread(target=keyboard_listener, daemon=True)
    t2 = threading.Thread(target=data_acquisition, daemon=True)
    t1.start()
    t2.start()

    # Run the live plotting window (this will block the main thread)
    import fastplotlib as fpl
    fpl.loop.run()
    stop_event.set()  # Stop acquisition when window is closed

    t1.join()  # Wait for user input thread to finish
    t2.join()  # Wait for data thread to finish
    #plot_helper.close()  # Close the plotting figure

    csv_helper.stop()  # Finalize and close the CSV file
    connection.close()  # Close the connection to the device

    folder = os.path.join(".", "csv_files")  # Folder: ./csv_files
    os.makedirs(folder, exist_ok=True) 

    #folder = ".//csv_files"  # Default folder to save CSV file
    # folder = input("Enter folder to save the CSV file (default: ./csv_files):").strip()
    # if not folder:
    #     folder = ".//csv_files"  # Use current directory if nothing entered
    # os.makedirs(folder, exist_ok=True)  # Create folder if it doesn't exist

    # Ask the user where to save the data and rename the file
    final_csv = prompt_filename("values.csv")
    final_path = os.path.join(folder, final_csv) # Use current directory if nothing entered
    shutil.move(temp_csv, final_path)
    print(f"Data saved to {final_path}")  # Confirm file save to user

# Run everything if this file is executed directly
if __name__ == "__main__":
    main()
