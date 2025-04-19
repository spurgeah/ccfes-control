"""Provides some helper functionality for examples"""

import sys
import threading
from typing import Callable
from getch import getch

from science_mode_4 import SerialPortConnection


class KeyboardInputThread(threading.Thread):
    """Thread for non blocking keyboard input"""

    def __init__(self, input_cbk: Callable[[str], bool]):
        self._input_cbk = input_cbk
        super().__init__(name = "keyboard_input_thread", daemon = True)
        self.start()


    def run(self):
        while True:
            # getch() returns a bytes object
            key_raw = getch()
            key = bytes.decode(key_raw)
            # handle ctrl+c
            if key == "\x03":
                raise KeyboardInterrupt

            if self._input_cbk(key):
                # callback returned True, so end thread
                break


class ExampleUtils():
    """Helper functions for examples"""

    @staticmethod
    def get_comport_from_commandline_argument() -> str:
        """Get com port from command line argument, if no argument provided,
        look for the first matching device,
        if nothing found, end program with exit code 1"""
        if len(sys.argv) != 2:
            # check for available science mode device ports
            ports = SerialPortConnection.list_science_mode_device_ports()
            if len(ports) > 0:
                return ports[0].device

            # nothing found -> exit
            print("No science mode device found")
            print("Serial port command line argument missing (e.g. python -m examples.<layer>.<example> COM3)")
            sys.exit(1)

        com_port = sys.argv[1]
        return com_port
