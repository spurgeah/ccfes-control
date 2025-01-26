"""Provides base class for packets"""

class Packet():
    """Base class for all packets"""


    def __init__(self):
        self._command = -1


    def get_command(self) -> int:
        """Getter for command"""
        return self._command


    def get_data(self) -> bytes:
        """Return packet payload"""
        return []
    

    def create_copy(self) -> 'Packet':
        """Returns a copy"""
        return type(self)()


    command = property(get_command)


class PacketAck(Packet):
    """Base class for all acknowledge packets"""


    def __init__(self, data: bytes):
        _ = data
        super().__init__()


    def create_copy_with_data(self, data: bytes) -> 'Packet':
        """Returns a copy with data"""
        return type(self)(data)
