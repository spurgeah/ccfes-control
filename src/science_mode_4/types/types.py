"""Provides common types"""

from enum import Enum

class Channel(Enum):
    """Representa a channel"""
    RED = 0
    BLUE = 1
    BLACK = 2
    WHITE = 3


class Connector(Enum):
    """Representa a cable connector"""
    YELLOW = 0
    GREEN = 1
