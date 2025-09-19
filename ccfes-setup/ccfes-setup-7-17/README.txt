## To-Do updated 7/18
-/ check fastplotlibhelper 
- and csvhelper functions, possiblt rewrite for new configs
- create a fastplotlib plot function for the stim parameters
- in ccfes-functions create a fastplot lib helper that takes 2 EMG channels and 2 FES channels and graphs them live
- delete / fix DyscomSignalType and change this code to 2 channels not 4


## Upon startup
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass 
conda activate i24setup2 
cd ccfes-setup 
cd ccfes-setup-7-18
$env:PYTHONPATH="Y:\Hasomed Code\HasomedSetup13\ScienceMode4Python"

# if 'no module named examples'
$env:PYTHONPATH="Y:\Hasomed Code\HasomedSetup13\ScienceMode4Python"

## CCFES Python Library folder setup 
- csv_files folder - where all the csv files are saved to
- dyscom_runlive2.py - Alisa's version of ScienceMode4Python dyscom files to run data collection from the I24 live, then save to a CSV file 
- midlevel_runlive.py - scienceMode4Python version of pyScienceMode P24 runlive code (2 channels)
    - 2 - changes plotting functions to fastplotlib.utils functions
- both_live.py - just runs P24 and I24 simultaneously, no talking to each other
- ccfes_runlive.py - P24 parameters are based on I24 measurement

## Introduction

## Alisa's computer COM ports
1 - 
2 - 
3 - 
4 - USB-C, bottom right

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