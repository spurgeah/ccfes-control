"""Provides a base class for a connection"""

from abc import ABC, abstractmethod


class Connection(ABC):
    """Abstract base class for connection"""


    @abstractmethod
    def open(self):
        """Open connection"""


    @abstractmethod
    def close(self):
        """Close connection"""


    @abstractmethod
    def is_open(self) -> bool:
        """Checks if connection is open"""


    @abstractmethod
    def write(self, data: bytes):
        """Write data to connection"""


    @abstractmethod
    def read(self) -> bytes:
        """Read all data from connection"""


    @abstractmethod
    def clear_buffer(self):
        """Clear buffer from connection"""
