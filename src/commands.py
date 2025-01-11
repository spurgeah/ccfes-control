from enum import Enum, auto


class Commands:

    GetDeviceId: int = 52
    GetDeviceIdAck: int = 53
    Reset: int = 58
    ResetAck: int = 59
    GetStimStatus: int = 62
    GetStimStatusAck: int = 63
    GetExtendedVersion: int = 68
    GetExtendedVersionAck: int = 69
    GeneralError: int = 66
    UnkownCommand: int = 67
    
    LowLevelInit: int = 0
    LowLevelInitAck: int = 1
    LowLevelChannelConfig: int = 2
    LowLevelChannelConfigAck: int = 3
    LowLevelStop: int = 4
    LowLevelStopAck: int = 5


class Errors(Enum):
    NO_ERROR = 0
    TRANSFER_ERROR = 1
    PARAMETER_ERROR = 2
    NOT_INITIALIZED = 7
    ELECTRODE_ERROR = 10
    PULSE_TIMEOUT_ERROR = 16
    PULSE_LOW_CURRENT_ERROR = 28

class StimStatus(Enum):
    NO_LEVEL_INITIALIZED = 0
    LOW_LEVEL_INITIALIZED = 1
    MID_LEVEL_INITIALIZED = 2
    MID_LEVEL_RUNNING = 3