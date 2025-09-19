import pandas as pd
import matplotlib.pyplot as plt

# === Step 1: Load the CSV file ===
filename = "7-21-14.csv"  # Change this if you saved your CSV under a different name
df = pd.read_csv(filename)

# === Step 2: Extract relevant columns ===
# Assumes columns: "Channel 1", "Channel 2", "Channel 3", "Channel 4"
# These correspond to EMG/Bio signals based on the setup
channel_names = ["Channel 1", "Channel 2", "Channel 3", "Channel 4"]

# Optional: create a time axis from time deltas (in ms or whatever unit used)
if "time_delta" in df.columns:
    time = df["time_delta"].cumsum() / 1000000  # Convert microseconds to seconds (if applicable)
else:
    time = range(len(df))  # Use sample number instead

# === Step 3: Plot all 4 EMG channels ===
fig, axs = plt.subplots(4, 1, figsize=(12, 8), sharex=True)
fig.suptitle("EMG Channel Recordings", fontsize=16)

for i, channel in enumerate(channel_names):
    axs[i].plot(time, df[channel], label=channel, color=f"C{i}")
    axs[i].set_ylabel("Signal")
    axs[i].legend(loc="upper right")
    axs[i].grid(True)

axs[-1].set_xlabel("Time (s)")
plt.tight_layout(rect=[0, 0.03, 1, 0.95])  # Adjust layout to fit title
plt.show()
