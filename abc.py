import subprocess
import re
from math import log10
from time import sleep
import tkinter as tk
from tkinter import ttk
from threading import Thread


def runCmd():
    # Run the iwconfig command and parse the output
    result = subprocess.run("iwconfig wlp0s20f3", shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    out = result.stdout.decode("utf-8", errors="ignore")

    # Regex to capture ESSID, Frequency, BSSID, Bit Rate, and Signal Level
    match = re.search(
        r'ESSID:"(.*)".*Frequency:([0-9.]+) GHz.*Access Point: ([A-F0-9:]+).*Bit Rate[:=]([0-9.]+) Mb/s.*Signal level=(-[0-9]+) dBm',
        out, re.DOTALL
    )

    if match:
        ESSID, Freq, BSSID, Rate, SignalLevel = match.groups()
        return ESSID, Freq, BSSID, Rate, SignalLevel
    else:
        return None, None, None, None, None


def distance(signal_level, freq, rate, p0=0, n=2):
    # Calculate approximate distance using signal strength
    signal_level = int(signal_level)
    freq_mhz = float(freq) * 1000  # Convert GHz to MHz
    rate_mbps = float(rate)

    fm = signal_level - (-154 + 10 * log10(rate_mbps * 10 ** 6))
    distance = 10 ** ((p0 - 0 * fm - signal_level - 10 * n * log10(freq_mhz) + 30 * n - 32.44) / (10 * n))
    return round(distance, 2)


def update_gui():
    # Periodically update the GUI with Wi-Fi data
    while True:
        ESSID, Freq, BSSID, Rate, SignalLevel = runCmd()
        if ESSID:
            essid_label.config(text=f"ESSID: {ESSID}")
            freq_label.config(text=f"Frequency: {Freq} GHz")
            bssid_label.config(text=f"BSSID: {BSSID}")
            rate_label.config(text=f"Bit Rate: {Rate} Mb/s")
            signal_label.config(text=f"Signal Level: {SignalLevel} dBm")
            distance_val = distance(SignalLevel, Freq, Rate)
            distance_label.config(text=f"Distance: {distance_val} meters")
        else:
            essid_label.config(text="No Wi-Fi data available")

        sleep(1)


# Set up the tkinter GUI
root = tk.Tk()
root.title("Wi-Fi Information")

# Set up styling
style = ttk.Style()
style.configure("TFrame", background="#f2f2f2")
style.configure("TLabel", background="#f2f2f2", font=("Helvetica", 12), foreground="#333333")

# Main frame
main_frame = ttk.Frame(root, padding="10 10 10 10", style="TFrame")
main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
root.columnconfigure(0, weight=1)
root.rowconfigure(0, weight=1)

# Title label
title_label = ttk.Label(main_frame, text="Wi-Fi Network Information", font=("Helvetica", 16, "bold"), style="TLabel")
title_label.grid(row=0, column=0, columnspan=2, pady=(0, 10))

# Labels to display the Wi-Fi data
essid_label = ttk.Label(main_frame, text="ESSID: ", style="TLabel")
freq_label = ttk.Label(main_frame, text="Frequency: ", style="TLabel")
bssid_label = ttk.Label(main_frame, text="BSSID: ", style="TLabel")
rate_label = ttk.Label(main_frame, text="Bit Rate: ", style="TLabel")
signal_label = ttk.Label(main_frame, text="Signal Level: ", style="TLabel")
distance_label = ttk.Label(main_frame, text="Distance: ", style="TLabel")

# Arrange the labels in the GUI window
essid_label.grid(row=1, column=0, sticky=tk.W, pady=2)
freq_label.grid(row=2, column=0, sticky=tk.W, pady=2)
bssid_label.grid(row=3, column=0, sticky=tk.W, pady=2)
rate_label.grid(row=4, column=0, sticky=tk.W, pady=2)
signal_label.grid(row=5, column=0, sticky=tk.W, pady=2)
distance_label.grid(row=6, column=0, sticky=tk.W, pady=2)

# Run the update function in a separate thread to prevent the GUI from freezing
thread = Thread(target=update_gui)
thread.daemon = True
thread.start()

# Start the tkinter main loop
root.mainloop()
