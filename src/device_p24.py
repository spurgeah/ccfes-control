from .device import Device, DeviceCapabilities
from .utils.connection import Connection


class DeviceP24(Device):


    def __init__(self, conn: Connection):
        super().__init__(conn, [DeviceCapabilities.GENERAL, 
                                DeviceCapabilities.LOW_LEVEL, 
                                DeviceCapabilities.MID_LEVEL])
