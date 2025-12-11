"""
EMG-only processing for Hasomed ScienceMode I24

This script reads live data from the I24 measurement device (Hasomed), processes
EMG channels EMG_1 and EMG_2 (device channels 2 and 3 in the packet), converts
to millivolts, applies a highpass (default 20 Hz) and zero-phase bandpass
(20-450 Hz), full-wave rectifies, computes RMS using a sliding window, and
prints normalized muscle effort and threshold events to the terminal.

User-editable parameters are at the top of this file (COM port, calibration,
filter orders, MVC values, window sizes, and thresholds).

Usage: run this file from the repository root where `science_mode_4` is importable.
    python asp_emg_processing.py

Notes:
- This is a streaming/simple-block processor intended for demo and offline analysis
  using packets from the I24 device. In live use, adjust buffer sizes and block
  durations to match your latency/accuracy requirements.
"""

import asyncio
import threading
import time
from typing import List
import os
import csv

import numpy as np
from scipy.signal import butter, filtfilt

# Device imports (same as other repo scripts)
from science_mode_4 import DeviceI24, Commands, SerialPortConnection as SerialPortI24
from science_mode_4.dyscom.dyscom_send_live_data import PacketDyscomSendLiveData
from science_mode_4.dyscom.dyscom_types import (
    DyscomInitParams,
    DyscomSignalType,
    DyscomPowerModuleType,
    DyscomPowerModulePowerType,
)
from science_mode_4.dyscom.ads129x.ads129x_config_register_1 import Ads129xOutputDataRate, Ads129xPowerMode



# Make repository 'examples' package importable regardless of cwd
import sys
from pathlib import Path
_p = Path(__file__).resolve()
_repo_root = None
for _ in range(6):
    if (_p / 'examples').exists():
        _repo_root = _p
        break
    _p = _p.parent
if _repo_root is not None:
    sys.path.insert(0, str(_repo_root))

# Optional plotting helper
try:
    from examples.utils.fastplotlib_utils import FastPlotLibHelper
except Exception:
    FastPlotLibHelper = None


# ------------------------ User configuration ------------------------
# Serial port for I24 device
I24_COM = "COM3"

# ADC / conversion parameters (match your device setup)
VREF = 4.0  # Volts
GAIN = 6    # Amplifier gain used on the device
CURRENT = 30e-6  # 30 µA injected (used for converted BI channel) - kept for consistency

# Sampling frequency (Hz) -- must match the device init params below
FS = 500

# Filter parameters
HIGHPASS_CUTOFF = 20.0  # Hz (remove motion/DC)
HIGHPASS_ORDER = 4      # 2..4 (user may set 2,3 or 4)
BANDPASS_LOW = 20.0     # Hz
BANDPASS_HIGH = 450.0   # Hz
BANDPASS_ORDER = 4      # order for butterworth bandpass used with filtfilt

# RMS smoothing (window and overlap in ms)
RMS_WINDOW_MS = 100     # window size in ms (50-100 suggested)
RMS_OVERLAP_MS = 10     # step size between RMS computations in ms

# Normalization / thresholds (user should set MVC values per muscle in millivolts)
MVC_CH1_UV = 3 * 10**-6 # mV -> .004 µV
MVC_CH2_UV = 6 * 10**-6 # mV -> .004 µV
THRESHOLD_NORM = 0.20   # normalized threshold as fraction of MVC (e.g., 0.10 -> 10% MVC)

# Processing block (how many seconds of data to collect before processing)
BLOCK_SEC = 0.5

# ---------------------- End user configuration ----------------------

stop_event = threading.Event()


def butter_highpass(cutoff_hz: float, fs: float, order: int = 4):
    nyq = 0.5 * fs
    b, a = butter(order, cutoff_hz / nyq, btype='high', analog=False)
    return b, a


def butter_bandpass(lowcut: float, highcut: float, fs: float, order: int = 4):
    nyq = 0.5 * fs
    b, a = butter(order, [lowcut / nyq, highcut / nyq], btype='band', analog=False)
    return b, a


def convert_raw_to_mv(raw_adc: int, channel_index: int) -> float:
    """
    Convert raw ADC value from packet to millivolts for EMG channels.
    channel_index uses the same mapping as packets in `ccfes_runlive.py` where
    index 1 and 2 correspond to EMG_1 and EMG_2 respectively.
    """
    # The conversion below follows the approach in the repository examples.
    # For EMG channels (not BI), multiply by 1e3 to get millivolts.
    if channel_index == 0:
        # BI channel conversion (kept for completeness) -> returns millivolts
        return ((raw_adc * VREF * 2) / ((2 ** 24) * GAIN)) / CURRENT
    else:
        return ((raw_adc * VREF * 2) / ((2 ** 24) * GAIN)) * 1e3


def sliding_rms(signal: np.ndarray, window_samples: int, step_samples: int) -> tuple[np.ndarray, np.ndarray]:
    """
    Compute sliding RMS of `signal` using window length `window_samples` and step `step_samples`.
    Returns (rms_timeseries, center_indices) where the rms array corresponds to center indices
    in the original signal.
    """
    if window_samples <= 0:
        raise ValueError("window_samples must be > 0")
    if step_samples <= 0:
        raise ValueError("step_samples must be > 0")

    x2 = signal ** 2
    win = np.ones(window_samples, dtype=float)
    # Use convolution to compute moving sum of squares
    summed = np.convolve(x2, win, mode='valid')
    rms = np.sqrt(summed / window_samples)

    # indices of center points for each RMS value
    start = window_samples // 2
    indices = np.arange(start, start + len(rms))

    # sub-sample by step_samples to implement overlap/step
    sel = np.arange(0, len(rms), step_samples)
    return rms[sel], indices[sel]


def listen_for_input():
    input("Press Enter to stop processing...\n")
    stop_event.set()


async def main():
    print("Starting EMG processing...")
    # Open connection to I24 device
    record_connection = SerialPortI24(I24_COM)
    record_connection.open()
    record_device = DeviceI24(record_connection)
    await record_device.initialize()
    dyscom = record_device.get_layer_dyscom()

    # Configure device measurement parameters (match values used elsewhere)
    init_params = DyscomInitParams()
    init_params.signal_type = [
        DyscomSignalType.BI,
        DyscomSignalType.EMG_1,
        DyscomSignalType.EMG_2,
        DyscomSignalType.BREATHING,
    ]
    init_params.register_map_ads129x.config_register_1.output_data_rate = (
        Ads129xOutputDataRate.HR_MODE_4_KSPS__LP_MODE_2_KSPS
    )
    init_params.register_map_ads129x.config_register_1.power_mode = (
        Ads129xPowerMode.HIGH_RESOLUTION
    )

    # Start measurement
    await dyscom.power_module(DyscomPowerModuleType.MEASUREMENT, DyscomPowerModulePowerType.SWITCH_ON)
    await dyscom.init(init_params)
    await dyscom.start()

    # use a local fs variable and try to detect actual sampling freq from device config
    fs = FS
    try:
        odr = init_params.register_map_ads129x.config_register_1.output_data_rate
        odr_name = getattr(odr, 'name', str(odr))
        import re
        matches = re.findall(r"(\d+)_KSPS|(\d+)_SPS", odr_name)
        fs_candidates = []
        for m in matches:
            if m[0]:
                fs_candidates.append(int(m[0]) * 1000)
            elif m[1]:
                fs_candidates.append(int(m[1]))
        if fs_candidates:
            fs = max(fs_candidates)
            print(f"Detected output_data_rate '{odr_name}' -> FS={fs} Hz")
        else:
            print(f"Could not parse output_data_rate '{odr_name}', using FS={fs} Hz")
    except Exception as e:
        print(f"Warning: failed to detect FS from device config: {e}. Using FS={fs} Hz")

    # Build filters using detected fs
    hp_b, hp_a = butter_highpass(HIGHPASS_CUTOFF, fs, order=HIGHPASS_ORDER)

    # Ensure bandpass high cutoff is below Nyquist (fs/2). If not, clamp and warn.
    nyq = 0.5 * fs
    bp_high = BANDPASS_HIGH
    bp_low = BANDPASS_LOW
    if not (0 < bp_low < nyq):
        print(f"Warning: requested bandpass low {bp_low} Hz is out of (0, Nyquist={nyq} Hz). Clamping to 1 Hz.")
        bp_low = max(1.0, min(bp_low, nyq * 0.5))
    if not (0 < bp_high < nyq):
        bp_high = max(bp_low + 1.0, nyq * 0.95)
        print(f"Warning: requested bandpass high {BANDPASS_HIGH} Hz >= Nyquist ({nyq} Hz). Clamping to {bp_high:.4f} Hz.")

    bp_b, bp_a = butter_bandpass(bp_low, bp_high, fs, order=BANDPASS_ORDER)

    # --- CSV output setup ---
    os.makedirs('csv_files', exist_ok=True)
    csv_path = os.path.join('csv_files', 'emg_processing.csv')
    csv_file = open(csv_path, 'w', newline='')
    csv_writer = csv.writer(csv_file)
    csv_writer.writerow(['timestamp', 'packet_nr', 'device_time_offset_us', 'raw_ch1_mv', 'raw_ch2_mv', 'rms_ch1_mv', 'rms_ch2_mv', 'norm_ch1', 'norm_ch2'])

    block_size = max(int(BLOCK_SEC * fs), 32)
    buffer_ch1: List[float] = []
    buffer_ch2: List[float] = []

    # RMS window and step in samples
    window_samples = max(1, int(RMS_WINDOW_MS * fs / 1000.0))
    step_samples = max(1, int(RMS_OVERLAP_MS * fs / 1000.0))

    # Setup plotting helper if available
    if FastPlotLibHelper is not None:
        plot_helper = FastPlotLibHelper({
            0: ["EMG RMS CH1 (mV)", "g"],
            1: ["EMG RMS CH2 (mV)", "m"],
            2: ["Raw CH1 (mV)", "r"],
            3: ["Raw CH2 (mV)", "b"],
        }, 1000)
    else:
        plot_helper = None

    threading.Thread(target=listen_for_input, daemon=True).start()
    print(f">>> Processing EMG CH1/CH2. FS={fs} Hz, block={block_size} samples, RMS window={window_samples} samples")

    try:
        while not stop_event.is_set():
            ack = dyscom.packet_buffer.get_packet_from_buffer()
            if ack and ack.command == Commands.DL_SEND_LIVE_DATA:
                sld: PacketDyscomSendLiveData = ack
                if sld.status_error:
                    print("Received status error, stopping")
                    break

                # Extract raw ADC values for EMG channels (index 1 and 2 as in repo examples)
                raw_ch1 = sld.samples[1].value
                raw_ch2 = sld.samples[2].value

                uv_ch1 = convert_raw_to_mv(raw_ch1, 1)
                uv_ch2 = convert_raw_to_mv(raw_ch2, 2)

                # Append rectified (abs) values to buffers for future processing
                buffer_ch1.append(abs(uv_ch1))
                buffer_ch2.append(abs(uv_ch2))

                # If we have enough data to process a block, do filtering + RMS
                if len(buffer_ch1) >= block_size:
                    # Convert to numpy arrays
                    x1 = np.asarray(buffer_ch1, dtype=float)
                    x2 = np.asarray(buffer_ch2, dtype=float)

                    # Apply DC removal / highpass then zero-phase bandpass using filtfilt
                    try:
                        x1_hp = filtfilt(hp_b, hp_a, x1)
                        x1_bp = filtfilt(bp_b, bp_a, x1_hp)

                        x2_hp = filtfilt(hp_b, hp_a, x2)
                        x2_bp = filtfilt(bp_b, bp_a, x2_hp)
                    except Exception as e:
                        # filtfilt can fail on too-short signals; fallback to unfiltered data
                        print(f"Filter error (insufficient data?): {e}. Skipping filters for this block.")
                        x1_bp = x1
                        x2_bp = x2

                    # Full-wave rectify (absolute)
                    x1_rect = np.abs(x1_bp)
                    x2_rect = np.abs(x2_bp)

                    # Compute sliding RMS
                    rms1, inds1 = sliding_rms(x1_rect, window_samples=window_samples, step_samples=step_samples)
                    rms2, inds2 = sliding_rms(x2_rect, window_samples=window_samples, step_samples=step_samples)

                    # Take the most recent RMS value as current level
                    if len(rms1) > 0:
                        current_rms_ch1 = rms1[-1]
                    else:
                        current_rms_ch1 = np.mean(x1_rect)
                    if len(rms2) > 0:
                        current_rms_ch2 = rms2[-1]
                    else:
                        current_rms_ch2 = np.mean(x2_rect)

                    # Normalize by MVC (use absolute values to avoid negative MVC entries)
                    norm_ch1 = current_rms_ch1 / max(abs(MVC_CH1_UV), 1e-12)
                    norm_ch2 = current_rms_ch2 / max(abs(MVC_CH2_UV), 1e-12)

                    # Threshold detection and nested-if printing
                    # For CH1
                    if norm_ch1 >= THRESHOLD_NORM:
                        # nested check for high effort
                        if norm_ch1 >= 0.6:
                            print(f"[CH1] HIGH EFFORT: {norm_ch1*100:.4f}% MVC (>=60% MVC). Threshold={THRESHOLD_NORM*100:.4f}%")
                            #print(f"Current RMS (mV): CH1={current_rms_ch1:.4f}, CH2={current_rms_ch2:.4f}")
                        else:
                            print(f"[CH1] Above threshold: {norm_ch1*100:.4f}% MVC. Threshold={THRESHOLD_NORM*100:.4f}%")
                    else:
                        print(f"[CH1] Below threshold: {norm_ch1*100:.4f}% MVC (threshold {THRESHOLD_NORM*100:.4f}%).")

                    # For CH2
                    if norm_ch2 >= THRESHOLD_NORM:
                        if norm_ch2 >= 0.6:
                            print(f"[CH2] HIGH EFFORT: {norm_ch2*100:.4f}% MVC (>=60% MVC). Threshold={THRESHOLD_NORM*100:.4f}%")
                        else:
                            print(f"[CH2] Above threshold: {norm_ch2*100:.4f}% MVC. Threshold={THRESHOLD_NORM*100:.4f}%")
                    else:
                        print(f"[CH2] Below threshold: {norm_ch2*100:.4f}% MVC (threshold {THRESHOLD_NORM*100:.4f}%).")

                    # Optionally print raw RMS values (mV) and timestamp
                    print(f"Current RMS (mV): CH1={current_rms_ch1:.4f}, CH2={current_rms_ch2:.4f}")

                    # Append to CSV (include raw millivolts and device time offset)
                    try:
                        ts = time.time()
                        pkt = getattr(ack, 'number', None)
                        device_offset = getattr(sld, 'time_offset', None)
                        csv_writer.writerow([ts, pkt, device_offset, float(uv_ch1), float(uv_ch2), float(current_rms_ch1), float(current_rms_ch2), float(norm_ch1), float(norm_ch2)])
                        csv_file.flush()
                    except Exception as e:
                        print(f"Failed to write CSV row: {e}")

                    # Update plots if available
                    if plot_helper is not None:
                        try:
                            plot_helper.append_value(0, current_rms_ch1)
                            plot_helper.append_value(1, current_rms_ch2)
                            plot_helper.append_value(2, uv_ch1)
                            plot_helper.append_value(3, uv_ch2)
                            overlay_text = (
                                f"CH1: {norm_ch1*100:.4f}% MVC ({'ON' if norm_ch1>=THRESHOLD_NORM else 'OFF'})\n"
                                f"CH2: {norm_ch2*100:.4f}% MVC ({'ON' if norm_ch2>=THRESHOLD_NORM else 'OFF'})\n"
                            )
                            if hasattr(plot_helper, "set_text_overlay"):
                                plot_helper.set_text_overlay(overlay_text)
                            plot_helper.update()
                        except Exception:
                            pass

                    # Remove the processed block while keeping a small overlap equal to window length
                    # Keep last `window_samples` samples to preserve continuity
                    keep = window_samples
                    buffer_ch1 = buffer_ch1[-keep:]
                    buffer_ch2 = buffer_ch2[-keep:]

                # Otherwise wait a tiny bit
            else:
                await asyncio.sleep(0.001)

    except KeyboardInterrupt:
        print("KeyboardInterrupt received, stopping")

    finally:
        print(">>> Stopping device and cleaning up")
        try:
            await dyscom.stop()
        except Exception:
            pass
        try:
            await dyscom.power_module(dyscom.PowerModuleType.MEASUREMENT, dyscom.PowerModulePowerType.SWITCH_OFF)
        except Exception:
            pass
        # Close CSV file
        try:
            csv_file.close()
        except Exception:
            pass
        record_connection.close()


if __name__ == "__main__":
    asyncio.run(main())
