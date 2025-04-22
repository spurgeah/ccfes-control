"""Test program how to use library without installing the library,
DO NOT USE THIS FILE, USE EXAMPLES INSTEAD"""

import logging
import sys
import asyncio

from science_mode_4.device_i24 import DeviceI24
from science_mode_4.device_p24 import DeviceP24
from science_mode_4.utils import logger
from science_mode_4.utils.serial_port_connection import SerialPortConnection
from science_mode_4.utils.usb_connection import UsbConnection



async def main() -> int:
    """Main function"""

    # Serial
    # 2025-04-22 15:38 - DEBUG - Outgoing data, length: 12, bytes: F0 81 55 81 59 81 4E 81 0C 04 3E 0F
    # 2025-04-22 15:38 - DEBUG - Incoming data, length: 13, bytes: F0 81 55 81 58 81 D1 81 0A 04 43 00 0F
    # USB
    # 2025-04-22 15:45 - DEBUG - Outgoing data, length: 12, bytes: F0 81 55 81 59 81 4E 81 0C 04 3E 0F
    # 2025-04-22 15:45 - DEBUG - Incoming data, length: 13, bytes: F0 81 55 81 58 81 D1 81 0A 04 43 00 0F
    logger().setLevel(logging.DEBUG)
    # devices = SerialPortConnection.list_science_mode_device_ports()
    # connection = SerialPortConnection(devices[0].device)
    devices = UsbConnection.list_science_mode_devices()
    connection = UsbConnection(devices[0])
    # connection = NullConnection()
    connection.open()

    device = DeviceI24(connection)
    await device.initialize()
    general = device.get_layer_general()
    print(f"Device id: {general.device_id}")
    print(f"Firmware version: {general.firmware_version}")
    print(f"Science mode version: {general.science_mode_version}")

    connection.close()

    return 0


if __name__ == "__main__":
    res = asyncio.run(main())
    sys.exit(res)
