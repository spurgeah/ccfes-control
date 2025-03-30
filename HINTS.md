# Introduction
This site discribes implementation hints.

# Deviation from Instruction for Use

## Dyscom commands

### Common
- Most strings are 1 byte less long (null termination is not an extra byte)

### DL_get_ack for type file by name
- Addition parameter mode (1 byte)
  - Undefined = 0
  - Multiblock = 1
  - Singleblock = 2