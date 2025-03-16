"""Provides all science mode command numbers"""


class Commands:
    """Class with all commands"""

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

    MidLevelInit: int = 30
    MidLevelInitAck: int = 31
    MidLevelUpdate: int = 32
    MidLevelUpdateAck: int = 33
    MidLevelStop: int = 34
    MidLevelStopAck: int = 35
    MidLevelGetCurrentData: int = 36
    MidLevelGetCurrentDataAck: int = 37

    DlInit: int = 100
    DlInitAck: int = 101
    DlStart: int = 102
    DlStartAck: int = 103
    DlStop: int = 104
    DlStopAck: int = 105
    DlGet: int = 109
    DlGetAck: int = 110
    DlPowerModule: int = 111
    DlPowerModuleAck: int = 112
    DlSys: int = 114
    DlSysAck: int = 115

    DlSendLiveData: int = 106
    DlSendFile: int = 107
    DlSendFileAck: int = 113
    DlMmi: int = 108
