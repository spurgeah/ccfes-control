import csv
import matplotlib.pyplot as plt

csv_path = r"y:\Hasomed Code\HasomedSetup13\ScienceMode4Python\ccfes-setup\ccfes-setup-7-17\csv_files\7-17-9.csv"
#csv_path = r"Y:\Hasomed Code\HasomedSetup13\ScienceMode4Python\examples\dyscom\csv_files\792.csv"

# Read data
with open(csv_path, newline='') as csvfile:
    reader = csv.reader(csvfile)
    header = next(reader)
    # If the header is a string representation of a list, eval it
    if header[0].startswith("["):
        header = eval(header[0])
    data = [row for row in reader]

# Find column indices
time_idx = header.index("total_runtime")
emg1_idx = header.index("EMG_CH1")
emg2_idx = header.index("EMG_CH2")

# Extract columns
total_runtime = [float(row[time_idx]) for row in data]
emg_ch1 = [float(row[emg1_idx]) for row in data]
emg_ch2 = [float(row[emg2_idx]) for row in data]

# Plot
plt.figure(figsize=(10, 6))
plt.plot(total_runtime, emg_ch1, label="EMG_CH1")
plt.plot(total_runtime, emg_ch2, label="EMG_CH2")
plt.xlabel("Total Runtime (s)")
plt.ylabel("EMG Value")
plt.title("EMG_CH1 and EMG_CH2 vs Total Runtime")
plt.legend()
plt.tight_layout()
plt.show()