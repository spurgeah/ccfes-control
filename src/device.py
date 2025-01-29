"""Provides device class representing a science mode device"""

from enum import Enum, auto
from typing import Type
from src.mid_level.layer_mid_level import LayerMidLevel
from .layer import Layer
from .general.layer_general import LayerGeneral
from .protocol.packet_factory import PacketFactory
from .protocol.packet_number_generator import PacketNumberGenerator
from .utils.connection import Connection


class DeviceCapability(Enum):
    """Represent device capabilities"""
    GENERAL = auto()
    LOW_LEVEL = auto()
    MID_LEVEL = auto()
    DYSCOM = auto()


class Device():
    """Base class for a science mode devices"""


    def __init__(self, conn: Connection, capabilities: set[DeviceCapability]):
        self._connection  = conn
        self._packet_factory = PacketFactory()
        self._packet_number_generator = PacketNumberGenerator()
        self._capabilities = capabilities
        self._layer: dict[DeviceCapability, Layer] = {}

        self._add_layer(DeviceCapability.GENERAL, capabilities, LayerGeneral)
        self._add_layer(DeviceCapability.MID_LEVEL, capabilities, LayerMidLevel)


    @property
    def capabilities(self) -> set[DeviceCapability]:
        """Getter for capabilites"""
        return self._capabilities


    async def initialize(self):
        """Initialize device"""
        await self.get_layer_general().initialize()


    def get_layer_general(self) -> LayerGeneral:
        """Helper function to access general layer"""
        return self._layer[DeviceCapability.GENERAL]


    def get_layer_mid_level(self) -> LayerMidLevel:
        """Helper function to access mid level layer"""
        return self._layer[DeviceCapability.MID_LEVEL]


    def _add_layer(self, capability: DeviceCapability, used_capabilities: set[DeviceCapability], layer_class: Type[Layer]):
        if capability in used_capabilities:
            self._layer[capability] = layer_class(self._connection, self._packet_factory, self._packet_number_generator)
