import subprocess
import re
from math import log10


class APTracker():
    def __init__(self, wifiInterface = "wlp0s20f3"):
        self.APs = dict()
        self.wifiInterface = wifiInterface
    def fetch_APs(self):

        result = subprocess.run("iwlist wlp0s20f3 scanning", shell=True, stdout=subprocess.PIPE,
                                 stderr=subprocess.STDOUT)
        out = result.stdout.decode("utf-8", errors="ignore")
        l1 = out.split("Cell")

        result1 = subprocess.run("nmcli dev wifi list", shell=True, stdout=subprocess.PIPE,
                                 stderr=subprocess.STDOUT)
        out1 = result1.stdout.decode("utf-8", errors="ignore")
        l2 = out1.split("\n")
        print(l2)

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

    def format_AP(self,ap):
        ch=f"ESSID: {ap['ESSID']}\n"+"\n".join(["   "+str(i)+": "+str(j) for i,j in ap.items() if i!="ESSID"])
        ch=ch+'\n____________________'
        return ch

    def show_APs(self):
        for AP in list(self.APs.values()):
            print(self.format_AP(AP))

    def distance(self, p, f, rate, p0=0 , n=2.7 ):
        fm = int(p) - (-154+10*log10(int(rate)*10**6))
        print(p, fm)
        return 10**((p0-0*fm-int(p)-10*n*log10(float(f)*1000)+30*n-32.44)/(10*n))

apt = APTracker()
apt.fetch_APs()
apt.show_APs()