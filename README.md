# ScienceMode4 Python

## Introduction

Python implementation of ScienceMode 4 protocol (https://github.com/ScienceMode/ScienceMode4_P24)

## Requirements

Python 3.11 or higher

## Installation

- Install science-mode-4 library inclusive dependencies via pip
  - `pip install science-mode-4`
  - https://pypi.org/project/science-mode-4/

## Dependencies

- PySerial
  - https://pypi.org/project/pyserial/
  - `pip install pyserial`
- Keyboard (only for examples)
  - https://pypi.org/project/keyboard/
  - `pip install keyboard`

## Build library

- Install dependencies
  - `python -m pip install --upgrade build`
- Build project
  - `python -m build`
- Install local library
  - `pip install .\dist\science_mode_4-0.0.1-py3-none-any.whl` (adjust path accordingly)
