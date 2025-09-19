import csv
import matplotlib.pyplot as plt

csv_path = r"y:\Hasomed Code\HasomedSetup13\ScienceMode4Python\ccfes-setup\ccfes-setup-7-19\csv_files\7-23-8.csv"
#csv_path = r"ccfes-setup\ccfes-setup-7-18\csv_files\7-18-7.csv"
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
#time_idx = (slice(None), header.index("total_runtime") if "total_runtime" in header else header.index("time_delta"))
# emg1_idx = header.index("EMG_CH1")
# emg2_idx = header.index("EMG_CH2")
# emg3_idx = header.index("EMG_CH3") 
# emg4_idx = header.index("EMG_CH4") 
emg1_idx = header.index("Channel 1") 
emg2_idx = header.index("Channel 2")
emg3_idx = header.index("Channel 3") 
emg4_idx = header.index("Channel 4")

# Extract columns
#total_runtime = [float(row[time_idx]) for row in data]
emg_ch1 = [float(row[emg1_idx]) for row in data]
emg_ch2 = [float(row[emg2_idx]) for row in data]
emg_ch3 = [float(row[emg3_idx]) for row in data] if emg3_idx is not None else None
emg_ch4 = [float(row[emg4_idx]) for row in data] if emg4_idx is not None else None  

# Plot
plt.figure(figsize=(10, 6))
# plt.plot(total_runtime, emg_ch1, label="EMG_CH1")
# plt.plot(total_runtime, emg_ch2, label="EMG_CH2")
# plt.plot(total_runtime, emg_ch3, label="EMG_CH3") 
# plt.plot(total_runtime, emg_ch4, label="EMG_CH4")
plt.plot( emg_ch1, label="Channel 1")
plt.plot( emg_ch2, label="Channel 2")
plt.plot( emg_ch3, label="Channel 3")
plt.plot( emg_ch4, label="Channel 4")
plt.xlabel("Total Runtime (packets)")
plt.ylabel("EMG Value")
plt.title("EMG_CH1 and EMG_CH2 vs Total Runtime")
plt.legend()
plt.tight_layout()
plt.show()