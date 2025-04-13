# Introduction
This page describes implementation hints.

# Deviation from Instruction for Use

## Dyscom commands

### Common
- Strings are 1 byte less long (null termination is not an extra byte) in acknowledge packets
- Datetime parameters have a different order

### DL_get_ack for type file by name
- Addition parameter mode (1 byte)
  - Undefined = 0
  - Multiblock = 1
  - Singleblock = 2

### DL_get for type battery
- Dl get types (table 23)
  - 0 -> Battery (was Unused)

### DL_get_ack for type battery
- energy state, 1 byte, is a flag, bit 1: cable connected, bit 2: device is loading
- percentage, 1 byte, [0, 100] in percent
- temperature, 1 byte, [-128, 127] in degrees
- current, 4 bytes, [-327675, 327675] in milli ampere
- voltage, 4 bytes, [0, 65535] in milli volt

### DL_send_file_ack
- block number, 4 byte, block number of DL_send_file

### DL_send_live_data
- parameters are big endian?
- SignalType for each sample is always 0