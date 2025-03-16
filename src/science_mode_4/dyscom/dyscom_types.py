"""Provides dyscom types"""

from enum import IntEnum

class DyscomFrequencyOut(IntEnum):
    """Represent dyscom type for frequency out"""
    SAMPLES_PER_SECOND_32K = 1
    SAMPLES_PER_SECOND_16K = 2
    SAMPLES_PER_SECOND_8K = 3
    SAMPLES_PER_SECOND_4K = 4
    SAMPLES_PER_SECOND_2K = 5
    SAMPLES_PER_SECOND_1K = 6
    SAMPLES_PER_SECOND_500 = 7
    SAMPLES_PER_SECOND_250  = 8


class DyscomInitState(IntEnum):
    """Represent dyscom type for init state"""
    SUCESS = 1
    ERROR_STORAGE_INIT = 2
    ERROR_STORAGE_WRITE = 3
    ERROR_STORAGE_FULL = 4
    ERROR_ADS129X_REGISTER  = 6


class DyscomSignalType(IntEnum):
    """Represent dyscom type for signal type"""
    UNKNOWN = 1
    BI = 2
    EMG_1 = 3
    OP_VOLTAGE = 4
    TEST_SIGNAL = 5
    GROUND = 6
    TEMPERATURE = 7
    INTERNAL_SC = 8
    EMG_2 = 9
    TIME = 10
    PUSHBUTTON = 11
    BREATHING = 12


class DyscomFilterType(IntEnum):
    """Represent dyscom type for filter type"""
    FILTER_OFF = 0
    PREDEFINED_FILTER_1 = 1
    PREDEFINED_FILTER_2 = 2
    PREDEFINED_FILTER_3 = 3


class DyscomInitFlag(IntEnum):
    """Represent dyscom type for init flag"""
    ENABLE_LIVE_DATA_MODE = 1 << 0
    ENABLE_SD_STORAGE_MODE = 1 << 1
    ENABLE_TIMED_START = 1 << 2
    SET_SYSTEM_TIME_WITH_SENDED_SYSTEM_TIME_STAMP = 1 << 3
