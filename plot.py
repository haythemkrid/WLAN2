import matplotlib.pyplot as plt
import subprocess
import re
from math import log10


class APTracker():
    def __init__(self, wifiInterface = "wlp0s20f3"):
        self.APs = dict()
        self.wifiInterface = wifiInterface
    def fetch_APs(self):

        result = subprocess.run(f"iwlist {self.wifiInterface}  scanning", shell=True, stdout=subprocess.PIPE,
                                 stderr=subprocess.STDOUT)
        out = result.stdout.decode("utf-8", errors="ignore")

        l1 = out.split("Cell")

        result1 = subprocess.run("nmcli dev wifi list", shell=True, stdout=subprocess.PIPE,
                                 stderr=subprocess.STDOUT)
        out1 = result1.stdout.decode("utf-8", errors="ignore")
        l2 = out1.split("\n")

        if len(l1)  > 1 and len(l2) > 1:
            l1 = l1[1::]
            l2 = l2[1::]
            for i in l1:
                m = re.findall('Address: ([A-F0-9]*:[A-F0-9]*:[A-F0-9]*:[A-F0-9]*:[A-F0-9]*:[A-F0-9]*).*Frequency:([0-9].[0-9]*).*Signal level=(-[0-9]*).*ESSID:"(.*)"',i,re.DOTALL)
                AP=dict()
                AP["BSSID"], AP["Frequency"], AP["SignalLevel"], AP["ESSID"]=m[0][0], m[0][1], m[0][2], m[0][3]
                self.APs[AP["BSSID"]] = AP

            for i in l2:
                m1 = re.findall('\*? *([A-F0-9]*:[A-F0-9]*:[A-F0-9]*:[A-F0-9]*:[A-F0-9]*:[A-F0-9]*).* ([0-9]*) Mbit/s.*',i,re.DOTALL)
                if len(m1) > 0:
                    bssid, rate=m1[0][0], m1[0][1]
                    if bssid in self.APs.keys():
                        self.APs[bssid]["Rate"]=rate
                        self.APs[bssid]["Distance"] = self.distance(self.APs[bssid]["SignalLevel"], self.APs[bssid]["Frequency"], rate)
                        self.APs[bssid]["Distance2"]=self.distance2(int(self.APs[bssid]["SignalLevel"]))

    def format_AP(self):
        ap_list = []
        for ap in self.APs.values():
            # Ensure ESSID is at the top by creating an ordered dictionary
            ap_obj = {"ESSID": ap["ESSID"]}
            # Add other items except ESSID
            for key, value in ap.items():
                if key != "ESSID":
                    ap_obj[key] = value
            ap_list.append(ap_obj)
        return ap_list

    def show_APs(self):
        ap_list = self.format_AP()
        L=[]
        for ap in ap_list:
            L.append(ap)
        return L

    def distance(self, p, f, rate, p0=0 , n=2.7 ):
        fm = int(p) - (-154+10*log10(int(rate)*10**6))
        return 10**((p0-0*fm-int(p)-10*n*log10(float(f)*1000)+30*n-32.44)/(10*n))
    def distance2(self,p,n=2):
        measured_power = -44
        return 10**((measured_power-p)/(10*n))

# ahmed idani interface : wlo1
# haythem krid interface : wlp0s20f3
apt = APTracker("wlo1")
apt.fetch_APs()
L=apt.show_APs()
print(L)

print("Pick 3 access points and their coordinates:")
pickedAPs = {}
for i in range(3):
    pickedAPsName = input(f"Access point {i + 1} ESSID: ")
    x = int(input("Type x coordinate: "))
    y = int(input("Type y coordinate: "))
    # Add the access point as a key with coordinates as values
    pickedAPs[pickedAPsName] = {"coordinates": {"x": x, "y": y}}
#for testing purposes:
"""
pickedAPs ["OPPO A54"]= {"coordinates": {"x": 4, "y": 5}}

pickedAPs["guest network"] = {"coordinates": {"x": 9, "y": 10}}
pickedAPs["TOPNET8A828ED9"] = {"coordinates": {"x": 7, "y": 9}"""

print(pickedAPs)
finalAPs=[]
for i in range(len(L)):
    if L[i]["ESSID"] in pickedAPs:
        L[i]["coordinates"]=pickedAPs[L[i]["ESSID"]]["coordinates"]
        finalAPs.append(L[i])
print(finalAPs)

print("Print Formula to apply for you distance:")
formula = input("type fomula 1/2:")
dist=""
if(formula==1):
    dist="Distance"
else:
    dist="Distance2"



plt.axis([0,35,0,35])
plt.axis("equal")
c=[] #circles to plot
colors=["red","green","blue"]
for i in range(len(finalAPs)):
    x=finalAPs[i]["coordinates"]["x"]
    y=finalAPs[i]["coordinates"]["y"]
    distanceAP= finalAPs[i][dist]

    c.append(plt.Circle((x,y), radius=distanceAP, fill=False, edgecolor=colors[i]))
for circle in c:
    plt.gca().add_artist(circle)
for i in range(len(finalAPs)):
    essid = finalAPs[i]["ESSID"]
    color = colors[i]
    plt.text(25, 30-i*2, essid, color=color, ha='left', va='center', fontsize=10)

plt.show()