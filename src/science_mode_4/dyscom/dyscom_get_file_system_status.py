"""Provides packet classes for dyscom get with type file system status"""

# from dataclasses import dataclass

from typing import NamedTuple
from ..protocol.commands import Commands
from ..protocol.types import ResultAndError
from ..utils.byte_builder import ByteBuilder
from ..protocol.packet import Packet, PacketAck
from .dyscom_types import DyscomGetType
from .dyscom_helper import DyscomHelper
from .dyscom_get import PacketDyscomGet, PacketDyscomGetAck


# @dataclass
# class DyscomGetFileParams():
#     """Dyscom get packet file related parameters"""

#     filename = ""
#     block_offset = 0
#     filesize = 0
#     number_of_blocks = 0


#     def set_data(self, data: bytes):
#         """Convert data to information"""

#         # ToDo
#         control_register = data[0]
#         self.device_id = control_register

#         self.config_register_1.set_data([data[8]])
#         self.config_register_2.set_data([data[9]])
#         self.config_register_3.set_data([data[10]])

#         self.positive_signal_derivation_register = data[23]
#         self.negative_signal_derivation_register = data[22]

#         self.respiration_control_register.set_data([data[21]])


#     def get_data(self) -> bytes:
#         """Convert information to bytes"""

#         if len(self.filename) > 128:
#             raise ValueError(f"Filename name must be shorter than 129 {self.filename}")
#         if self.block_offset < 0 or self.block_offset > 2**32 - 1:
#             raise ValueError(f"block_offset name must be between 0 and 2^32-1 {self.block_offset}")
#         if self.filesize < 0 or self.filesize > 2**32 - 1:
#             raise ValueError(f"filesize name must be between 0 and 2^64-1 {self.filesize}")
#         if self.number_of_blocks < 0 or self.number_of_blocks > 2**32 - 1:
#             raise ValueError(f"number_of_blocks name must be between 0 and 2^32-1 {self.number_of_blocks}")

#         bb = ByteBuilder()
#         bb.append_bytes(DyscomHelper.str_to_bytes(self.filename, 129))
#         bb.append_value(self.block_offset, 4, True)
#         bb.append_value(self.filesize, 8, True)
#         bb.append_value(self.number_of_blocks, 4, True)
#         return bb.get_bytes()

class DyscomGetFileSystemStatusResult(NamedTuple):
    """Helper class for dyscom get with type file system status"""
    file_system_ready: bool
    used_size: int
    free_size: int


class PacketDyscomGetFileSystemStatus(PacketDyscomGet):
    """Packet for dyscom get with type file system status"""


    def __init__(self):
        super().__init__()
        self._command = Commands.DlGet
        self._type = DyscomGetType.FILESYSTEM_STATUS
        self._kind = int(self._type)


class PacketDyscomGetAckFileSystemStatus(PacketDyscomGetAck):
    """Packet for dyscom get for type file system status acknowledge"""


    def __init__(self, data: bytes):
        super().__init__(data)
        self._kind = int(DyscomGetType.FILESYSTEM_STATUS)
        self._file_system_ready = False
        self._used_size = 0
        self._free_size = 0

        if not data is None:
            self._file_system_ready = bool(data[2])
            self._used_size = int.from_bytes(data[3:11], "little")
            self._free_size = int.from_bytes(data[11:19], "little")


    @property
    def file_system_ready(self) -> bool:
        """Getter for file system ready"""
        return self._file_system_ready


    @property
    def used_size(self) -> int:
        """Getter for used size"""
        return self._used_size


    @property
    def free_size(self) -> int:
        """Getter for free size"""
        return self._free_size
