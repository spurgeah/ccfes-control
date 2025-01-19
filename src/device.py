from enum import Enum, auto

from src.layer_mid_level import LayerMidLevel

from .layer import Layer
from .layer_general import LayerGeneral
from .packet_factory import PacketFactory
from .utils.connection import Connection


class DeviceCapabilities(Enum):
    GENERAL = auto()
    LOW_LEVEL = auto()
    MID_LEVEL = auto()
    DYSCOM = auto()


class Device():

    connection: Connection
    packetFactory: PacketFactory
    layer: list[Layer] = []


    def __init__(self, conn: Connection, capabilities: set[DeviceCapabilities]):
        self.connection  = conn
        self.packetFactory = PacketFactory()

        # for x in capabilities:
        self.layer.append(LayerGeneral(conn, self.packetFactory))
        self.layer.append(LayerMidLevel(conn, self.packetFactory))


    async def initialize(self):
        await self.getLayerGeneral().initialize()


    def getLayerGeneral(self) -> LayerGeneral:
        return self.layer[0]


    def getLayerMidLevel(self) -> LayerMidLevel:
        return self.layer[1]


    def f(self):
        return 'hello world'