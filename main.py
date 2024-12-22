import sys
import serial
import asyncio

from src.general.device_id import PacketGetDeviceId, PacketGetDeviceIdAck
from src.lowlevel.low_level_channel_config import LowLevelChannelPoint, PacketLowLevelChannelConfig, PacketLowLevelChannelConfigAck
from src.lowlevel.low_level_init import PacketLowLevelInit, PacketLowLevelInitAck
from src.lowlevel.low_level_stop import PacketLowLevelStop, PacketLowLevelStopAck
from src.packet_factory import PacketFactory
from src.packet import Packet
from src.protocol import Protocol
from src.utils.serial_port_connection import SerialPortConnection

async def main() -> int:

    factory = PacketFactory()

    p = PacketGetDeviceId()
    # p = PacketLowLevelInit()
    # p = PacketLowLevelChannelConfig()
    # p.executionStimulation = 1
    # p.channelSelection = 0
    # p.points = [LowLevelChannelPoint(250, 20), LowLevelChannelPoint(100, 0), LowLevelChannelPoint(250, -20)]
    # p = PacketLowLevelStop()

    connection = SerialPortConnection('COM3')
    connection.open()

    ack = await Protocol.sendPacket(p, 0, connection, factory)
    if ack:
        print(ack)

    connection.close()         
    
    return 0


if __name__ == '__main__':
    res = asyncio.run(main())
    sys.exit(res)