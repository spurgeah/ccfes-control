"""Provides result and error type"""

from enum import Enum

class ResultAndError(Enum):
    """Represent science mode type ResultAndError"""
    NO_ERROR = 0
    TRANSFER_ERROR = 1
    PARAMETER_ERROR = 2
    NOT_INITIALIZED = 7
    ELECTRODE_ERROR = 10
    PULSE_TIMEOUT_ERROR = 16
    PULSE_LOW_CURRENT_ERROR = 28