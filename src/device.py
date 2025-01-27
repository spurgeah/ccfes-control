"""Provides device class representing a science mode device"""

from enum import Enum, auto
from src.layer_mid_level import LayerMidLevel
from .layer import Layer
from .layer_general import LayerGeneral
from .packet_factory import PacketFactory
from .utils.connection import Connection


class DeviceCapabilities(Enum):
    """Represent device capabilities"""
    GENERAL = auto()
    LOW_LEVEL = auto()
    MID_LEVEL = auto()
    DYSCOM = auto()


class Device():
    """Base class for a science mode devices"""

    connection: Connection
    packetFactory: PacketFactory
    layer: list[Layer] = []


    def __init__(self, conn: Connection, capabilities: set[DeviceCapabilities]):
        self._connection  = conn
        self._packet_factory = PacketFactory()
        self._capabilities = capabilities

        # ToDo: create layer depending on capabilites and change access functions
        # for x in capabilities:
        self.layer.append(LayerGeneral(self._connection, self._packet_factory))
        self.layer.append(LayerMidLevel(self._connection, self._packet_factory))


    @property
    def capabilities(self) -> set[DeviceCapabilities]:
        """Getter for capabilites"""
        return self._capabilities


    async def initialize(self):
        """Initialize device"""
        await self.get_layer_general().initialize()


    def get_layer_general(self) -> LayerGeneral:
        """Helper function to access general layer"""
        return self.layer[0]


    def get_layer_mid_level(self) -> LayerMidLevel:
        """Helper function to access mid level layer"""
        return self.layer[1]
