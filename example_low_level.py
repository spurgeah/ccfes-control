"""Provides an example how to use low level layer"""

import asyncio
import sys
import threading
from typing import Callable

from src.device_p24 import DeviceP24
from src.low_level.low_level_layer import LayerLowLevel
from src.types.channel_point import ChannelPoint
from src.types.types import Channel, Connector
from src.utils.null_connection import NullConnection

class KeyboardInputThread(threading.Thread):
    """Thread for non blocking keyboard input"""

    def __init__(self, input_cbk: Callable[[str], bool]):
        self._input_cbk = input_cbk
        super().__init__(name = "keyboard_input_thread", daemon = True)
        self.start()


    def run(self):
        while True:
            if self._input_cbk(input()):
                break


def send_channel_config(low_level_layer: LayerLowLevel, connector: Connector):
    """Sends channel update"""
    for channel in Channel:
        low_level_layer.send_channel_config(True, channel, connector,
                                            [ChannelPoint(4000, 20), ChannelPoint(4000, -20),
                                            ChannelPoint(4000, 0)])


async def main() -> int:
    """Main function"""

    # connection = SerialPortConnection('COM3')
    connection = NullConnection()
    connection.open()

    device = DeviceP24(connection)
    await device.initialize()

    low_level_layer = device.get_layer_low_level()

    def input_callback(input_value: str) -> bool:
        # this function runs in keyboard input thread scope
        print(f"Input value {input_value}")

        if input_value == "1":
            send_channel_config(low_level_layer, Connector.GREEN)
        elif input_value == "2":
            send_channel_config(low_level_layer, Connector.YELLOW)
        elif input_value == "q":
            # end keyboard input thread
            return True

        return False


    keyboard_input_thread = KeyboardInputThread(input_callback)

    await low_level_layer.init()
    
    while keyboard_input_thread.is_alive:
        # get new data from connection
        # both append_bytes_to_buffer and get_packet_from_buffer should be called regulary
        new_buffer_data = device.connection.read()
        if len(new_buffer_data) > 0:
            low_level_layer.packet_buffer.append_bytes_to_buffer(new_buffer_data)
            # we added new data to buffer, so there may be new valid acknowledges
            packet_ack = low_level_layer.packet_buffer.get_packet_from_buffer()
            # do something with packet ack
            print(packet_ack)

    await low_level_layer.stop()

    connection.close()
    return 0


if __name__ == '__main__':
    res = asyncio.run(main())
    sys.exit(res)
