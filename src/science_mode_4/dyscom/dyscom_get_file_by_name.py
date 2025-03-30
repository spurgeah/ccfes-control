"""Provides packet classes for dyscom get with type file system status"""

from typing import NamedTuple

from ..protocol.commands import Commands
from ..protocol.types import ResultAndError
from ..utils.byte_builder import ByteBuilder
from ..protocol.packet import Packet, PacketAck
from .dyscom_types import DyscomFileByNameMode, DyscomGetType
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

class DyscomGetFileByNameResult(NamedTuple):
    """Helper class for dyscom get with type file by name"""
    filename: str
    block_offset: int
    filesize: int
    number_of_blocks: int
    mode: DyscomFileByNameMode


class PacketDyscomGetFileByName(PacketDyscomGet):
    """Packet for dyscom get with type file by name"""


    def __init__(self):
        super().__init__()
        self._type = DyscomGetType.FILE_BY_NAME
        self._kind = int(self._type)


class PacketDyscomGetAckFileByName(PacketDyscomGetAck):
    """Packet for dyscom get for type file by name acknowledge"""


    def __init__(self, data: bytes):
        super().__init__(data)
        self._kind = int(DyscomGetType.FILE_BY_NAME)
        self._filename = ""
        self._block_offset = 0
        self._filesize = 0
        self._number_of_blocks = 0
        self._mode: DyscomFileByNameMode.UNDEFINED

        if not data is None:
            self._filename = DyscomHelper.bytes_to_str(data[2:130], 128)
            self._block_offset = int.from_bytes(data[130:134], "little")
            self._filesize = int.from_bytes(data[134:142], "little")
            self._number_of_blocks = int.from_bytes(data[142:146], "little")
            self._mode = DyscomFileByNameMode(data[146])



    @property
    def filename(self) -> str:
        """Getter for filename"""
        return self._filename


    @property
    def block_offset(self) -> int:
        """Getter for block offset"""
        return self._block_offset


    @property
    def filesize(self) -> int:
        """Getter for filesize"""
        return self._filesize


    @property
    def number_of_blocks(self) -> int:
        """Getter for number of blocks"""
        return self._number_of_blocks


    @property
    def mode(self) -> DyscomFileByNameMode:
        """Getter for mode"""
        return self._mode
