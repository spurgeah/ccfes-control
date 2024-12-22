class Commands:

    GetDeviceId: int = 52
    GetDeviceIdAck: int = 53

    LowLevelInit: int = 0
    LowLevelInitAck: int = 1
    LowLevelChannelConfig: int = 2
    LowLevelChannelConfigAck: int = 3
    LowLevelStop: int = 4
    LowLevelStopAck: int = 5

    GetVersionMain: int = 50
    GetVersionMainAck: int = GetVersionMain + 1