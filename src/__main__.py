"""Test program how to use library without installing the library,
DO NOT USE THIS FILE, USE EXAMPLES INSTEAD"""

import sys
import asyncio

from science_mode_4 import DeviceP24
from science_mode_4.low_level.low_level_channel_config import PacketLowLevelChannelConfigAck
from science_mode_4.protocol import ChannelPoint
from science_mode_4.protocol.commands import Commands
from science_mode_4.utils import SerialPortConnection
from science_mode_4.low_level import LayerLowLevel
from science_mode_4.protocol import Connector, Channel
from science_mode_4.low_level import LowLevelHighVoltageSource, LowLevelMode


async def main() -> int:
    """Main function"""

    # logger().setLevel(logging.DEBUG)
    current = 70

    # # keyboard is our trigger to start specific stimulation
    # def input_callback(input_value: str) -> bool:
    #     """Callback call from keyboard input thread"""
    #     print(f"Input value {input_value}")

    #     nonlocal current
    #     if input_value == "1":
    #         send_channel_config(low_level_layer, Connector.GREEN)
    #     elif input_value == "2":
    #         send_channel_config(low_level_layer, Connector.YELLOW)
    #     elif input_value == "+":
    #         current += 0.5
    #         print(f"current: {current}")
    #     elif input_value == "-":
    #         current -= 0.5
    #         print(f"current: {current}")
    #     elif input_value == "q":
    #         # end keyboard input thread
    #         return True
    #     else:
    #         print("Invalid command")

    #     return False


    def send_channel_config(low_level_layer: LayerLowLevel, connector: Connector):
        """Sends channel update"""
        # device can store up to 10 channel config commands
        for channel in Channel:
            # send_channel_config does not wait for an acknowledge
            low_level_layer.send_channel_config(True, channel, connector,
                                                [ChannelPoint(1000, current), ChannelPoint(4000, 0),
                                                ChannelPoint(1000, -current)])


    print("Usage:")
    print("Press 1 or 2 to stimulate green or yellow connector")
    print("Press + or - to increase or decrease current")
    print("Press q to quit")
    # create keyboard input thread for non blocking console input
    # keyboard_input_thread = KeyboardInputThread(input_callback)

    # get comport from command line argument
    # com_port = ExampleUtils.get_comport_from_commandline_argument()
    # create serial port connection
    connection = SerialPortConnection(SerialPortConnection.list_science_mode_device_ports()[0].device)
    # open connection, now we can read and write data
    connection.open()

    # create science mode device
    device = DeviceP24(connection)
    # call initialize to get basic information (serial, versions) and stop any active stimulation/measurement
    # to have a defined state
    await device.initialize()

    # get low level layer to call low level commands
    low_level_layer = device.get_layer_low_level()

    # call init low level
    await low_level_layer.init(LowLevelMode.NO_MEASUREMENT, LowLevelHighVoltageSource.STANDARD)

    # now we can start stimulation
    # while keyboard_input_thread.is_alive():
    for x in range(500):
        if x % 100 == 0:
            send_channel_config(low_level_layer, Connector.YELLOW)
        # get new packets from connection
        ack = low_level_layer.packet_buffer.get_packet_from_buffer()
        if ack and ack.command == Commands.LOW_LEVEL_CHANNEL_CONFIG_ACK:
            cca: PacketLowLevelChannelConfigAck = ack
            # do something with packet ack
            # here we print that an acknowledge arrived
            print(cca.result.name)

        await asyncio.sleep(0.1)

    # wait until all acknowledges are received
    await asyncio.sleep(0.5)
    # call stop low level
    await low_level_layer.stop()

    # close serial port connection
    connection.close()
    return 0


if __name__ == "__main__":
    res = asyncio.run(main())
    sys.exit(res)
