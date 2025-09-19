import asyncio
import threading
from science_mode_4 import DeviceI24, Commands, SerialPortConnection
from science_mode_4.dyscom.dyscom_get_operation_mode import PacketDyscomGetAckOperationMode
from science_mode_4.dyscom.dyscom_types import DyscomGetType, DyscomInitParams, DyscomPowerModulePowerType, DyscomPowerModuleType, DyscomSignalType
from science_mode_4.dyscom.ads129x.ads129x_config_register_1 import Ads129xOutputDataRate, Ads129xPowerMode
from examples.utils.example_utils import ExampleUtils

async def debug_device_communication():
    com_port = ExampleUtils.get_comport_from_commandline_argument()
    connection = SerialPortConnection(com_port)
    connection.open()

    device = DeviceI24(connection)
    print("Initializing device...")
    try:
        await device.initialize()
        print("Device initialized successfully.")
    except Exception as e:
        print(f"Initialization failed: {e}")
        connection.close()
        return

    dyscom = device.get_layer_dyscom()

    # Query supported operation mode
    try:
        print("Querying operation mode...")
        op_mode = await dyscom.get_operation_mode()
        print("Operation mode:", op_mode.operation_mode.name)
    except Exception as e:
        print("Failed to query operation mode:", e)

    # Power on measurement module
    await dyscom.power_module(DyscomPowerModuleType.MEASUREMENT, DyscomPowerModulePowerType.SWITCH_ON)

    # First attempt: your original init parameters
    init_params = DyscomInitParams()
    init_params.signal_type = [DyscomSignalType.BI, DyscomSignalType.EMG_1, DyscomSignalType.EMG_2, DyscomSignalType.BREATHING]
    init_params.register_map_ads129x.config_register_1.output_data_rate = Ads129xOutputDataRate.HR_MODE_500_SPS__LP_MODE_250_SPS
    init_params.register_map_ads129x.config_register_1.power_mode = Ads129xPowerMode.LOW_POWER

    print("Attempting initialization with:")
    print(" signal_type:", init_params.signal_type)
    print(" output_data_rate:", init_params.register_map_ads129x.config_register_1.output_data_rate)
    print(" power_mode:", init_params.register_map_ads129x.config_register_1.power_mode)

    try:
        await dyscom.init(init_params)
        print("Initialization successful with original parameters.")
    except Exception as e:
        print("First initialization failed:", e)
        print("Retrying with safe defaults...")

        # Safe defaults
        safe_params = DyscomInitParams()
        safe_params.signal_type = [DyscomSignalType.EMG_1]
        safe_params.register_map_ads129x.config_register_1.output_data_rate = Ads129xOutputDataRate.HR_MODE_2_KSPS__LP_MODE_1_KSPS
        safe_params.register_map_ads129x.config_register_1.power_mode = Ads129xPowerMode.HIGH_RESOLUTION

        print("Attempting safe defaults:")
        print(" signal_type:", safe_params.signal_type)
        print(" output_data_rate:", safe_params.register_map_ads129x.config_register_1.output_data_rate)
        print(" power_mode:", safe_params.register_map_ads129x.config_register_1.power_mode)

        try:
            await dyscom.init(safe_params)
            print("Initialization successful with safe defaults.")
        except Exception as e2:
            print("Initialization failed with safe defaults as well:", e2)

    connection.close()
    print("Debug session complete.")


def main():
    asyncio.run(debug_device_communication())

if __name__ == "__main__":
    main()

