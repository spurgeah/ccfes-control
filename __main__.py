"""Simple example how to use library"""

import sys
import asyncio

from src.device_p24 import DeviceP24
from src.utils.channel_configuration import MidLevelChannelConfiguration
from src.utils.channel_point import ChannelPoint
from src.utils.null_connection import NullConnection
from src.utils.serial_port_connection import SerialPortConnection


async def main() -> int:
    """Main functions"""

    # connection = SerialPortConnection('COM3')
    connection = NullConnection()
    connection.open()

    device = DeviceP24(connection)
    await device.initialize()
    general = device.get_layer_general()
    print(general.device_id)
    print(general.firmware_version)
    print(general.science_mode_version)

    # ss = await general.getStimStatus()

    c1p1: ChannelPoint = ChannelPoint(200, 20)
    c1p2: ChannelPoint = ChannelPoint(100, 0)
    c1p3: ChannelPoint = ChannelPoint(200, -20)
    cc1: MidLevelChannelConfiguration = MidLevelChannelConfiguration(True, 3, 20, [c1p1, c1p2, c1p3])

    c2p1: ChannelPoint = ChannelPoint(100, 10)
    c2p2: ChannelPoint = ChannelPoint(100, 0)
    c2p3: ChannelPoint = ChannelPoint(100, -10)
    cc2: MidLevelChannelConfiguration = MidLevelChannelConfiguration(True, 3, 10, [c2p1, c2p2, c2p3])

    mid_level = device.get_layer_mid_level()
    await mid_level.init(True)
    await mid_level.update([cc1, cc2])
    for _ in range(10):
        update = await mid_level.getCurrentData()
        print(update)

        await asyncio.sleep(1)

    await mid_level.stop()

    connection.close()
    return 0


if __name__ == '__main__':
    res = asyncio.run(main())
    sys.exit(res)
