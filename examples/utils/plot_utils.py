"""Provides a buffer class to plot values"""

import collections
import matplotlib.pyplot as plt


class PlotValueChannel:
    """Class for holding a specific number of values and handling minimum/maximum"""


    def __init__(self, axes: plt.Axes, color: str, max_value_count: int = 100):

        self._x_data = []
        self._y_data = []

        # add line with color
        line, = axes.plot(self._x_data, self._y_data, color)
        # enable grid
        axes.grid()

        self._axes = axes
        self._line = line

        self._max_value_count = max_value_count
        self._counter = 0
        self._minimum = None
        self._maximum = None

        # self._line.set_xdata(self._x_data)
        # self._line.set_ydata(self._y_data)



    def append_value(self, value: float):
        """Appends a value and returns updated minimum and maximum for plot"""
        self._x_data.append(self._counter)
        self._counter += 1
        if len(self._x_data) > self._max_value_count:
            self._x_data.pop(0)

        self._y_data.append(value)
        if len(self._y_data) > self._max_value_count:
            self._y_data.pop(0)

        self._line.set_xdata(self._x_data)
        self._line.set_ydata(self._y_data)

        if self._minimum is None or value < self._minimum:
            self._minimum = value
        if self._maximum is None or value > self._maximum:
            self._maximum = value

        if len(self._x_data) > 1:
            self._axes.set_xlim(self._x_data[0], self._x_data[-1])
            offset = (self._maximum - self._minimum) * 0.1
            self._axes.set_ylim(bottom=self._minimum - offset, top=self._maximum + offset)

        self._axes.redraw_in_frame()


class PlotHelper:
    """Class to handle values for plotting"""


    def __init__(self, channels: dict[int, tuple[str, str]], x_value_count: int = 100):
        self._data: dict[int, PlotValueChannel] = {}
        self._figure, self._axes = plt.subplots(len(channels), 1, constrained_layout=True)

        axes_count = 0

        for key, value in channels.items():
            ax = self._axes[axes_count]
            axes_count += 1

            ax.set(xlabel="Samples", ylabel=value[0], title=value[0])
            self._data[key] = PlotValueChannel(ax, value[1], x_value_count)

        self.interactive_mode(True)
        plt.show()


    def append_value(self, channel: int, value: float) -> tuple[float, float]:
        self._data[channel].append_value(value)


    def update(self):
        # self._figure.canvas.draw()
        # self._figure.canvas.flush_events()
        pass


    def interactive_mode(self, enabled: bool):
        if enabled:
            plt.ion()
        else:
            plt.ioff()
