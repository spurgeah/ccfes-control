"""Provides a paket factory class"""

from .packet import Packet, PacketAck


class PacketFactory():
    """Packet factory class, it is possible to register multiple packet classes
    per command distinguished by kind"""


    def __init__(self):
        # keys for dict: command, kind, packet class
        self.data: dict[int, int, Packet] = {}
        # register all subclasses of Packet (exclude Packet and PacketAck, because these are base classes)
        self.handle_class(Packet)


    def handle_class(self, cls: type[Packet]):
        """Register all subclasses from cls"""
        for x in cls.__subclasses__():
            # print(f"Handle type {x.__name__}")

            # ignore PacketAck
            if x is not PacketAck:
                if issubclass(x, PacketAck):
                    self.register_packet(x(None))
                else:
                    self.register_packet(x())

            # handle subclasses of this class
            self.handle_class(x)


    def register_packet(self, packet: Packet):
        """Register a packet"""
        # print(f"Register type {packet.__class__.__name__} command {packet.command} kind {packet.kind}")
        self.data[packet.command, packet.kind] = packet


    def create_packet(self, command: int) -> Packet:
        """Create a packet based on command number"""
        copy = self.data[command, -1].create_copy()
        return copy


    def create_packet_with_data(self, command: int, number: int, data: bytes) -> PacketAck:
        """Create a acknowledge packet based on command number with data"""
        # we use default kind of -1 to have a packet class who is able to read kind from data
        proto: PacketAck = self.data[command, -1]
        copy = proto.create_copy_with_data(data)
        # check if we have a specialized kind
        kind = copy.get_kind(data)
        if kind != -1:
            proto = self.data[command, kind]
            copy = proto.create_copy_with_data(data)
        copy.number = number
        return copy
