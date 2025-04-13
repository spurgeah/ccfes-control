"""Test program how to use library without installing the library,
DO NOT USE THIS FILE, USE EXAMPLES INSTEAD"""

from imaplib import Commands
import sys
import asyncio

import matplotlib.pyplot as plt
import numpy as np

from src.science_mode_4 import LayerDyscom, LayerLowLevel, LayerMidLevel,\
    Commands, Connector, Channel, ChannelPoint,\
    SerialPortConnection,\
    DeviceI24,\
    Ads129xOutputDataRate, Ads129xPowerMode,\
    PacketDyscomGetAckOperationMode, PacketDyscomSendLiveData,\
    DyscomInitParams, DyscomPowerModulePowerType, DyscomPowerModuleType, DyscomSignalType



# print(science_mode_4.__version__)

def send_channel_config(low_level_layer: LayerLowLevel, connector: Connector):
    """Sends channel update"""
    # device can store up to 10 channel config commands
    for channel in Channel:
        # send_channel_config does not wait for an acknowledge
        low_level_layer.send_channel_config(True, channel, connector,
                                            [ChannelPoint(4000, 20), ChannelPoint(4000, -20),
                                            ChannelPoint(4000, 0)])

async def main() -> int:
    """Main function"""

    connection = SerialPortConnection("COM6")
    # devices = UsbConnection.list_science_mode_devices()
    # connection = UsbConnection(devices[0])
    # connection = NullConnection()
    connection.open()

    device = DeviceI24(connection)
    await device.initialize()
    # general = device.get_layer_general()
    # print(f"device id: {general.device_id}")
    # print(f"firmware version: {general.firmware_version}")
    # print(f"science mode version: {general.science_mode_version}")

    dyscom: LayerDyscom = device.get_layer_dyscom()
    # fss: DyscomGetFileSystemStatusResult = await dyscom.get_file_system_status()
    # print(f"Ready {fss.file_system_ready}, used size {fss.used_size}, free size {fss.free_size}")
    # fbn: DyscomGetFileByNameResult = await dyscom.get_file_by_name()
    # print(f"Filename {fbn.filename}, block offset {fbn.block_offset}, filesize {fbn.filesize}, nr of blocks {fbn.number_of_blocks}")
    # fv: str = await dyscom.get_firmware_version()
    # print(f"Firmware version {fv}")
    # nrof = await dyscom.get_list_of_measurement_meta_info()
    # print(f"Number of measurement meta info {nrof}")
    # did = await dyscom.get_device_id()
    # print(f"Device ID {did}")
    # fi = await dyscom.get_file_info()
    # print(f"File info {fi.filename} {fi.filesize} {fi.checksum}")
    # b = await dyscom.get_battery()
    # print(f"Battery {b.voltage} {b.current} {b.percentage} {b.temperature} {b.energy_state}")

    # sys_ack: DyscomSysResult = await dyscom.sys(DyscomSysType.DEVICE_STORAGE)
    # print(f"Sys {sys_ack.sys_type} {sys_ack.state} {sys_ack.filename}")

    await dyscom.power_module(DyscomPowerModuleType.MEASUREMENT, DyscomPowerModulePowerType.SWITCH_ON)
    init_params = DyscomInitParams()
    init_params.register_map_ads129x.config_register_1.output_data_rate = Ads129xOutputDataRate.HR_MODE_500_SPS__LP_MODE_250_SPS
    init_params.register_map_ads129x.config_register_1.power_mode = Ads129xPowerMode.LOW_POWER
    await dyscom.init(init_params)

    fig, ax = plt.subplots()
    ax.set(xlabel="Sample Time (µs)", ylabel="Current (mA)",
        title="Current measurement")
    ax.grid()
    plt.ion()
    plt.show()

    def update_ylim(data: list[float]):
        if len(data) == 0:
            return

        new_min = data[0]
        new_max = data[0]
        for x in data:
            if x < new_min:
                new_min = x
            if x > new_max:
                new_max = x

        offset = (new_max - new_min) * 0.1
        plt.ylim(new_min - offset, new_max + offset)

    plot_buffer: list[float] = []
    plot_data, = ax.plot(np.linspace(0, 100, len(plot_buffer)), plot_buffer)
    update_ylim(plot_buffer)
    used_signals: set[DyscomSignalType] = set()
    await dyscom.start()

    for x in range(1000):
        if x % 100 == 0:
            dyscom.send_get_operation_mode()

        while True:
            ack = dyscom.packet_buffer.get_packet_from_buffer()
            if ack:
                if ack.command == Commands.DlGetAck:
                    om_ack: PacketDyscomGetAckOperationMode = ack
                    print(f"Operation mode {om_ack.operation_mode}")
                elif ack.command == Commands.DlSendLiveData:
                    sld: PacketDyscomSendLiveData = ack
                    if sld.status_error:
                        print(f"SendLiveData status error {sld.samples}")
                        break
                    if sld.number % 50 == 0:
                        # print(f"Append {sld.value} {sld.signal_type}")
                        for s in sld.samples:
                            used_signals.add(s.signal_type)
                        if len(plot_buffer) > 250:
                            plot_buffer.pop(0)
                        plot_buffer.append(sld.time_offset) # samples[1].value
                        plot_data.remove()
                        plot_data, = ax.plot(np.linspace(0, len(plot_buffer), len(plot_buffer)), plot_buffer, color = "b")
                        # plot_data.set_xdata(np.linspace(0, 100, len(plot_buffer)))
                        # plot_data.set_ydata(plot_buffer)
                        # update_ylim(plot_buffer)
                        fig.canvas.draw()
                        fig.canvas.flush_events()

            else:
                break

        await asyncio.sleep(0.01)

    # wait until all acknowledges are received
    await asyncio.sleep(0.5)

    await dyscom.stop()
    await dyscom.power_module(DyscomPowerModuleType.MEASUREMENT, DyscomPowerModulePowerType.SWITCH_OFF)

    print(used_signals)
    # c1p1: ChannelPoint = ChannelPoint(200, 20)
    # c1p2: ChannelPoint = ChannelPoint(100, 0)
    # c1p3: ChannelPoint = ChannelPoint(200, -20)
    # cc1 = MidLevelChannelConfiguration(True, 3, 20, [c1p1, c1p2, c1p3])

    # c2p1: ChannelPoint = ChannelPoint(100, 100)
    # c2p2: ChannelPoint = ChannelPoint(100, 0)
    # c2p3: ChannelPoint = ChannelPoint(100, -100)
    # cc2 = MidLevelChannelConfiguration(True, 3, 10, [c2p1, c2p2, c2p3])

    # mid_level = device.get_layer_mid_level()
    # await mid_level.init(False)
    # await mid_level.update([cc1, cc2])
    # for _ in range(100):
    #     update = await mid_level.get_current_data()
    #     print(update)

    #     await asyncio.sleep(1)

    # await mid_level.stop()

    # # get low level layer to call low level commands
    # low_level_layer = device.get_layer_low_level()

    # # call init low level
    # await low_level_layer.init(LowLevelMode.STIM_CURRENT, LowLevelHighVoltageSource.STANDARD)

    # # now we can start stimulation
    # counter = 0
    # ms: list[float] = []
    # sample_time = 0
    # while counter < 10:
    #     # get new data from connection
    #     # both append_bytes_to_buffer and get_packet_from_buffer should be called regulary
    #     new_buffer_data = device.connection.read()
    #     if len(new_buffer_data) > 0:
    #         low_level_layer.packet_buffer.append_bytes_to_buffer(new_buffer_data)
    #         # we added new data to buffer, so there may be new valid acknowledges
    #         packet_ack = low_level_layer.packet_buffer.get_packet_from_buffer()
    #         # do something with packet ack
    #         # here we print that an acknowledge arrived
    #         # print(f"I {packet_ack}")
    #         if packet_ack.command == Commands.LowLevelChannelConfigAck:
    #             ll_config_ack: PacketLowLevelChannelConfigAck = packet_ack
    #             ms.extend(ll_config_ack.measurement_samples)
    #             sample_time = ll_config_ack.sampling_time_in_microseconds
    #             print(f"sample time {ll_config_ack.sampling_time_in_microseconds}")
    #             print(ms)

    #     # if counter % 10 == 0:
    #     #     send_channel_config(low_level_layer, Connector.GREEN)
    #     # elif counter % 10 == 5:
    #     #     send_channel_config(low_level_layer, Connector.YELLOW)

    #     if counter % 10 == 0:
    #         low_level_layer.send_channel_config(True, Channel.RED, Connector.GREEN,
    #                                             [ChannelPoint(2000, 40), ChannelPoint(1000, 0),
    #                                             ChannelPoint(1000, -20)])
    #     await asyncio.sleep(0.01)
    #     counter += 1

    # # wait until all acknowledges are received
    # await asyncio.sleep(0.5)
    # # call stop low level
    # await low_level_layer.stop()

    connection.close()

    return 0


if __name__ == "__main__":
    res = asyncio.run(main())
    sys.exit(res)
