import sys
import asyncio

from src.device_p24 import DeviceP24
from src.utils.serial_port_connection import SerialPortConnection

async def main() -> int:

    # factory = PacketFactory()

    # p = PacketGetDeviceId()
    # p = PacketLowLevelInit()
    # p = PacketLowLevelChannelConfig()
    # p.executionStimulation = 1
    # p.channelSelection = 0
    # p.points = [LowLevelChannelPoint(250, 20), LowLevelChannelPoint(100, 0), LowLevelChannelPoint(250, -20)]
    # p = PacketLowLevelStop()

    connection = SerialPortConnection('COM3')
    connection.open()

    device = DeviceP24(connection)
    await device.initialize()
    general = device.getGeneralLayer()
    print(general.deviceId)
    print(general.firmwareVersion)
    print(general.scienceModeVersion)

    ss = await general.getStimStatus()

    connection.close()         
    
    return 0


if __name__ == '__main__':
    res = asyncio.run(main())
    sys.exit(res)