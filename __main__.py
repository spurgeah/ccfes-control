"""Test program how to use library without installing the library,
DO NOT USE THIS FILE, USE EXAMPLES INSTEAD"""

import sys
import asyncio

from science_mode_4.device_p24 import DeviceP24
from science_mode_4.utils.serial_port_connection import SerialPortConnection



async def main() -> int:
    """Main function"""

    devices = SerialPortConnection.list_science_mode_device_ports()
    connection = SerialPortConnection(devices[0].device)
    # devices = UsbConnection.list_science_mode_devices()
    # connection = UsbConnection(devices[0])
    # connection = NullConnection()
    connection.open()

    device = DeviceP24(connection)
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
