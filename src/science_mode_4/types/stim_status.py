"""Provides stim status type"""

from enum import Enum


class StimStatus(Enum):
    """Represents science mode type StimStatus"""
    NO_LEVEL_INITIALIZED = 0
    LOW_LEVEL_INITIALIZED = 1
    MID_LEVEL_INITIALIZED = 2
    MID_LEVEL_RUNNING = 3
    