import tkinter as tk
from tkinter import simpledialog
import matplotlib.pyplot as plt
import subprocess
import re
import time
from math import log10

class APTracker:
    def __init__(self, wifiInterface="wlp0s20f3"):
        self.APs = dict()
        self.wifiInterface = wifiInterface

    def fetch_APs(self):
        result = subprocess.run(f"iwlist {self.wifiInterface} scanning", shell=True, stdout=subprocess.PIPE,
                                stderr=subprocess.STDOUT)
        out = result.stdout.decode("utf-8", errors="ignore")
        l1 = out.split("Cell")

        result1 = subprocess.run("nmcli dev wifi list", shell=True, stdout=subprocess.PIPE,
                                 stderr=subprocess.STDOUT)
        out1 = result1.stdout.decode("utf-8", errors="ignore")
        l2 = out1.split("\n")

        if len(l1) > 1 and len(l2) > 1:
            l1 = l1[1:]
            l2 = l2[1:]
            for i in l1:
                m = re.findall(
                    r'Address: ([A-F0-9:]*).*Frequency:([0-9.]*).*Signal level=(-[0-9]*).*ESSID:"(.*)"',
                    i, re.DOTALL)
                if m:
                    AP = {
                        "BSSID": m[0][0],
                        "Frequency": m[0][1],
                        "SignalLevel": m[0][2],
                        "ESSID": m[0][3]
                    }
                    self.APs[AP["BSSID"]] = AP

            for i in l2:
                m1 = re.findall(
                    r'\*? *([A-F0-9:]*).* ([0-9]*) Mbit/s.*',
                    i, re.DOTALL)
                if m1:
                    bssid, rate = m1[0][0], m1[0][1]
                    if bssid in self.APs:
                        self.APs[bssid]["Rate"] = rate
                        self.APs[bssid]["Distance"] = self.distance(
                            self.APs[bssid]["SignalLevel"],
                            self.APs[bssid]["Frequency"],
                            rate
                        )
                        self.APs[bssid]["Distance2"] = self.distance2(
                            int(self.APs[bssid]["SignalLevel"])
                        )

    def format_AP(self):
        return [{"ESSID": ap["ESSID"], **ap} for ap in self.APs.values()]

    def show_APs(self):
        return self.format_AP()

    def distance(self, p, f, rate, p0=0, n=2.7):
        fm = int(p) - (-154 + 10 * log10(int(rate) * 10 ** 6))
        return 10 ** ((p0 - 0 * fm - int(p) - 10 * n * log10(float(f) * 1000) + 30 * n - 32.44) / (10 * n))

    def distance2(self, p, n=2):
        measured_power = -44
        return 10 ** ((measured_power - p) / (10 * n))


class APSelectionApp:
    def __init__(self, root, aps):
        self.root = root
        self.root.title("Select Access Points and Coordinates")
        self.aps = aps
        self.picked_aps = {}

        # Set the window size to make it wider
        self.root.geometry("600x400")

        self.listbox = tk.Listbox(root, selectmode=tk.MULTIPLE, width=50, height=10)
        self.listbox.pack(pady=20)

        for ap in self.aps:
            self.listbox.insert(tk.END, ap['ESSID'])

        self.coord_button = tk.Button(root, text="Enter Coordinates", command=self.enter_coordinates)
        self.coord_button.pack(pady=10)

        self.plot_button = tk.Button(root, text="Plot APs", command=self.plot_aps)
        self.plot_button.pack(pady=10)

    def enter_coordinates(self):
        selected_indices = self.listbox.curselection()
        for idx in selected_indices:
            ap = self.aps[idx]
            essid = ap['ESSID']
            x = simpledialog.askinteger("Input", f"Enter x coordinate for {essid}:")
            y = simpledialog.askinteger("Input", f"Enter y coordinate for {essid}:")
            self.picked_aps[essid] = {"coordinates": {"x": x, "y": y}}

    def plot_aps(self):
        plt.figure(figsize=(8, 8))
        plt.axis([0, 20, 0, 20])
        plt.gca().set_aspect('equal', adjustable='box')

        # Use a color map to handle a dynamic number of colors
        cmap = plt.cm.get_cmap('tab20', len(self.picked_aps))  # Colormap for dynamic size
        circles = []

        for i, ap in enumerate(self.aps):
            if ap['ESSID'] in self.picked_aps:
                x = self.picked_aps[ap['ESSID']]['coordinates']['x']
                y = self.picked_aps[ap['ESSID']]['coordinates']['y']
                distance = ap.get('Distance', ap.get('Distance2', 0))  # Use Distance or Distance2 as fallback
                color = cmap(i)  # Get color from the colormap
                circle = plt.Circle((x, y), radius=distance, fill=False, edgecolor=color)
                plt.gca().add_artist(circle)

                # Add the AP name (ESSID) near the corresponding circle
                plt.text(x, y, ap['ESSID'], color=color, ha='center', va='center', fontsize=9, weight='bold')

        plt.title("Access Points with Distances")
        plt.xlabel("X Coordinate")
        plt.ylabel("Y Coordinate")
        plt.grid(True)
        plt.show()


def main():
    apt = APTracker("wlo1")
    apt.fetch_APs()
    aps = apt.show_APs()

    root = tk.Tk()
    app = APSelectionApp(root, aps)
    root.mainloop()
    while True:
        apt.fetch_APs()
        time.sleep(1)
        #i want to refresh the plot every time in the Tkinter interface


if __name__ == "__main__":
    main()
