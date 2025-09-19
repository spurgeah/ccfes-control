## to do 7/23
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
why channel 1 voltage sign flip at 1k samples?
detects movement on channels 2 + 3
still virtually nothing on channel 4 
what's diferent from dyscom_runlive ? 
csv 8
csv 9 - point/flex, tapped 2-4
plot and decipher from there



## Upon startup
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass 
conda activate i24setup2 
cd ccfes-setup 
cd ccfes-setup-7-19
$env:PYTHONPATH="Y:\Hasomed Code\HasomedSetup13\ScienceMode4Python"

cd ..
cd ..
cd examples
cd dyscom

# if 'no module named examples'
$env:PYTHONPATH="Y:\Hasomed Code\HasomedSetup13\ScienceMode4Python"

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

## Introduction

## Alisa's computer COM ports
1 - 
2 - 
3 - USB-A, bottom left
4 - USB-C, bottom right

## I24 device information
- 3 channels for measurement and 1 for impedance measurement
ch1 ALWAYS RED has to be bio impedance? YES
green - emg & BI
red - output for BI
white - common more rejection
black - emg
yellow - emg 

surface emg sampling rate - 1k - 2k Hz 

channel_settings_register - gain, 
config_register_1 - power mode, output data rate, 
config_register_3 - referance voltage
config_register_4 - 
dyscom_types - signal type, get info, power module type


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


I have the hasomed I24 measurement device, and am controlling it with this python repository; https://github.com/nextroundwinner/ScienceMode4Python
in the initialization parameters, How can I tell which channel (each has different chord colors on the machine) is taking which measurement when I look at the 
live data? What units are the output values in? The documentation says that there is one impedance channel and 3 measurement channels. How can I assign or discern which is which? 
even with all 4 channels hooked up, I keep geeting a miniscule reading on channel 4. What might be wrong with it?

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