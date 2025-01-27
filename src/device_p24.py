"""Provides device class representing a P24"""

from .device import Device, DeviceCapabilities
from .utils.connection import Connection


class DeviceP24(Device):
    """Device class for a P24 device"""

    def __init__(self, conn: Connection):
        super().__init__(conn, [DeviceCapabilities.GENERAL,
                                DeviceCapabilities.LOW_LEVEL,
                                DeviceCapabilities.MID_LEVEL])
