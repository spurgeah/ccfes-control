"""Provides packet classes for dyscom init"""

from dataclasses import dataclass, field
import datetime


from ..protocol.commands import Commands
from ..protocol.types import ResultAndError
from ..utils.byte_builder import ByteBuilder
from ..protocol.packet import Packet, PacketAck
from .dyscom_types import DyscomFrequencyOut, DyscomInitState, DyscomSignalType, DyscomFilterType, DyscomInitFlag
from .ads129x.ads129x import Ads129x


@dataclass
class DyscomInitParams():
    """Dyscom init packet parameters"""

    register_map_ads129x = Ads129x()
    start_time = datetime.datetime.now()
    system_time = datetime.datetime.now()
    proband_name = ""
    investigator_name = ""
    proband_number = ""
    number_of_channels: int = 2
    duration = datetime.timedelta()
    signal_type: list[DyscomSignalType] = field(default_factory=lambda: [DyscomSignalType.BI,  DyscomSignalType.EMG_1])
    sync_signal: bool = False
    filter = DyscomFilterType.FILTER_OFF
    flag: set[DyscomInitFlag] = field(default_factory=lambda: {DyscomInitFlag.ENABLE_LIVE_DATA_MODE})


    def get_data(self) -> bytes:
        """Convert information to bytes"""

        bb = ByteBuilder()
        bb.append_bytes(self.register_map_ads129x.get_data())
        return bb.get_bytes()


class PacketDyscomInit(Packet):
    """Packet for dyscom init"""


    def __init__(self, params: DyscomInitParams):
        super().__init__()
        self._command = Commands.DlInit
        self._params = params


    @property
    def params(self) -> DyscomInitParams:
        """Getter for params"""
        return self._params


    @params.setter
    def params(self, value: DyscomInitParams):
        """Setter for params"""
        self._params = value


    def get_data(self) -> bytes:
        return self._params.get_data()


class PacketDyscomInitAck(PacketAck):
    """Packet for dyscom init acknowledge"""


    def __init__(self, data: bytes):
        super().__init__(data)
        self._command = Commands.DlInitAck
        self._result_error = ResultAndError.NO_ERROR
        self.register_map_ads129x: Ads129x
        self._measurement_file_id: str
        self._init_state = DyscomInitState.SUCESS
        self._frequency_out = DyscomFrequencyOut.SAMPLES_PER_SECOND_4K

        if not data is None:
            self._result_error = ResultAndError(data[0])
            self.register_map_ads129x = Ads129x()
            self.register_map_ads129x.set_data(data[1:27])
            self._measurement_file_id = data[27:87]
            self._init_state = DyscomInitState(data[87])
            self._frequency_out = DyscomFrequencyOut[data[88]]


    @property
    def result_error(self) -> ResultAndError:
        """Getter for ResultError"""
        return self._result_error


    @property
    def init_state(self) -> DyscomInitState:
        """Getter for init state"""
        return self._init_state


    @property
    def frequency_out(self) -> DyscomFrequencyOut:
        """Getter for frequency out"""
        return self._frequency_out
