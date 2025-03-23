"""Provides dyscom types"""

from enum import IntEnum

class DyscomFrequencyOut(IntEnum):
    """Represent dyscom type for frequency out"""
    UNUSED = 0
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
    UNUSED = 0
    SUCESS = 1
    ERROR_STORAGE_INIT = 2
    ERROR_STORAGE_WRITE = 3
    ERROR_STORAGE_FULL = 4
    UNUSED2 = 5
    ERROR_ADS129X_REGISTER  = 6


class DyscomSignalType(IntEnum):
    """Represent dyscom type for signal type"""
    UNUSED = 0
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
    ENABLE_LIVE_DATA_MODE = 0
    ENABLE_SD_STORAGE_MODE = 1
    ENABLE_TIMED_START = 2
    SET_SYSTEM_TIME_WITH_SENDED_SYSTEM_TIME_STAMP = 4


class DyscomGetType(IntEnum):
    """Represent dyscom type for get"""
    UNUSED = 0
    FILESYSTEM_STATUS = 1
    LIST_OF_MEASUREMENT_META_INFO = 2
    OPERATION_MODE = 3
    FILE_BY_NAME = 4
    DEVICE_ID = 5
    FIRMWARE_VERSION = 6
    FILE_INFO = 7


class DyscomGetOperationModeType(IntEnum):
    """Represents dyscom get operation mode type"""
    UNDEFINED = 0
    IDLE = 1
    LIVE_MEASURING_PRE = 2
    LIVE_MEASURING = 3
    RECORD_PRE = 4
    RECORD = 5
    DATATRANSFER_PRE = 6
    DATATRANSFER = 7


class DyscomPowerModuleType(IntEnum):
    """Represents dyscom power module type"""
    MEMORY_CARD = 2
    MEASUREMENT = 3


class DyscomPowerModulePowerType(IntEnum):
    """Represents dyscom power module power type"""
    SWITCH_OFF = 0
    SWITCH_ON = 1
