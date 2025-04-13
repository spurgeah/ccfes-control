"""Provides classes for general GetVersion"""

from typing import NamedTuple
from science_mode_4.protocol.commands import Commands
from science_mode_4.protocol.packet import Packet, PacketAck


class GetExtendedVersionResult(NamedTuple):
    """Helper class for dyscom get with type file system status"""
    firmware_version: str
    science_mode_version: str


class PacketGeneralGetExtendedVersion(Packet):
    """Packet for general GetExtendetVersion"""


    def __init__(self):
        super().__init__()
        self._command = Commands.GetExtendedVersion


class PacketGeneralGetExtendedVersionAck(PacketAck):
    """Packet for general GetExtendetVersion acknowledge"""


    def __init__(self, data: bytes):
        super().__init__(data)
        self._command = Commands.GetExtendedVersionAck
        self._successful = False
        self._firmware_version = ""
        self._science_mode_version = ""
        self._firmware_hash = 0
        self._hash_type = 0
        self._is_valid_hash = False

        if not data is None:
            self._successful = data[0] == 0
            self._firmware_version = f"{data[1]}.{data[2]}.{data[3]}"
            self._science_mode_version = f"{data[4]}.{data[5]}.{data[6]}"
            self._firmware_hash = int.from_bytes(data[7:10], "little")
            self._hash_type = data[11]
            self._is_valid_hash = data[12] == 1


    @property
    def successful(self) -> bool:
        """Getter for Successful"""
        return self._successful


    @property
    def firmware_version(self) -> str:
        """Getter for FirmwareVersion"""
        return self._firmware_version


    @property
    def science_mode_version(self) -> str:
        """Getter for ^ScienceModeVersion"""
        return self._science_mode_version


    @property
    def firmware_hash(self) -> int:
        """Getter for FirmwareHash"""
        return self._firmware_hash


    @property
    def hash_type(self) -> int:
        """Getter for HashType"""
        return self._hash_type


    @property
    def is_valid_hash(self) -> bool:
        """Getter for IsValidHash"""
        return self._is_valid_hash
