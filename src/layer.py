"""Provides base class for all ScienceMode layers"""

from src.commands import ResultAndError
from .packet_factory import PacketFactory
from .utils.connection import Connection
from .protocol.packet_number_generator import PacketNumberGenerator


class Layer():
    """Base class for all layers"""


    def __init__(self, conn: Connection, packet_factory: PacketFactory, packet_number_generator: PacketNumberGenerator):
        self._connection  = conn
        self._packet_factory = packet_factory
        self._packet_number_generator = packet_number_generator


    def check_result_error(self, result_error: ResultAndError, packet_name: str):
        """Check if result_error contains an error and if yes prints packet_name"""
        if result_error != ResultAndError.NO_ERROR:
            raise ValueError(f"Error {packet_name} {result_error}")
