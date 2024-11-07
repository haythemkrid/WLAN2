import tkinter as tk
from tkinter import simpledialog
import matplotlib.pyplot as plt
import subprocess
import re
from math import log10

class APTracker():
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
            l1 = l1[1::]
            l2 = l2[1::]
            for i in l1:
                m = re.findall('Address: ([A-F0-9]*:[A-F0-9]*:[A-F0-9]*:[A-F0-9]*:[A-F0-9]*:[A-F0-9]*).*Frequency:([0-9].[0-9]*).*Signal level=(-[0-9]*).*ESSID:"(.*)"', i, re.DOTALL)
                AP = dict()
                AP["BSSID"], AP["Frequency"], AP["SignalLevel"], AP["ESSID"] = m[0][0], m[0][1], m[0][2], m[0][3]
                self.APs[AP["BSSID"]] = AP

            for i in l2:
                m1 = re.findall('\*? *([A-F0-9]*:[A-F0-9]*:[A-F0-9]*:[A-F0-9]*:[A-F0-9]*:[A-F0-9]*).* ([0-9]*) Mbit/s.*', i, re.DOTALL)
                if len(m1) > 0:
                    bssid, rate = m1[0][0], m1[0][1]
                    if bssid in self.APs.keys():
                        self.APs[bssid]["Rate"] = rate
                        self.APs[bssid]["Distance"] = self.distance(self.APs[bssid]["SignalLevel"], self.APs[bssid]["Frequency"], rate)
                        self.APs[bssid]["Distance2"] = self.distance2(int(self.APs[bssid]["SignalLevel"]))

    def format_AP(self):
        ap_list = []
        for ap in self.APs.values():
            ap_obj = {"ESSID": ap["ESSID"]}
            for key, value in ap.items():
                if key != "ESSID":
                    ap_obj[key] = value
            ap_list.append(ap_obj)
        return ap_list

    def show_APs(self):
        ap_list = self.format_AP()
        L = []
        for ap in ap_list:
            L.append(ap)
        return L

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
        plt.axis([0, 35, 0, 35])
        plt.axis("equal")
        colors = ["red", "green", "blue"]
        c = []  # circles to plot
        for i, ap in enumerate(self.aps):
            if ap['ESSID'] in self.picked_aps:
                x = self.picked_aps[ap['ESSID']]['coordinates']['x']
                y = self.picked_aps[ap['ESSID']]['coordinates']['y']
                distance = ap['Distance'] if ap['Distance'] else ap['Distance2']

                c.append(plt.Circle((x, y), radius=distance, fill=False, edgecolor=colors[i % len(colors)]))

        for circle in c:
            plt.gca().add_artist(circle)
        #tkinter
        for i, ap in enumerate(self.aps):
            if ap['ESSID'] in self.picked_aps:
                essid = ap['ESSID']
                x = self.picked_aps[essid]['coordinates']['x']
                y = self.picked_aps[essid]['coordinates']['y']
                color = colors[i % len(colors)]
                plt.text(26, 30-i*2, essid, color=color, ha='left', va='center', fontsize=10)

        plt.show()


def main():
    apt = APTracker("wlo1")
    apt.fetch_APs()
    aps = apt.show_APs()

    root = tk.Tk()
    app = APSelectionApp(root, aps)
    root.mainloop()


if __name__ == "__main__":
    main()
