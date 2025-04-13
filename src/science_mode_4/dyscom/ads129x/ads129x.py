"""Provides class for ADS129x chip"""

from dataclasses import dataclass

from science_mode_4.utils.byte_builder import ByteBuilder
from .ads129x_config_register_1 import Ads129xConfigRegister1
from .ads129x_config_register_2 import Ads129xConfigRegister2
from .ads129x_config_register_3 import Ads129xConfigRegister3
from .ads129x_config_register_4 import Ads129xConfigRegister4
from .ads129x_respiration_control_register import Ads129xRespirationControlRegister


@dataclass
class Ads129x:
    """Describes register map of ADS129x chip"""

    # control register
    device_id = 0

    # config register
    config_register_1 = Ads129xConfigRegister1() # CONFIG1
    config_register_2 = Ads129xConfigRegister2() # CONFIG2
    config_register_3 = Ads129xConfigRegister3() # CONFIG3
    config_register_4 = Ads129xConfigRegister4() # CONFIG4

    # signal derivation register
    positive_signal_derivation_register = 0x02 # RLD_SENSP
    negative_signal_derivation_register = 0xEA # RLD_SENSN

    # respiration register
    respiration_control_register = Ads129xRespirationControlRegister() # RESP


    def set_data(self, data: bytes):
        """Convert data to information"""

        control_register = data[0]
        self.device_id = control_register

        self.config_register_1.set_data([data[8]])
        self.config_register_2.set_data([data[9]])
        self.config_register_3.set_data([data[10]])
        self.config_register_4.set_data([data[11]])

        self.positive_signal_derivation_register = data[23]
        self.negative_signal_derivation_register = data[22]

        self.respiration_control_register.set_data([data[21]])


    def get_data(self) -> bytes:
        """Convert information to bytes"""

        bb = ByteBuilder(0, 26)
        bb.set_bytes_to_position(self.config_register_1.get_data(), 8, 1)
        bb.set_bytes_to_position(self.config_register_2.get_data(), 9, 1)
        bb.set_bytes_to_position(self.config_register_3.get_data(), 10, 1)
        bb.set_bytes_to_position(self.config_register_4.get_data(), 11, 1)

        bb.set_bytes_to_position([self.positive_signal_derivation_register], 23, 1)
        bb.set_bytes_to_position([self.negative_signal_derivation_register], 22, 1)

        bb.set_bytes_to_position(self.respiration_control_register.get_data(), 21, 1)

        return bb.get_bytes()
