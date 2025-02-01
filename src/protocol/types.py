"""Provides common types"""

from enum import Enum



# ToDo wrong file
class ResultAndError(Enum):
    """Represent science mode type ResultAndError"""
    NO_ERROR = 0
    TRANSFER_ERROR = 1
    PARAMETER_ERROR = 2
    NOT_INITIALIZED = 7
    ELECTRODE_ERROR = 10
    PULSE_TIMEOUT_ERROR = 16
    PULSE_LOW_CURRENT_ERROR = 28


# ToDo wrong file
class StimStatus(Enum):
    """Represents science mode type StimStatus"""
    NO_LEVEL_INITIALIZED = 0
    LOW_LEVEL_INITIALIZED = 1
    MID_LEVEL_INITIALIZED = 2
    MID_LEVEL_RUNNING = 3
    