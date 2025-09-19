"""
Combined Control Interface for Hasomed I24 (Dyscom) and P24 (Rehastim) Devices.

This script:
- Starts recording filtered EMG data from I24 (COM3),
- Turns on stimulation on P24 (COM4) only when EMG channel 1 or 2 is above a user-given threshold,
- Saves data to CSV,
- Stops when Enter is pressed.
"""

import asyncio  # For running asynchronous code (lets the program do multiple things at once)
import threading  # For running code in the background (like listening for keyboard input)
import shutil  # For moving files around
import os  # For interacting with the operating system (like making folders)
import time  # For measuring time and durations
from scipy.signal import butter, lfilter, lfilter_zi  # For filtering EMG signals

# Import device drivers and helpers for Hasomed I24 and P24
from science_mode_4 import DeviceI24, Commands, SerialPortConnection as SerialPortI24
from science_mode_4.dyscom.dyscom_send_live_data import PacketDyscomSendLiveData
from science_mode_4.dyscom.dyscom_types import DyscomInitParams, DyscomSignalType, DyscomPowerModuleType, DyscomPowerModulePowerType
from science_mode_4.dyscom.ads129x.ads129x_config_register_1 import Ads129xOutputDataRate, Ads129xPowerMode

from science_mode_4 import DeviceP24, MidLevelChannelConfiguration, ChannelPoint
from science_mode_4 import SerialPortConnection as SerialPortP24

from examples.utils.fastplotlib_utils import FastPlotLibHelper  # For live plotting
from examples.utils.csv_utils import CsvHelper  # For saving data to CSV

# GLOBAL SETTINGS - USER CONFIGURATION 
# check which COM ports your devices are connected to
I24_COM = "COM3"  # Serial port for I24 device (EMG recorder)
P24_COM = "COM4"  # Serial port for P24 device (stimulator)
stop_event = threading.Event()  # Used to signal the program to stop

# Stimulation parameters (fixed values)
params = {
    "amp1": 7,  # Amplitude for channel 1 (mA)
    "amp2": 7,  # Amplitude for channel 2 (mA)
    "freq1": 20,  # Frequency for channel 1 (Hz)
    "freq2": 20,  # Frequency for channel 2 (Hz)
    "pw1": 260,  # Pulse width for channel 1 (microseconds)
    "pw2": 260   # Pulse width for channel 2 (microseconds)
}

amp_max = 120  # Maximum allowed amplitude (mA)
freq_max = 2000  # Maximum allowed frequency (Hz)
pw_max = 10000  # Maximum allowed pulse width (microseconds)

emg_threshold = 10.0  # Default EMG threshold for turning on stimulation (can be changed by user)

# Function to create a highpass filter (removes low-frequency noise from EMG)
def butter_highpass(cutoff, fs, order=4):
    nyq = 0.5 * fs  # Nyquist frequency (half the sampling rate)
    return butter(order, cutoff / nyq, btype='high')

# Function to create a bandstop (notch) filter (removes 60 Hz powerline noise)
def butter_bandstop(lowcut, highcut, fs, order=2):
    nyq = 0.5 * fs
    return butter(order, [lowcut / nyq, highcut / nyq], btype='bandstop')

# Function to apply a filter to a single data point, keeping filter state
def apply_filter(data, b, a, zi):
    y, zo = lfilter(b, a, [data], zi=zi)  # Filter the data point
    return y[0], zo  # Return filtered value and updated filter state

# Function to ask the user for a filename to save the data
def prompt_filename(default="temp_values.csv"):
    name = input(f"Enter filename to save (default: {default}): ").strip()
    name = name + ".csv" if not name.endswith(".csv") else name
    return name if name else default

# Function to listen for Enter key to stop the program
def listen_for_input():
    input("Press Enter to stop...\n")
    stop_event.set()  # Signal the main loop to stop

# Function to build the stimulation pattern for both channels
def build_stim_config():
    # Each channel has 3 points: positive, zero, negative (biphasic pulse)
    c1 = [
        ChannelPoint(int(params["pw1"] / 2), int(params["amp1"])),
        ChannelPoint(int(params["pw1"] / 2), 0),
        ChannelPoint(int(params["pw1"] / 2), -int(params["amp1"]))
    ]
    c2 = [
        ChannelPoint(int(params["pw2"] / 2), int(params["amp2"])),
        ChannelPoint(int(params["pw2"] / 2), 0),
        ChannelPoint(int(params["pw2"] / 2), -int(params["amp2"]))
    ]
    # Create configuration objects for both channels
    cc1 = MidLevelChannelConfiguration(True, 3, params["freq1"], c1)
    cc2 = MidLevelChannelConfiguration(True, 3, params["freq2"], c2)
    return [cc1, cc2]

start_time = time.time()  # Record the start time of the program

async def main():
    # Ask user for EMG threshold (the value above which stimulation turns on)
    # try:
    #     emg_threshold = float(input("Enter EMG threshold (e.g., 10.0): "))
    # except Exception:
    #     print("Invalid input, using default threshold of 10.0")
    #     emg_threshold = 10.0

    stim_on = False  # Track whether stimulation is currently ON

    # --- Setup P24 Stimulator ---
    stim_connection = SerialPortP24(P24_COM)  # Open connection to P24 device
    stim_connection.open()
    stim_device = DeviceP24(stim_connection)
    await stim_device.initialize()  # Initialize the P24 device
    stim_layer = stim_device.get_layer_mid_level()  # Get the mid-level control layer
    await stim_layer.init(do_stop_on_all_errors=True)  # Initialize with error handling

    # --- Setup I24 Recorder ---
    record_connection = SerialPortI24(I24_COM)  # Open connection to I24 device
    record_connection.open()
    record_device = DeviceI24(record_connection)
    await record_device.initialize()  # Initialize the I24 device
    dyscom = record_device.get_layer_dyscom()  # Get the Dyscom control layer

    # --- Configure I24 measurement parameters ---
    init_params = DyscomInitParams()
    init_params.signal_type = [DyscomSignalType.EMG_1, DyscomSignalType.EMG_2]  # Record EMG channels 1 and 2

    # Set the sampling rate and resolution for EMG recording
    init_params.register_map_ads129x.config_register_1.output_data_rate = Ads129xOutputDataRate.HR_MODE_4_KSPS__LP_MODE_2_KSPS
    init_params.register_map_ads129x.config_register_1.power_mode = Ads129xPowerMode.HIGH_RESOLUTION

    fs = 4000  # Sampling frequency in Hz
    hp_b, hp_a = butter_highpass(5, fs)  # Highpass filter coefficients
    notch_b, notch_a = butter_bandstop(58, 62, fs)  # Notch filter coefficients
    hp_zi = [lfilter_zi(hp_b, hp_a) * 0 for _ in range(5)]  # Filter state for each channel
    notch_zi = [lfilter_zi(notch_b, notch_a) * 0 for _ in range(5)]  # Filter state for each channel

    # --- Start I24 device ---
    await dyscom.power_module(DyscomPowerModuleType.MEASUREMENT, DyscomPowerModulePowerType.SWITCH_ON)
    await dyscom.init(init_params)
    await dyscom.start()

    # --- Setup live plotting ---
    plot_helper = FastPlotLibHelper({
        0: ["EMG CH1", "r"],   # EMG channel 1, red
        1: ["EMG CH2", "b"],   # EMG channel 2, blue
        2: ["Stim Amp1", "g"], # Stimulation amplitude channel 1, green
        3: ["Stim Amp2", "m"]  # Stimulation amplitude channel 2, magenta
    }, 1000)  # Show 1000 samples at a time

    # --- Setup CSV output ---
    csv_columns = [
        "packet_nr",    # Packet number from the device
        "EMG_CH1",      # Filtered EMG channel 1
        "EMG_CH2",      # Filtered EMG channel 2
        "EMG_CH3",      # (Unused, but included for compatibility)
        "EMG_CH4",      # (Unused, but included for compatibility)
        "EMG_CH5",      # (Unused, but included for compatibility)
        "stim_amp1",    # Stimulation amplitude channel 1
        "stim_freq1",   # Stimulation frequency channel 1
        "stim_pw1",     # Stimulation pulse width channel 1
        "stim_amp2",    # Stimulation amplitude channel 2
        "stim_freq2",   # Stimulation frequency channel 2
        "stim_pw2",     # Stimulation pulse width channel 2
        "total_runtime",# Time since script started (seconds)
        "time_offset"   # Time offset from the device (microseconds)
    ]
    csv_helper = CsvHelper("temp_values.csv", csv_columns)  # Create CSV helper
    csv_helper.start()  # Start writing to CSV

    # --- Start background thread to listen for Enter key ---
    threading.Thread(target=listen_for_input, daemon=True).start()
    print(f">>> Running. Stimulation will turn ON when EMG CH1 or CH2 > {emg_threshold}. Press Enter to stop...")

    # --- Main data collection loop ---
    while not stop_event.is_set():
        ack = dyscom.packet_buffer.get_packet_from_buffer()  # Get latest data packet from I24
        if ack and ack.command == Commands.DL_SEND_LIVE_DATA:
            sld: PacketDyscomSendLiveData = ack
            filtered = []  # List to hold filtered values for each channel
            for ch in range(5):
                raw = sld.samples[ch].value  # Raw EMG value from channel
                hp_out, hp_zi[ch] = apply_filter(raw, hp_b, hp_a, hp_zi[ch])  # Highpass filter
                notch_out, notch_zi[ch] = apply_filter(hp_out, notch_b, notch_a, notch_zi[ch])  # Notch filter
                filtered.append(notch_out)  # Store filtered value

            # --- Update the live plot ---
            plot_helper.append_value(0, filtered[0])  # EMG CH1
            plot_helper.append_value(1, filtered[1])  # EMG CH2
            plot_helper.append_value(2, params["amp1"] if stim_on else 0)  # Show stim amplitude if ON, else 0
            plot_helper.append_value(3, params["amp2"] if stim_on else 0)
            plot_helper.update()

            # --- Show current stimulation parameters as text on the plot ---
            overlay_text = (
                f"CH1: freq={params['freq1']} Hz, pw={params['pw1']} µs,  {'ON' if stim_on_ch1 else 'OFF'} \n"
                f"CH2: freq={params['freq2']} Hz, pw={params['pw2']} µs,  {'ON' if stim_on_ch2 else 'OFF'}  \n"
                #f"Stimulation: {'ON' if stim_on else 'OFF'}"
            )
            if hasattr(plot_helper, "set_text_overlay"):
                plot_helper.set_text_overlay(overlay_text)

            duration = time.time() - start_time  # How long the script has been running

            # --- Save data to CSV ---
            csv_row = [
                ack.number,              # Packet number
                *filtered,               # All filtered EMG channels
                params["amp1"] if stim_on else 0,  # stim_amp1
                params["freq1"],                 # stim_freq1
                params["pw1"],                   # stim_pw1
                params["amp2"] if stim_on else 0,  # stim_amp2
                params["freq2"],                 # stim_freq2
                params["pw2"],                   # stim_pw2
                duration                         # total_runtime
            ]
            csv_helper.append_values(package_nr=int(csv_row[0]), values=csv_row[1:], time_delta=sld.time_offset)

            # --- Turn stimulation ON/OFF based on EMG threshold for each channel independently ---
            # Track stim state for each channel
            if 'stim_on_ch1' not in locals():
                stim_on_ch1 = False
            if 'stim_on_ch2' not in locals():
                stim_on_ch2 = False

            # Build configs for both channels
            zero_c1 = [
                ChannelPoint(int(params["pw1"] / 2), 0),
                ChannelPoint(int(params["pw1"] / 2), 0),
                ChannelPoint(int(params["pw1"] / 2), 0)
            ]
            zero_c2 = [
                ChannelPoint(int(params["pw2"] / 2), 0),
                ChannelPoint(int(params["pw2"] / 2), 0),
                ChannelPoint(int(params["pw2"] / 2), 0)
            ]
            # Default: use params for both channels
            c1 = [
                ChannelPoint(int(params["pw1"] / 2), int(params["amp1"])) if filtered[0] > emg_threshold else ChannelPoint(int(params["pw1"] / 2), 0),
                ChannelPoint(int(params["pw1"] / 2), 0),
                ChannelPoint(int(params["pw1"] / 2), -int(params["amp1"])) if filtered[0] > emg_threshold else ChannelPoint(int(params["pw1"] / 2), 0)
            ]
            c2 = [
                ChannelPoint(int(params["pw2"] / 2), int(params["amp2"])) if filtered[1] > emg_threshold else ChannelPoint(int(params["pw2"] / 2), 0),
                ChannelPoint(int(params["pw2"] / 2), 0),
                ChannelPoint(int(params["pw2"] / 2), -int(params["amp2"])) if filtered[1] > emg_threshold else ChannelPoint(int(params["pw2"] / 2), 0)
            ]
            cc1 = MidLevelChannelConfiguration(True, 3, params["freq1"], c1)
            cc2 = MidLevelChannelConfiguration(True, 3, params["freq2"], c2)
            await stim_layer.update([cc1, cc2])

            # Update stim_on_ch1/ch2 for overlay/plotting
            stim_on_ch1 = filtered[0] > emg_threshold
            stim_on_ch2 = filtered[1] > emg_threshold

        else:
            await asyncio.sleep(0.001)  # Wait a tiny bit before checking again

    # --- Shutdown and cleanup ---
    print(">>> Shutting down...")
    await dyscom.stop()  # Stop I24 recording
    await stim_layer.stop()  # Stop P24 stimulation
    await dyscom.power_module(DyscomPowerModuleType.MEASUREMENT, DyscomPowerModulePowerType.SWITCH_OFF)  # Power off I24
    record_connection.close()  # Close I24 connection
    stim_connection.close()  # Close P24 connection
    csv_helper.stop()  # Stop writing to CSV

    # --- Ask user for final filename and move the CSV file ---
    final_csv = prompt_filename('temp_values.csv')
    folder = os.path.join(".", "csv_files")
    os.makedirs(folder, exist_ok=True)
    final_path = os.path.join(folder, final_csv)
    shutil.move('temp_values.csv', final_path)
    print(f"Data saved to {final_path}")

if __name__ == "__main__":
    asyncio.run(main())  # Start the main function
    