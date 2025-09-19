"""
Combined Control Interface for Hasomed I24 (Dyscom) and P24 (Rehastim) Devices.

This script:
- Starts recording filtered EMG data from I24 (COM3),
- Starts electrical stimulation on P24 (COM4),
- Allows live adjustments to stimulation parameters using keyboard controls,
- Stops both when Enter is pressed.

"""

# Import required Python libraries and modules for functionality
import asyncio  # Allows handling tasks that run asynchronously, like live data collection
import threading  # Used for running multiple operations at once (e.g., listening for keyboard input while collecting data)
import shutil  # Used to move files around (e.g., renaming the CSV after saving)
import os  # Interacts with the operating system (not directly used in this script) 
import time # Used for time-related functions, like measuring how long the script runs 
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from scipy.signal import butter, lfilter, lfilter_zi # Used for signal processing, specifically filtering the EMG data
import keyboard  # Used to listen for keyboard input to adjust stimulation parameters

# IMPORT FOR I24 (MEASUREMENT)
from science_mode_4 import DeviceI24, Commands, SerialPortConnection as SerialPortI24
from science_mode_4.dyscom.dyscom_send_live_data import PacketDyscomSendLiveData
from science_mode_4.dyscom.dyscom_types import DyscomInitParams, DyscomSignalType, DyscomFilterType, DyscomPowerModuleType, DyscomPowerModulePowerType
from science_mode_4.dyscom.ads129x.ads129x_config_register_1 import Ads129xOutputDataRate, Ads129xPowerMode

# IMPORT FOR P24 (STIMULATION)
from science_mode_4 import DeviceP24, MidLevelChannelConfiguration, ChannelPoint
from science_mode_4 import SerialPortConnection as SerialPortP24

# Plotting helper (custom module provided with examples)
from ccfes_functions import FastPlotLibHelper
#from examples.utils.fastplotlib_utils import FastPlotLibHelper
#from .ccfes_functions import CsvHelper
from examples.utils.csv_utils import CsvHelper

# GLOBAL SETTINGS - USER CONFIGURATION 
# check which COM ports your devices are connected to
I24_COM = "COM4" 
P24_COM = "COM3"
stop_event = threading.Event() # Event to signal when to stop the program

# Starting parameters for stimulation
params = {
    "amp1": 5, # mA, channel 1 amplitude
    "amp2": 5, # mA
    "freq1": 20,  # Hz
    "freq2": 20, # Hz
    "pw1": 260,  # microseconds
    "pw2": 260 # microseconds
}

# Change steps when keys are pressed
delta_amp = 0.25 # Amplitude change step in mA
delta_freq = 5 # Frequency change step in Hz
delta_pw = 10 # Pulse width change step in microseconds

#also edit line ~214 I24 initialization parameters to the type of EMG you want to record

# Maximum allowed values for safety
amp_max = 120 # maximum amplitude in mA
    #0-130 in manual
freq_max = 2000 # maximum frequency in Hz
    #in manual, impulse repetition period is .5-16383 ms
    # .0610 - 2000 Hz
pw_max = 10000 # maximum pulse width in microseconds
    #10-65520 in manual

amp_history = {"amp1": [], "amp2": [], "time": []}
time_index = 0


# FILTER DESIGN FOR I24
# def butter_highpass(cutoff, fs, order=4): # Design a highpass filter to remove low-frequency noise
#     nyq = 0.5 * fs 
#     return butter(order, cutoff / nyq, btype='high') 
#         # order - the order of the filter, higher order means steeper roll-off
#         # cutoff - frequency below which the filter will attenuate signals
#         # btype - type of filter, 'high' means highpass

# def butter_bandstop(lowcut, highcut, fs, order=2): # Design a bandstop filter to remove noise
#     nyq = 0.5 * fs
#     return butter(order, [lowcut / nyq, highcut / nyq], btype='bandstop')
#         # lowcut and highcut - frequencies to stop, in Hz
#         # btype - type of filter, 'bandstop' means it will block signals in the specified frequency range   

# def apply_filter(data, b, a, zi): # Apply a filter to the data
#     y, zo = lfilter(b, a, [data], zi=zi) 
#     return y[0], zo # Return the filtered data and the new filter state

# Asks the user what filename to save the data under
def prompt_filename(default="temp_values.csv"):
    name = input(f"Enter filename to save (default: {default}): ").strip()
    name = name + ".csv" if not name.endswith(".csv") else name # Ensure it ends with .csv
    return name if name else default  # Use default if user enters nothing

# KEYBOARD CONTROLS
stop_event = threading.Event() # Event to signal when to stop the program

def listen_for_input():
    input("Press Enter to stop...\n")
    stop_event.set()

# Listens for amplitude changes via keyboard
# 1+w/q = CH1 up/down, 2+w/q = CH2 up/down
def listen_for_amp():
    while not stop_event.is_set():
        if keyboard.is_pressed('1'):
            if keyboard.is_pressed('w'):
                params["amp1"] = min(amp_max, params["amp1"] + delta_amp)
                print(f"[CH1] Amplitude increased: {params['amp1']} mA")
                keyboard.wait('r')
            elif keyboard.is_pressed('q'):
                params["amp1"] = max(0.1, params["amp1"] - delta_amp)
                print(f"[CH1] Amplitude decreased: {params['amp1']} mA")
                keyboard.wait('r')
        elif keyboard.is_pressed('2'):
            if keyboard.is_pressed('w'):
                params["amp2"] = min(amp_max, params["amp2"] + delta_amp)
                print(f"[CH2] Amplitude increased: {params['amp2']} mA")
                keyboard.wait('r')
            elif keyboard.is_pressed('q'):
                params["amp2"] = max(0.1, params["amp2"] - delta_amp)
                print(f"[CH2] Amplitude decreased: {params['amp2']} mA")
                keyboard.wait('r')

# Listens for frequency changes
# 1+s/a = CH1 up/down, 2+s/a = CH2 up/down
def listen_for_freq():
    while not stop_event.is_set():
        if keyboard.is_pressed('1'):
            if keyboard.is_pressed('s'):
                params["freq1"] = min(freq_max, params["freq1"] + delta_freq)
                print(f"[CH1] Frequency increased: {params['freq1']} Hz")
                keyboard.wait('r')
            elif keyboard.is_pressed('a'):
                params["freq1"] = max(1, params["freq1"] - delta_freq)
                print(f"[CH1] Frequency decreased: {params['freq1']} Hz")
                keyboard.wait('r')
        elif keyboard.is_pressed('2'):
            if keyboard.is_pressed('s'):
                params["freq2"] = min(freq_max, params["freq2"] + delta_freq)
                print(f"[CH2] Frequency increased: {params['freq2']} Hz")
                keyboard.wait('r')
            elif keyboard.is_pressed('a'):
                params["freq2"] = max(1, params["freq2"] - delta_freq)
                print(f"[CH2] Frequency decreased: {params['freq2']} Hz")
                keyboard.wait('r')

# Listens for pulse width changes
# 1+x/z = CH1 up/down, 2+x/z = CH2 up/down
def listen_for_pw():
    while not stop_event.is_set():
        if keyboard.is_pressed('1'):
            if keyboard.is_pressed('x'):
                params["pw1"] = min(pw_max, params["pw1"] + delta_pw)
                print(f"[CH1] Pulse width increased: {params['pw1']} µs")
                keyboard.wait('r')
            elif keyboard.is_pressed('z'):
                params["pw1"] = max(1, params["pw1"] - delta_pw)
                print(f"[CH1] Pulse width decreased: {params['pw1']} µs")
                keyboard.wait('r')
        elif keyboard.is_pressed('2'):
            if keyboard.is_pressed('x'):
                params["pw2"] = min(pw_max, params["pw2"] + delta_pw)
                print(f"[CH2] Pulse width increased: {params['pw2']} µs")
                keyboard.wait('r')
            elif keyboard.is_pressed('z'):
                params["pw2"] = max(1, params["pw2"] - delta_pw)
                print(f"[CH2] Pulse width decreased: {params['pw2']} µs")
                keyboard.wait('r')

# BUILD STIM PATTERN
# Builds stimulation configuration for both channels based on current params
# This is called before every stimulation update
def build_stim_config():
    # Create channel points for both channels based on current parameters
    # Each channel has three points: positive, zero, and negative
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
    # Create mid-level channel configurations for both channels
    cc1 = MidLevelChannelConfiguration(True, 3, params["freq1"], c1) 
    cc2 = MidLevelChannelConfiguration(True, 3, params["freq2"], c2)
    # True - means the channel is enabled
    # 3 - means the channel is in bipolar mode (two electrodes) 
    return [cc1, cc2]

# MAIN RUN LOOP
start_time = time.time() # Record start time before main loop 
async def main():
    #  Setup P24 Stimulator 
    stim_connection = SerialPortP24(P24_COM) # Open connection to P24 device
    stim_connection.open()
    stim_device = DeviceP24(stim_connection)
    await stim_device.initialize() # Initialize the P24 device
    stim_layer = stim_device.get_layer_mid_level() # Get the mid-level layer for stimulation control
    await stim_layer.init(do_stop_on_all_errors=True) # Initialize the mid-level layer with error handling

    # Setup I24 Recorder 
    record_connection = SerialPortI24(I24_COM) # Open connection to I24 device
    record_connection.open()
    record_device = DeviceI24(record_connection) # Create an instance of the I24 device
    await record_device.initialize() # Initialize the I24 device
    dyscom = record_device.get_layer_dyscom() # Get the Dyscom layer for I24 control

    # Configure I24 measurement
    init_params = DyscomInitParams() # Create initialization parameters for I24
    init_params.signal_type = [DyscomSignalType.EMG_1, DyscomSignalType.EMG_2]
        # BI - bipolar input, 
        # EMG_1 and EMG_2 - EMG channels, 
        # BREATHING - breathing signal
    #init_params.filter = [DyscomFilterType.PREDEFINED_FILTER_1]

    # Choose the speed (samples per second) and quality of data 
    init_params.register_map_ads129x.config_register_1.output_data_rate = Ads129xOutputDataRate.HR_MODE_2_KSPS__LP_MODE_1_KSPS
    init_params.register_map_ads129x.config_register_1.power_mode = Ads129xPowerMode.HIGH_RESOLUTION
        # HR_MODE_2_KSPS means high resolution at 2000 samples per second
        # LP_MODE_1_KSPS means lower power mode at 1000 samples per second
        # LOW_POWER is used to save battery life, but it reduces the data quality
        # HR_MODE is used for high-quality data, but it consumes more power
        # how to edit these; src\science_mode_4\dyscom\ads129x\ads129x_config_register_1.py


    fs = 2000 # Sampling frequency in Hz (adjust if you change output_data_rate)
    # hp_b, hp_a = butter_highpass(5, fs) 
    # notch_b, notch_a = butter_bandstop(58, 62, fs)
    # hp_zi = [lfilter_zi(hp_b, hp_a) * 0 for _ in range(5)]
    #     # Initialize filter state for filter for each channel
    #     # lfilter_zi returns the initial state of the filter, which is zeroed out here
    #     # lfilter_zi is used to create a zero-initialized filter state for real-time processing 
    #     # lfilter returns the filtered output and the new filter state (zi) 
    #     # in range(5) means we have 5 channels (4 EMG + 1 breathing)
    #     # for each channel, we keep the initial state of the filter, zi
    # notch_zi = [lfilter_zi(notch_b, notch_a) * 0 for _ in range(5)]


    await dyscom.power_module(DyscomPowerModuleType.MEASUREMENT, DyscomPowerModulePowerType.SWITCH_ON)
    await dyscom.init(init_params)
    await dyscom.start()


    plot_helper = FastPlotLibHelper({
        0: ["EMG CH1", "r"],   # EMG channel 1, red
        1: ["EMG CH2", "b"],   # EMG channel 2, blue
        2: ["Stim Amp1", "g"], # Stimulation amplitude channel 1, green
        3: ["Stim Amp2", "m"]  # Stimulation amplitude channel 2, magenta
        }, 
    max_value_count=1000) # 1000 samples shown in the plot at a time

    # csv_helper = CsvHelper("temp_values.csv", ["packet_nr", "Channel 1", "Channel 2", "Channel 3", "Channel 4", "Channel 5", "time_delta"])
    # csv_helper.start()
    csv_columns = [
    "packet_nr", # Packet number
    "EMG_CH1", # Filtered EMG channel 1
    "EMG_CH2", 
    "EMG_CH3", 
    "EMG_CH4", 
    "EMG_CH5", 
    "stim_amp1", 
    "stim_freq1", 
    "stim_pw1",
    "stim_amp2", # amplitude in mA
    "stim_freq2", # frequency in Hz
    "stim_pw2", # microseconds
    "total_runtime", # time in seconds
    "time_offset"] # time offset from the device, in microseconds

    csv_helper = CsvHelper("temp_values.csv", csv_columns) 
    csv_helper.start()


    #  Start Listeners for keyboard inputs 
    for fn in [listen_for_input, listen_for_amp, listen_for_freq, listen_for_pw]:
        threading.Thread(target=fn, daemon=True).start()
         # Start each listening thread in a separate thread so they run concurrently with the main loop

    print(">>> Running. Use keys to adjust stimulation. Press Enter to stop...")

    #  Main Loop 
    while not stop_event.is_set():
        # I24: Get and process packet
        ack = dyscom.packet_buffer.get_packet_from_buffer() # Try to get the latest data packet from the device
        
        # If the packet is valid and contains live data
        if ack and ack.command == Commands.DL_SEND_LIVE_DATA:
            sld: PacketDyscomSendLiveData = ack
            # Apply filters to the raw data from each channel
            filtered = [] # List to hold filtered values for each channel
            for ch in range(5):
                raw = (sld.samples[ch].value)
            #     # highpass filter
            #     hp_out, hp_zi[ch] = apply_filter(raw, hp_b, hp_a, hp_zi[ch])
            #     # notch filter
            #     notch_out, notch_zi[ch] = apply_filter(hp_out, notch_b, notch_a, notch_zi[ch])
            #     filtered.append(notch_out)
            # # This approach uses simple IIR filters and maintains filter state for real-time streaming. 
                filtered.append(raw)

            plot_helper.append_value(0, filtered[0])         # EMG CH1
            plot_helper.append_value(1, filtered[1])         # EMG CH2
            plot_helper.append_value(2, params["amp1"])      # Stim Amp1
            plot_helper.append_value(3, params["amp2"])      # Stim Amp2
            plot_helper.update()
            
            duration = time.time() - start_time  # Total duration of program in seconds

            #csv_helper.append_values(ack.number, filtered, sld.time_offset)
            # Build full row of data
            csv_row = [
                ack.number,              # Packet number
                *filtered,               # EMG_CH1-CH5 (filtered values)
                params["amp1"],          # stim_amp1
                params["freq1"],         # stim_freq1
                params["pw1"],           # stim_pw1
                params["amp2"],          # stim_amp2
                params["freq2"],         # stim_freq2
                params["pw2"],           # stim_pw2
                duration ]                # total_runtime
            csv_helper.append_values(package_nr=int(csv_row[0]), values=csv_row[1:], time_delta=sld.time_offset)
        
        else:
            # If no valid packet, just pause very briefly to reduce CPU use
            await asyncio.sleep(0.001)


        # P24: Update stimulation config
        configs = build_stim_config()
        await stim_layer.update(configs) 
        await asyncio.sleep(0.001) 

    #  Shutdown 
    print(">>> Shutting down...")
    await dyscom.stop()
    await stim_layer.stop()
    await dyscom.power_module(DyscomPowerModuleType.MEASUREMENT, DyscomPowerModulePowerType.SWITCH_OFF)
    record_connection.close()
    stim_connection.close()
    csv_helper.stop()

    # Ask the user where to save the data and rename the file
    final_csv = prompt_filename('temp_values.csv')  # Prompt for filename, default is 'temp_values.csv'
    folder = os.path.join(".", "csv_files")  # Folder: /ccfes-setup/csv_files
    os.makedirs(folder, exist_ok=True) 
    final_path = os.path.join(folder, final_csv) # Use current directory if nothing entered
    shutil.move('temp_values.csv', final_path) # Move the temporary file to the final location

    print(f"Data saved to {final_path}")  # Confirm file save to user

if __name__ == "__main__":
    asyncio.run(main())


