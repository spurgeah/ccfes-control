"""Provides class for ADS129x chip"""

from dataclasses import dataclass

from ...utils.byte_builder import ByteBuilder
from .ads129x_config_register_1 import Ads129xConfigRegister1
from .ads129x_config_register_2 import Ads129xConfigRegister2
from .ads129x_config_register_3 import Ads129xConfigRegister3
from .ads129x_respiration_control_register import Ads129xRespirationControlRegister


@dataclass
class Ads129x:
    """Describes register map of ADS129x chip"""

    # control register
    device_id = 0

    # config register
    config_register_1 = Ads129xConfigRegister1()
    config_register_2 = Ads129xConfigRegister2()
    config_register_3 = Ads129xConfigRegister3()

    positive_signal_derivation_register = 0x02
    negative_signal_derivation_register = 0x02

    respiration_control_register = Ads129xRespirationControlRegister()


    def set_data(self, data: bytes):
        """Convert data to information"""

        control_register = data[0]
        self.device_id = control_register

        self.config_register_1.set_data(data[1])
        self.config_register_2.set_data(data[2])
        self.config_register_3.set_data(data[3])

        self.positive_signal_derivation_register = data[13]
        self.negative_signal_derivation_register = data[14]

        self.respiration_control_register.set_data(data[22])


    def get_data(self) -> bytes:
        """Convert information to bytes"""

        bb = ByteBuilder()
        bb.set_bytes_to_position(self.config_register_1.get_data(), 1, 1)
        bb.set_bytes_to_position(self.config_register_2.get_data(), 2, 1)
        bb.set_bytes_to_position(self.config_register_3.get_data(), 3, 1)

        bb.set_bytes_to_position([self.positive_signal_derivation_register], 13, 1)
        bb.set_bytes_to_position([self.negative_signal_derivation_register], 14, 1)

        bb.set_bytes_to_position(self.respiration_control_register.get_data(), 22, 1)

        return bb.get_bytes()
