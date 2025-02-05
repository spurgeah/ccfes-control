"""Provides an example how to use general layer"""

import sys
import asyncio

from example_utils import ExampleUtils
from .device_p24 import DeviceP24
from ScienceMode4_Python.utils.null_connection import NullConnection
from ScienceMode4_Python.utils.serial_port_connection import SerialPortConnection


async def main() -> int:
    """Main function"""

    # get comport from command line argument
    com_port = ExampleUtils.get_comport_from_commandline_argument()
    # create serial port connection
    connection = SerialPortConnection(com_port)
    connection = NullConnection()
    # open connection, now we can read and write data
    connection.open()

    # create science mode device
    device = DeviceP24(connection)
    # call initialize to get basic information (serial, versions) and stop any active stimulation/measurement
    # to have a defined state
    await device.initialize()

    # get general layer to call general commands
    general = device.get_layer_general()
    print(f"Device id: {general.device_id}")
    print(f"Firmware version: {general.firmware_version}")
    print(f"Science mode version: {general.science_mode_version}")

    # close serial port connection
    connection.close()
    return 0


if __name__ == '__main__':
    res = asyncio.run(main())
    sys.exit(res)
