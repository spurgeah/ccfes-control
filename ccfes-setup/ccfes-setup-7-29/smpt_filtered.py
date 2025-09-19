"""
adds 
-/convert to units
-/highpass bandpass filters
-/rectify
-channel 1 - check toggle bias injection / automatic switching
-channel 4 - check breathing signal criteria
-/switch to low power mode/low resolution mode 

"""


import asyncio
import shutil
import threading
import fastplotlib as fpl
from timeit import default_timer as timer

from science_mode_4 import DeviceI24, Commands, SerialPortConnection, dyscom
from science_mode_4.dyscom.ads129x.ads129x_config_register_1 import Ads129xOutputDataRate, Ads129xPowerMode
from science_mode_4.dyscom.dyscom_get_operation_mode import PacketDyscomGetAckOperationMode
from science_mode_4.dyscom.dyscom_send_live_data import PacketDyscomSendLiveData
from science_mode_4.dyscom.dyscom_types import DyscomGetType, DyscomInitParams, DyscomPowerModulePowerType, DyscomPowerModuleType, DyscomSignalType
from science_mode_4.protocol.types import ResultAndError
from science_mode_4.utils.logger import logger
#from science_mode_4.utils.logger import logger
from scipy.signal import butter, lfilter, lfilter_zi  # Used for filtering the live data to remove noise 

from examples.utils.fastplotlib_utils import FastPlotLibHelper
from examples.utils.example_utils import ExampleUtils
from examples.utils.csv_utils import CsvHelper

# FILTER DESIGN FOR I24-----------------------------
def butter_highpass(cutoff, fs, order=4): # Design a highpass filter to remove low-frequency noise
    nyq = 0.5 * fs 
    return butter(order, cutoff / nyq, btype='high') 
        # order - the order of the filter, higher order means steeper roll-off
        # cutoff - frequency below which the filter will attenuate signals
        # btype - type of filter, 'high' means highpass

def butter_bandstop(lowcut, highcut, fs, order=2): # Design a bandstop filter to remove noise
    nyq = 0.5 * fs
    return butter(order, [lowcut / nyq, highcut / nyq], btype='bandstop')
        # lowcut and highcut - frequencies to stop, in Hz
        # btype - type of filter, 'bandstop' blocks signals in the specified frequency range   

def apply_filter(data, b, a, zi): # Apply a filter to the data
    y, zo = lfilter(b, a, [data], zi=zi) 
    return y[0], zo # Return the filtered data and the new filter state

def main():
    """Main function"""

    # Setup plot helper
    plot_helper = FastPlotLibHelper(
        {0: ["Channel 1", "b"], 
         1: ["Channel 2", "r"], 
         2: ["Channel 3", "y"], 
         3: ["Channel 4", "g"]},
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
        
       

        await dyscom.power_module(DyscomPowerModuleType.MEASUREMENT, 
                                  DyscomPowerModulePowerType.SWITCH_ON)

        # Configure signal types and sample rate
        init_params = DyscomInitParams()
        init_params.signal_type = [
            DyscomSignalType.BI, 
            DyscomSignalType.EMG_1, 
            DyscomSignalType.EMG_2, 
            DyscomSignalType.BREATHING
            ]
        
        # LOW SAMPLING RATE FOR LOW POWER MODE
        init_params.register_map_ads129x.config_register_1.output_data_rate = (
            Ads129xOutputDataRate.HR_MODE_500_SPS__LP_MODE_250_SPS)
        init_params.register_map_ads129x.config_register_1.power_mode = (
            Ads129xPowerMode.LOW_POWER)
        # HR_MODE_2_KSPS means high resolution at 2000 samples per second
        # LP_MODE_1_KSPS means lower power mode at 1000 samples per second
        # LOW_POWER is used to save battery life, but it reduces the data quality
        # HR_MODE is used for high-quality data, but it consumes more power
        # how to edit these; src\science_mode_4\dyscom\ads129x\ads129x_config_register_1.py

        VREF = 4.0  # volts, automatically set at 4.0 unless add init_param
        GAIN = 6 #automatically set at 6 unless add init_param
        CURRENT = 30e-6  # 30 uA injected - page 15 of ads129x chip manual


        fs = 250 # Sampling frequency in Hz (adjust if you change output_data_rate)
        hp_b, hp_a = butter_highpass(5, fs) 
        notch_b, notch_a = butter_bandstop(58, 62, fs)
        hp_zi = [lfilter_zi(hp_b, hp_a) * 0 for _ in range(5)]
            # Initialize filter state for filter for each channel
            # lfilter_zi returns the initial state of the filter, which is zeroed out here
            # lfilter_zi is used to create a zero-initialized filter state for real-time processing 
            # lfilter returns the filtered output and the new filter state (zi) 
            # in range(5) means we have 5 channels (4 EMG + 1 blank for some reason)
            # for each channel, we keep the initial state of the filter, zi
        notch_zi = [lfilter_zi(notch_b, notch_a) * 0 for _ in range(5)]
    

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
                        converted = [0] * 5  # Initialize converted values for 5 channels
                        for i in range(4): #used to be 4
                            raw = sld.samples[i].value #raw ADC value 

                            #convert to respective channel units
                            if i == 0:
                                #converted[i] = (raw / (2**24)) * (VREF / GAIN) / CURRENT # convert to ohms for BI
                                converted[i] = ((raw * VREF * 2) / ((2**24)*GAIN)) / CURRENT # convert to microvolts
                                # Ohms = Voltage_measured / Current_injected
                                # 2**23: ADS129x is a 24‑bit ADC, so the full‑scale range is ±2^23.
                                # nope, 2 ^ N bits (24)
                                # VREF: ADC reference voltage (4.0 V in your code).
                                # GAIN: Programmable amplifier gain (6× here).
                                # For EMG channels, result × 1e6 to get microvolts.  

                            else:
                                # converted[i] = (raw / (2**24)) * (VREF / GAIN) * 1e6  # convert to microvolts
                                converted[i] = ((raw * VREF * 2) / ((2**24)*GAIN)) * 1e6  # convert to microvolts
                            
                            # Subtract DC offset (mean) using exponential moving average
                            alpha = 0.001  # Smoothing factor for mean estimate (adjust as needed)
                            if 'dc_offset' not in locals():
                                dc_offset = [0] * 5  # Initialize for all 5 channels
                            # Update running mean
                            dc_offset[i] = (1 - alpha) * dc_offset[i] + alpha * converted[i]
                            # Remove mean
                            converted[i] -= dc_offset[i]

        
                            # Apply highpass filter
                            converted[i], hp_zi[i] = apply_filter(converted[i], hp_b, hp_a, hp_zi[i])
                            # Apply bandstop filter 
                            converted[i], notch_zi[i] = apply_filter(converted[i], notch_b, notch_a, notch_zi[i])
                            
                            # Rectify the signal
                            converted[i] = abs(converted[i])  # Rectification
                            
                            #for ch in range(4):
                            # Append the value to the plot helper
                            plot_helper.append_value(i, converted[i])
                        plot_helper.update()

                        csv_helper.append_values(ack.number,
                            # sld.samples[0].value, sld.samples[1].value,
                            # sld.samples[2].value, sld.samples[3].value,
                            # sld.samples[4].value
                            converted,
                            sld.time_offset)
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
            print(f"Data saved to {final_path}")  # Confirm file save to user

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
