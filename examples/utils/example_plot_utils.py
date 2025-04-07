"""Provides a buffer class to plot values"""


class PlotValueChannel:
    """Class for holding a specific number of values and handling minimum/maximum"""


    def __init__(self, max_value_count: int):

        self._x_data: list[float] = []
        self._y_data: list[float] = []

        self._max_value_count = max_value_count
        self._counter = 0
        self._minimum = None
        self._maximum = None


    def append_value(self, value: float):
        """Appends a value and returns updated minimum and maximum for plot"""
        self._x_data.append(self._counter)
        self._counter += 1
        if len(self._x_data) > self._max_value_count:
            self._x_data.pop(0)

        self._y_data.append(value)
        if len(self._y_data) > self._max_value_count:
            self._y_data.pop(0)

        if self._minimum is None or value < self._minimum:
            self._minimum = value
        if self._maximum is None or value > self._maximum:
            self._maximum = value


    def update_plot(self):
        pass


    @property
    def data(self) -> tuple[list[float], list[float]]:
        return [self._x_data, self._y_data]


    @property
    def limits(self) -> tuple[float, float]:
        return [self._minimum, self._maximum]


class PlotHelper:
    """Class to handle values for plotting"""


    def __init__(self, channels: dict[int, tuple[str, str]], max_value_count: int):
        self._data: dict[int, PlotValueChannel] = {}


    @property
    def data(self) -> dict[int, PlotValueChannel]:
        return self._data


    def append_value(self, channel: int, value: float) -> tuple[float, float]:
        self._data[channel].append_value(value)


    def update(self):
        pass


    def interactive_mode(self, enabled: bool):
        pass
