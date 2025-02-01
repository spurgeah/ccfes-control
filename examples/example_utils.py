"""Provides some helper functionality for examples"""

import sys
import threading
from typing import Callable


class KeyboardInputThread(threading.Thread):
    """Thread for non blocking keyboard input"""

    def __init__(self, input_cbk: Callable[[str], bool]):
        self._input_cbk = input_cbk
        super().__init__(name = "keyboard_input_thread", daemon = True)
        self.start()


    def run(self):
        while True:
            if self._input_cbk(input()):
                # callback returned True, so end thread
                break


class ExampleUtils():
    """Helper functions for examples"""

    @staticmethod
    def get_comport_from_commandline_argument() -> str:
        """Get com port from command line argument, if no argument provided end program with exit code 1"""
        if len(sys.argv) != 2:
            print("Serial port command line argument missing (e.g. python -m example_xxx.py COM3)")
            sys.exit(1)

        com_port = sys.argv[1]
        return com_port
