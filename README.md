# ScienceMode4 Python

## Introduction

Python implementation of HasomedScience ScienceMode 4 protocol for P24 (https://github.com/ScienceMode/ScienceMode4_P24) and I24 (https://github.com/ScienceMode/ScienceMode4_I24) devices. To use this library see section [Installation](#installation).

## Requirements

Python 3.11 or higher

# Library

## Installation

- Install science_mode_4 library inclusive dependencies via pip
  - `pip install science_mode_4`
  - https://pypi.org/project/science-mode-4/

## Dependencies

- PySerial
  - https://pypi.org/project/pyserial/
  - `pip install pyserial`
- PyUSB
  - https://pypi.org/project/pyusb/
  - `pip install pyusb`
  - On Windows
    - Download libusb from https://libusb.info/
    - Copy libusb-XX.dll into venv root folder (besides python.exe)
    - Under Windows it there are driver issues

## Build library
- Only necessary, if you made changes to the library
- Install dependencies
  - `python -m pip install --upgrade build`
- Build project
  - `python -m build`
- Install local library
  - `pip install .\dist\science_mode_4-0.0.7-py3-none-any.whl` (adjust filename accordingly)

# Examples

## Description
- Located in folder `examples`
- Run examples with `python -m examples.<layer>.<example>`
  - Example: `python -m examples.dyscom.example_dyscom_fastplotlib`
- General layer
  - `example_general.py`
    - Demonstrates how to use general layer to initialize device and get serial number and firmware version
- Mid level layer
  - `example_mid_level.py`
    - Demonstrates how to use mid level layer, where a stimulation pattern is send to the stimulator and the device automatically executes the pattern by itself until stopped
- Low level layer
  - `example_low_level.py`
    - Demonstrates how to use low level layer, where host has to trigger stimulation manually, in this case by pressing a key 
  - `example_low_level_plot.py`
    - Demonstrates how to use low level layer to measure current and plot it in a graph using PyPlot
- Dyscom layer
  - `example_dyscom_get`
    - Demonstrate how to use different get commands from dyscom layer
  - `example_dyscom_fastplotlib`
    - Demonstrate how to use dyscom layer to measure EMG and BI and plotting values using fastplotlib
  - `example_dyscom_pyplot`
    - Demonstrate how to use dyscom layer to measure BI and plotting values using PyPlot
  - `example_dyscom_write_csv`
    - Demonstrate how to use dyscom layer to measure BI and EMG and writing measurement data to a .csv-file

## Dependencies for examples

- Keyboard
  - https://pypi.org/project/keyboard/
  - `pip install keyboard`
- NumPy
  - https://pypi.org/project/numpy/
  - `pip install numpy`
- Matplotlib / PyPlot
  - https://pypi.org/project/matplotlib/
  - `pip install matplotlib`
- Fastplotlib with glfw backend
  - `pip install -U fastplotlib`
  - `pip install -U glfw`

