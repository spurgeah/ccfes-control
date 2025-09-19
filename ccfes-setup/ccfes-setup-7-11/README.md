## To-Do updated 7/11
- check that mid_runlive.py works with P24
- start combining dyscom_runlive2 and mid_runlive according to the structure of the ghost codedeactivate 

## Upon startup
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass 
conda activate i24setup2 
cd ccfes-setup 
cd ccfes-setup-7-17
$env:PYTHONPATH="Y:\Hasomed Code\HasomedSetup13\ScienceMode4Python"

# if 'no module named examples'
$env:PYTHONPATH="Y:\Hasomed Code\HasomedSetup13\ScienceMode4Python"
python mid_runlive.py

## CCFES Python Library folder setup 
- csv_files folder - where all the csv files are saved to
- dyscom_runlive2.py - Alisa's version of ScienceMode4Python dyscom files to run data collection from the I24 live, then save to a CSV file 

- mid_runlive.py - scienceMode4Python version of pyScienceMode P24 runlive code (2 channels)
    - 2 - changes plotting functions to fastplotlib.utils functions

- ccfes_runlive.py -

## Introduction

## Alisa's computer COM ports
1 - 
2 - 
3 - 
4 - USB-C, bottom right