"""Provides packet classes for dyscom init"""

from dataclasses import dataclass, field
import datetime

from ..protocol.commands import Commands
from ..protocol.types import ResultAndError
from ..utils.byte_builder import ByteBuilder
from ..protocol.packet import Packet, PacketAck
from .dyscom_types import DyscomFrequencyOut, DyscomInitState, DyscomSignalType, DyscomFilterType, DyscomInitFlag
from .ads129x.ads129x import Ads129x
from .dyscom_helper import DyscomHelper


@dataclass
class DyscomInitParams():
    """Dyscom init packet parameters"""

    register_map_ads129x = Ads129x()
    start_time = datetime.datetime.now()
    system_time = datetime.datetime.now()
    proband_name = ""
    investigator_name = ""
    proband_number = ""
    duration = datetime.timedelta()
    signal_type: list[DyscomSignalType] = field(default_factory=lambda: [DyscomSignalType.BI,  DyscomSignalType.EMG_1])
    sync_signal: bool = False
    filter = DyscomFilterType.FILTER_OFF
    flags: set[DyscomInitFlag] = field(default_factory=lambda: {DyscomInitFlag.ENABLE_LIVE_DATA_MODE})


    def get_data(self) -> bytes:
        """Convert information to bytes"""

        if len(self.proband_name) > 128:
            raise ValueError(f"Proband name must be shorter than 129 {self.proband_name}")
        if len(self.investigator_name) > 128:
            raise ValueError(f"Investigator name must be shorter than 129 {self.investigator_name}")
        if len(self.proband_number) > 36:
            raise ValueError(f"Proband number must be shorter than 37 {self.proband_number}")


        bb = ByteBuilder()
        bb.append_bytes(self.register_map_ads129x.get_data())
        bb.append_bytes(DyscomHelper.datetime_to_bytes(self.start_time))
        bb.append_bytes(DyscomHelper.datetime_to_bytes(self.system_time))
        bb.append_bytes(DyscomHelper.str_to_bytes(self.proband_name, 129))
        bb.append_bytes(DyscomHelper.str_to_bytes(self.investigator_name, 129))
        bb.append_bytes(DyscomHelper.str_to_bytes(self.proband_number, 37))
        bb.append_value(len(self.signal_type), 2, True)
        bb.append_value(self.duration.seconds, 4, True)
        for x in range(8):
            bb.append_byte(self.signal_type[x] if x < len(self.signal_type) else DyscomSignalType.UNUSED)
        bb.append_byte(0)
        bb.append_byte(1 if self.sync_signal else 0)
        bb.append_byte(self.filter)
        flags = 0
        for x in self.flags:
            flags |= 1 << x
        bb.append_byte(flags)

        return bb.get_bytes()


class PacketDyscomInit(Packet):
    """Packet for dyscom init"""


    def __init__(self, params: DyscomInitParams = DyscomInitParams()):
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
        self._register_map_ads129x: Ads129x
        self._measurement_file_id: str
        self._init_state = DyscomInitState.SUCESS
        self._frequency_out = DyscomFrequencyOut.SAMPLES_PER_SECOND_4K

        if not data is None:
            self._result_error = ResultAndError(data[0])
            self._register_map_ads129x = Ads129x()
            self._register_map_ads129x.set_data(data[1:27])
            self._measurement_file_id = data[27:87]
            self._init_state = DyscomInitState(data[87])
            self._frequency_out = DyscomFrequencyOut(data[88])


    @property
    def result_error(self) -> ResultAndError:
        """Getter for ResultError"""
        return self._result_error


    @property
    def register_map_ads129x(self) -> Ads129x:
        """Getter for register map from ADS129x"""
        return self._register_map_ads129x


    @property
    def init_state(self) -> DyscomInitState:
        """Getter for init state"""
        return self._init_state


    @property
    def frequency_out(self) -> DyscomFrequencyOut:
        """Getter for frequency out"""
        return self._frequency_out
