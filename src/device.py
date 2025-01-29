"""Provides device class representing a science mode device"""

from enum import Enum, auto
from src.layer_mid_level import LayerMidLevel
from .layer import Layer
from .layer_general import LayerGeneral
from .protocol.packet_factory import PacketFactory
from .protocol.packet_number_generator import PacketNumberGenerator
from .utils.connection import Connection


class DeviceCapabilities(Enum):
    """Represent device capabilities"""
    GENERAL = auto()
    LOW_LEVEL = auto()
    MID_LEVEL = auto()
    DYSCOM = auto()


class Device():
    """Base class for a science mode devices"""


    def __init__(self, conn: Connection, capabilities: set[DeviceCapabilities]):
        self._connection  = conn
        self._packet_factory = PacketFactory()
        self._packet_number_generator = PacketNumberGenerator()
        self._capabilities = capabilities
        self._layer: list[Layer] = []

        # ToDo: create layer depending on capabilites and change access functions
        # for x in capabilities:
        self._layer.append(LayerGeneral(self._connection, self._packet_factory, self._packet_number_generator))
        self._layer.append(LayerMidLevel(self._connection, self._packet_factory, self._packet_number_generator))


    @property
    def capabilities(self) -> set[DeviceCapabilities]:
        """Getter for capabilites"""
        return self._capabilities


    async def initialize(self):
        """Initialize device"""
        await self.get_layer_general().initialize()


    def get_layer_general(self) -> LayerGeneral:
        """Helper function to access general layer"""
        return self._layer[0]


    def get_layer_mid_level(self) -> LayerMidLevel:
        """Helper function to access mid level layer"""
        return self._layer[1]
