## To Do 7/28
- Channel 4 is reading a miniscule signal no matter what, and I cannot find any hardware issues, so why? 
    -/ check breathing mode criteria, could find none
    - look in chip manual
-/ verify BI injected current amplitude, 
    -/ chip manual says 30 micro amps on page 15..?
- ccfes_runlive.py

write a python code that takes measured ADC values converted to voltage
 - removes the mean EMG value from the raw signal
 - creates and applies filter 
 - rectifies the signal

 https://scientificallysound.org/2016/08/18/python-analysing-emg-signals-part-3/
 
 - reads emg for 5 seconds
 - IF average of the last 15 packet values is above a certain threshold, the stimulation is turned on
 when the average dips below the threshold, the stimulation turns off until the user ends the program by pressing enter

what we got 
- ccfes_runlive - runs, activates stim?, measurement levels all flatline
- smpt_filtered - no valid packet 109
actually fine if only the I24 is plugged in
either assign command ports to the proper devices, check ccfes_runlive
now why is runlive flatlining




does dyscom_send_live_data.py convert the values to units anywhere? or is it outputting the raw ADC values to smpt_filtered.py (for example, sld.samples[0].value)?
does the signal need to be normalized as well for an EMG reading in smpt_filtered.py? What should I add to the python code? 
what should the conversion to units equation look like for a device with a baud rate of 3,000,000, 8 data bits, 2 stop bits?

for the hasomed I24 measuring device, I have questions about coding and the measurement table page 32, explain to an engineering student
- explain the technical specifications measurements table 
- what do the values in the * column mean, explain to a non-programmer
- input range of referance voltages
- what is BI frequency, and what does it affect in the output?
- does GAIN_12 mean the signal is just multiplied by 12?
- what are register values and how are they used to assign configurations to the device? 
- what are the units be for all the signal types in table 15?



## Upon startup
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass 
conda activate i24setup2 
cd ccfes-setup 
cd ccfes-setup-7-29
$env:PYTHONPATH="Y:\Hasomed Code\HasomedSetup13\ScienceMode4Python"

cd ..
cd ..
cd examples
cd dyscom

# if 'no module named examples'
$env:PYTHONPATH="Y:\Hasomed Code\HasomedSetup13\ScienceMode4Python"

# device manager from powershell - devmgmt.msc 

# check COM ports
# List all COM ports
Get-WmiObject Win32_SerialPort | Select-Object Name, DeviceID, Description


## CCFES Python Library folder setup 
- csv_files folder - where all the csv files are saved to
- dyscom_runlive2.py - Alisa's version of ScienceMode4Python dyscom files to run data collection from the I24 live, then save to a CSV file 
    - 0 - only sinusodal, no movement detection
    - 1 - detects sinusoidal signals, not movement
    - 4 - no filters, raw data
    - 5 - OG code, + gain settings
- midlevel_runlive.py - scienceMode4Python version of pyScienceMode P24 runlive code (2 channels)
    - 2 - changes plotting functions to fastplotlib.utils functions
- both_live.py - just runs P24 and I24 simultaneously, no talking to each other

- ccfes_runlive.py - P24 parameters are based on I24 measurement
- smpt_GUI_copy.py - reads exactly what the smpt_software does
    - _csv - same thing, but saves output to csv
    - _filtered - adds EMG filters
## Alisa's computer COM ports
1 - top right?
2 - 
3 - USB-A, bottom left
4 - USB-C, bottom right

## I24 device information
- 3 channels for measurement and 1 for impedance measurement
    ch1 ALWAYS RED has to be bio impedance? YES
    green - emg & BI, 2
    red - output for BI, 1
    white - common more rejection
    black - emg, 3
    yellow - emg, 4
- ADS1294R measurement chip 
-surface emg sampling rate - 1k - 2k Hz 

## good EMG signal values
| Condition          | EMG Signal Behavior                       |
| ------------------ | ----------------------------------------- |
| **At rest**        | Baseline, small fluctuations, \~±10–50 μV |
| **During flexion** | Large bursts, ±100–1000 μV or more        |
| **After flexion**  | Returns to baseline smoothly              | 

## Where to find parameters
- channel_settings_register - gain, 
- config_register_1 - power mode, output data rate, 
- config_register_3 - referance voltage
- config_register_4 - 
- dyscom_types - signal type, get info, power module type

## To-Do 7/25
- ex_dys_fpl_csv_filtered.py RENAMED smpt_filtered.py 
    -/convert ADC values to channel units
        VREF = Reference voltage (usually 2.42 V for ADS1299, check your device spec!)
        GAIN = ADC PGA gain (often 24 for EMG)
        2**23 = Max 24-bit signed integer range
        - ch 1 is in ohms for bioimpedance
    -/highpass and bandpass filters
    -/rectify each signal 
    -/switch to low power mode/low resolution mode 
- verify BI injected current amplitude, 
    -/ found nothing in documentation
    - However, typical bioimpedance systems at the I24’s scale often use an AC injection current between 50 µA and 100 µA, especially when aiming to measure muscle or tissue 
    impedance with minimal discomfort and high safety. For example, many similar systems use programmable currents in that range for 50–333 kHz measurements
    -/ chip manual says 30 micro amps on page 15
-/ how do ex_dys_fpl_csv.py and dyscom_runlive1.py output different values into the CSV
    -ex; low power, 500 sps
    -dys; high res, 4k sps. 
    raw_value: .value from the packet
- With ex_dys_fpl_csv.py, after 1000 samples, channel 1's signal flips from negative to positive, why? 
    -/ check toggle bias injection / automatic switching, found nothing in the documentation
    - Check your hardware/filtering chain: AC coupling or high-pass filter capacitor charging can cause baseline inversions after reaching equilibrium.
- Channel 4 is reading a miniscule signal no matter what, and I cannot find any hardware issues, so why? 
    -/ check breathing mode criteria, could find none 

    
## To-Do 7/24
- ex_dys_fpl_csv_filtered.py adds 
    -/convert ADC values to channel units
        VREF = Reference voltage (usually 2.42 V for ADS1299, check your device spec!)
        GAIN = ADC PGA gain (often 24 for EMG)
        2**23 = Max 24-bit signed integer range
        - ch 1 is in ohms for bioimpedance
    -/highpass and bandpass filters
    -/rectify each signal 
    -/switch to low power mode/low resolution mode 
- verify BI injected current amplitude, 
    -/ found nothing in documentation
    - However, typical bioimpedance systems at the I24’s scale often use an AC injection current between 50 µA and 100 µA, especially when aiming to measure muscle or tissue 
    impedance with minimal discomfort and high safety. For example, many similar systems use programmable currents in that range for 50–333 kHz measurements
-/ how do ex_dys_fpl_csv.py and dyscom_runlive1.py output different values into the CSV
    -ex; low power, 500 sps
    -dys; high res, 4k sps. 
    raw_value: .value from the packet
- With ex_dys_fpl_csv.py, after 1000 samples, channel 1's signal flips from negative to positive, why? 
    -/ check toggle bias injection / automatic switching, found nothing in the documentation
    - Check your hardware/filtering chain: AC coupling or high-pass filter capacitor charging can cause baseline inversions after reaching equilibrium.
- Channel 4 is reading a miniscule signal no matter what, and I cannot find any hardware issues, so why? 
    -/ check breathing mode criteria, could find none 

## to do 7/23
-dive into ADS129x chip register codes
- how are the initialization parameters applied to the device
- channel colors, mostly confirmed by tapping on electrodes
    1 - red, ALWAYS bioimpedance channel
    2 - green, EMG_1
    3 - black, EMG_2
    4 - yellow, 3rd EMG, wierd signal

## to do 7/22
-/ get good EMG recording by itself, start with the given code and manipulate from there
- sampling rate
-/ gain settings
- find out what a sound card is
-/ convert raw ADC counts to microvolts
-kinda convert channel 1 to ohms
-------------------
- dyscom_runlive5.py
added convert raw ADC counts to microvolts
set gain to 12
fixed baud rate in COM port settings?

try next 
lowest possible sampling rate 
match up packet speed with save to csv speed 

started pure with example_dyscom_fastplotlib -> ex_dys_fpl_csv.py
    rename smpt_software_copy or something
why channel 1 voltage sign flip at 1k samples?
detects movement on channels 2 + 3
still virtually nothing on channel 4 
what's diferent from dyscom_runlive ? 
csv 8
csv 9 - point/flex, tapped 2-4
plot and decipher from there

## To-Do updated 7/21
- why are EMG recordings bad
## to try 7/22
- get good EMG recording by itself, start with the given code and manipulate from there
-sampling rate
- gain settings
- find out what a sound card is
Reasons for Flat EMG Recordings 
-x improper electrode placement or poor contact between the electrodes and the skin, which can result in inadequate signal pickup  Another reason could be a 
-malfunction or failure in the recording equipment, such as a faulty amplifier or sound card, which may not properly amplify or capture the EMG signals   
-x muscles being recorded are not actively contracting or if the subject is not performing the required movements, the EMG signals may appear flat 
-the gain settings of the amplifier are too low, leading to a lack of signal amplification  Finally, 
- sm4.dyscom.ads129x.ads129x_config1
-issues with the software used for data acquisition or analysis could also contribute to flat EMG recordings

## To-Do updated 7/18
-/ check fastplotlibhelper; added to ccfes-functions
-X and csvhelper functions, possiblt rewrite for new configs; didnt need to, fixed
-/ create a fastplotlib plot function for the stim parameters
-/ in ccfes-functions create a fastplot lib helper that takes 2 EMG channels and 2 FES channels and graphs them live
-/ delete / fix DyscomSignalType and change this code to 2 channels not 4
--------
- lowered the sampling rate 

## To-Do 7/17
- check fastplotlibhelper 
- and csvhelper functions, possiblt rewrite for new configs
- create a fastplotlib plot function for the stim parameters
- in ccfes-functions create a fastplot lib helper that takes 2 EMG channels and 2 FES channels and graphs them live
- delete / fix DyscomSignalType and change this code to 2 channels not 4

# 7/14
combine and rewrite dyscom_runlive3.py and midlevel_runlive2.py into a single code that runs the I24 measurement device and the P24 stimulator device with live controls, starting at the same time. Assume the I24 is connectet to COM3 and the P24 is connected to COM4 on the computer. Leave notes and comments throughout the code explaining what every line and input does to a non-programmer that will be using the code as an interface to control the devices.

# 7/11 
example_mid_level.py and run2live4.py are fromdifferent python libraries used to control the hasomed P24 stimulator.
write a code to control the P24 that works with the commands from the example_mid_level.py library to create a code that does everything that run2live4.py does.
leave notes throughout the code explaining what each line does to a non-programmer