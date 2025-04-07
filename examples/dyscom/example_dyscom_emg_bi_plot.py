# """Provides an example how to use dyscom level layer to measure emg and bi and plot values"""

import asyncio
import sys

# from example_utils import ExampleUtils
# from fast_plot_utils import PlotHelper

# from science_mode_4 import DeviceI24
# from science_mode_4 import Commands
# from science_mode_4 import SerialPortConnection
# from science_mode_4.dyscom.ads129x.ads129x_config_register_1 import Ads129xOutputDataRate, Ads129xPowerMode
# from science_mode_4.dyscom.dyscom_get_operation_mode import PacketDyscomGetAckOperationMode
# from science_mode_4.dyscom.dyscom_send_live_data import PacketDyscomSendLiveData
# from science_mode_4.dyscom.dyscom_types import DyscomInitParams, DyscomPowerModulePowerType, DyscomPowerModuleType


# async def main() -> int:
#     """Main function"""

#     # get comport from command line argument
#     com_port = ExampleUtils.get_comport_from_commandline_argument()
#     # create serial port connection
#     connection = SerialPortConnection(com_port)
#     # open connection, now we can read and write data
#     connection.open()

#     # create science mode device
#     device = DeviceI24(connection)
#     # call initialize to get basic information (serial, versions) and stop any active stimulation/measurement
#     # to have a defined state
#     await device.initialize()

#     # get dyscom layer to call low level commands
#     dyscom = device.get_layer_dyscom()

#     # call enable measurement power module for measurement
#     await dyscom.power_module(DyscomPowerModuleType.MEASUREMENT, DyscomPowerModulePowerType.SWITCH_ON)
#     # call init with lowest sample rate (because of performance issues with plotting values)
#     init_params = DyscomInitParams()
#     init_params.register_map_ads129x.config_register_1.output_data_rate = Ads129xOutputDataRate.HR_MODE_500_SPS__LP_MODE_250_SPS
#     init_params.register_map_ads129x.config_register_1.power_mode = Ads129xPowerMode.LOW_POWER
#     await dyscom.init(init_params)


# # # Turn on interactive mode
# # plt.ion()

# # x = []
# # y = []

# # fig, ax = plt.subplots()
# # line, = ax.plot([], [], 'b-')  # Initialize an empty line

# # # Loop to update the plot
# # for i in np.arange(0, 10, 0.1):
# #     x.append(i)
# #     y.append(np.sin(i))
    
# #     # Update the line data
# #     line.set_xdata(x)
# #     line.set_ydata(y)
    
# #     # Adjust axis limits dynamically
# #     ax.relim()
# #     ax.autoscale_view()
    
# #     plt.draw()  # Redraw the plot
# #     plt.pause(0.1)  # Pause to simulate real-time updates

# # plt.ioff()  # Turn off interactive mode
# # plt.show()

#     # BI: 10
#     # EMG: -0,07
#     # EMG2: -0,7
#     # EMG3: -0,22
#     # ph = PlotHelper({0: ["BI", "blue"], 1: ["EMG", "red"]})
#     ph = PlotHelper({0: ["BI", "blue"]})

#     # start dyscom measurement
#     await dyscom.start()

#     for x in range(1000):
#         # check operation mode from time to time
#         if x % 100 == 0:
#             dyscom.send_get_operation_mode()

#         while True:
#             ack = dyscom.packet_buffer.get_packet_from_buffer()
#             if ack:
#                 if ack.command == Commands.DlGetAck:
#                     om_ack: PacketDyscomGetAckOperationMode = ack
#                     print(f"Operation mode {om_ack.operation_mode}")
#                 elif ack.command == Commands.DlSendLiveData:
#                     sld: PacketDyscomSendLiveData = ack
#                     if sld.status_error:
#                         print(f"SendLiveData status error {sld.samples}")
#                         break
#                     if sld.number % 10 == 0:
#                         # print(f"Append {sld.value} {sld.signal_type}")
#                         ph.append_value(0, sld.samples[0].value)
#                         # ph.append_value(1, sld.samples[1].value)
#                         # for s in sld.samples:
#                         #     ph.append_value(int(s.signal_type), s.value)

#                         ph.update()
#             else:
#                 break

#         await asyncio.sleep(0.01)

#     # wait until all acknowledges are received
#     await asyncio.sleep(0.5)

#     # stop measurement
#     await dyscom.stop()
#     # turn power module off
#     await dyscom.power_module(DyscomPowerModuleType.MEASUREMENT, DyscomPowerModulePowerType.SWITCH_OFF)

#     # close serial port connection
#     connection.close()

#     return 0


# if __name__ == "__main__":
#     res = asyncio.run(main())
#     sys.exit(res)


import fastplotlib as fpl
import numpy as np
import glfw
import OpenGL.GL as gl

# Initialisiere GLFW
# if not glfw.init():
#     raise Exception("GLFW konnte nicht initialisiert werden")

# # Erstelle ein Fenster
# width, height = 600, 400
# window = glfw.create_window(width, height, "fastplotlib mit GLFW", None, None)
# if not window:
#     glfw.terminate()
#     raise Exception("GLFW-Fenster konnte nicht erstellt werden")

# glfw.make_context_current(window)
# glfw.swap_interval(1)  # Aktiviere VSync

# generate some data
start, stop = 0, 2 * np.pi
increment = (2 * np.pi) / 50

# make a simple sine wave
xs = np.linspace(start, stop, 100)
ys = np.sin(xs)

# canvas = glfw.GlfwRenderCanvas()
figure = fpl.Figure() # size=(700, 560), canvas="glfw"


# plot the image data
sine = figure[0, 0].add_line(ys, name="sine", colors="r")


# increment along the x-axis on each render loop :D
def update_line(subplot):
    global increment, start, stop
    xs = np.linspace(start + increment, stop + increment, 100)
    ys = np.sin(xs)

    start += increment
    stop += increment

    # change only the y-axis values of the line
    subplot["sine"].data[:, 1] = ys


figure[0, 0].add_animations(update_line)

figure.show(maintain_aspect=False)


# while True:
#     # Process custom tasks here
#     figure.renderer.flush()
#     figure.canvas.request_draw() 
#     glfw.poll_events()  # Handle GLFW events
#     # figure.canvas.force_draw() #  draw()  # Render frame

# async def task():
#     glfw.poll_events()
#     await asyncio.sleep(0.01)

# while True:
#     asyncio.run(task())


# fpl.loop.run()


while True: #not glfw.window_should_close(window):
    glfw.poll_events()

    # Zeichne die Szene
    canvas = figure.canvas
    w = canvas.__dict__["_window"]
    glfw.make_context_current(w)
    gl.glClearColor(0.2, 0.3, 0.3, 1.0)
    gl.glClear(gl.GL_COLOR_BUFFER_BIT)

    # Zeichne die fastplotlib-Figur
    figure.canvas.request_draw()

    glfw.swap_buffers(figure.canvas.get_context())

# Beende GLFW
glfw.terminate()



