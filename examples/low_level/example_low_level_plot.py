"""Provides an example how to use low level layer to measure current and plot values"""

import asyncio
import sys

import matplotlib.pyplot as plt
import numpy as np

from science_mode_4 import DeviceP24
from science_mode_4 import ChannelPoint, Commands
from science_mode_4 import SerialPortConnection
from science_mode_4 import PacketLowLevelChannelConfigAck
from science_mode_4 import Connector, Channel
from science_mode_4 import LowLevelHighVoltageSource, LowLevelMode
from examples.utils.example_utils import ExampleUtils


async def main() -> int:
    """Main function"""

    # get comport from command line argument
    com_port = ExampleUtils.get_comport_from_commandline_argument()
    # create serial port connection
    connection = SerialPortConnection(com_port)
    # open connection, now we can read and write data
    connection.open()

    # create science mode device
    device = DeviceP24(connection)
    # call initialize to get basic information (serial, versions) and stop any active stimulation/measurement
    # to have a defined state
    await device.initialize()

    # get low level layer to call low level commands
    low_level_layer = device.get_layer_low_level()

    # call init low level and enable measurement
    await low_level_layer.init(LowLevelMode.STIM_CURRENT, LowLevelHighVoltageSource.STANDARD)

    # send one channel config so we get only one acknowledge
    low_level_layer.send_channel_config(True, Channel.RED, Connector.GREEN,
                                        [ChannelPoint(1000, 40), ChannelPoint(1000, 0),
                                        ChannelPoint(1000, -20)])

    # wait for stimulation to happen
    await asyncio.sleep(0.1)

    measurement_sample_time = 0
    measurement_samples: list[float] = []
    # get new data from connection
    ack = low_level_layer.packet_buffer.get_packet_from_buffer()
    if ack:
        if ack.command == Commands.LOW_LEVEL_CHANNEL_CONFIG_ACK:
            ll_config_ack: PacketLowLevelChannelConfigAck = ack
            measurement_sample_time = ll_config_ack.sampling_time_in_microseconds
            measurement_samples.extend(ll_config_ack.measurement_samples)

    # call stop low level
    await low_level_layer.stop()

    # close serial port connection
    connection.close()

    # show plot
    _, ax = plt.subplots()
    # use measurement_sample_time as time frame for x-axis
    # this may be wrong because measurement_sample_time seems to long and
    # does not match actual stimulation duration
    ax.plot(np.linspace(0, measurement_sample_time, len(measurement_samples)),
            measurement_samples)

    ax.set(xlabel="Sample Time (µs)", ylabel="Current (mA)",
        title="Current measurement")
    ax.grid()

    plt.show()

    return 0


if __name__ == "__main__":
    res = asyncio.run(main())
    sys.exit(res)
