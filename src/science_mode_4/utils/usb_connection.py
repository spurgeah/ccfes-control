"""Provides a class for a usb connection"""

import usb.core
import usb.util
from .connection import Connection

class UsbConnection(Connection):
    """USB connection class,
    IMPORTANT: work in progress (there driver issues under windows)"""


    @staticmethod
    def list_devices() -> list[usb.core.Device]:
        """Returns all USB devices"""
        return list(usb.core.find(find_all=True))


    @staticmethod
    def list_science_mode_devices() -> list[usb.core.Device]:
        """Returns all potential science mode USB devices"""
        devices = UsbConnection.list_devices()
        # science mode devices (P24/I24) have an STM32 mcu and these are
        # default values for USB CDC devices
        filtered_devices = list(filter(lambda x: x.idVendor == 0x0483 and x.idProduct == 0x5740 and
                                       x.bDeviceClass == 0x02, devices))
        return filtered_devices


    def __init__(self, device: usb.core.Device):
        self._device = device
        self._out_endpoint = None
        self._in_endpoint = None
        self._is_open = False


    def open(self):
        # P24/I24 have only one configuration
        self._device.set_configuration()
        # get an endpoint instance
        cfg = self._device.get_active_configuration()
        intf = cfg[(0,0)]

        # match the first OUT endpoint
        self._out_endpoint = usb.util.find_descriptor(
            intf,
            custom_match = lambda e: usb.util.endpoint_direction(e.bEndpointAddress) == usb.util.ENDPOINT_OUT)
        # match the first IN endpoint
        self._in_endpoint = usb.util.find_descriptor(
            intf,
            custom_match = lambda e: usb.util.endpoint_direction(e.bEndpointAddress) == usb.util.ENDPOINT_IN)

        self._is_open = True


    def close(self):
        self._is_open = False


    def is_open(self) -> bool:
        return self._is_open


    def write(self, data: bytes):
        self._out_endpoint.write(data)


    def read(self) -> bytes:
        return self._in_endpoint.read()


    def clear_buffer(self):
        pass
