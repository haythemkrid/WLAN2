import subprocess
import re
import time
from audioop import avgpp
from math import log10
from turtle import delay

from sympy import symbols, Eq, solve


class APTracker():
    def __init__(self, wifiInterface = "wlp0s20f3"):
        self.AP0, self.AP1, self.AP2=dict(), dict(), dict()
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
                        self.APs[bssid]["Distance2"] = self.distance2(int(self.APs[bssid]["SignalLevel"]))

    def ChooseRefrenceAPs(self):
        while True:
            ap0=input("Enter AP0: ")
            ap1=input("Enter AP1: ")
            ap2=input("Enter AP2: ")
            if (ap0 in self.APs.keys() and ap1 in self.APs.keys() and  ap2 in self.APs.keys()):
                break
                return False
            print("entrer des point d'accès existante")
        self.AP0["BSSID"], self.AP1["BSSID"], self.AP2["BSSID"]=ap0, ap1, ap2
        x0, y0=input("Enter coordinates 0: x y ").split()
        x1, y1=input("Enter coordinates 1: x y ").split()
        x2, y2=input("Enter coordinates 2: x y ").split()
        self.AP0["x"], self.AP1["x"], self.AP2["x"]= float(x0), float(x1), float(x2)
        self.AP0["y"], self.AP1["y"], self.AP2["y"]= float(y0), float(y1), float(y2)
        self.AP0["Distance"], self.AP1["Distance"], self.AP2["Distance"] = self.APs[ap0]["Distance"], self.APs[ap1]["Distance"], self.APs[ap2]["Distance"]
        return True

    def findPosition(self):
        xc0, xc1, xc2, yc0, yc1, yc2 = self.AP0["x"], self.AP1["x"], self.AP2["x"], self.AP0["y"], self.AP1["y"], self.AP2["y"]
        r0,r1,r2=self.APs[self.AP0["BSSID"]]["Distance"], self.APs[self.AP1["BSSID"]]["Distance"], self.APs[self.AP2["BSSID"]]["Distance"]
        x, y = symbols('x y')
        equation1 = Eq((x - xc0)**2+(y-yc0)**2, r0**2)
        equation2 = Eq((x - xc1)**2+(y-yc1)**2, r1**2)
        equation3 = Eq((x - xc2)**2+(y-yc2)**2, r2**2)
        solution1 = solve((equation1, equation2), (x, y))
        solution2 = solve((equation3, equation2), (x, y))
        solution3 = solve((equation1, equation3), (x, y))
        xmoy = round((solution1[0][0]+solution2[0][0]+solution3[0][0]+solution1[1][0]+solution2[1][0]+solution3[1][0])/6, 2)
        ymoy = round((solution1[0][1]+solution2[0][1]+solution3[0][1]+solution1[1][1]+solution2[1][1]+solution3[1][1])/6, 2)
        return xmoy, ymoy

    def format_AP(self,ap):
        ch=f"ESSID: {ap['ESSID']}\n"+"\n".join(["   "+str(i)+": "+str(j) for i,j in ap.items() if i!="ESSID"])
        ch=ch+'\n____________________'
        return ch

    def show_APs(self):
        for AP in list(self.APs.values()):
            print(self.format_AP(AP))

    def distance(self, p, f, rate, p0=0 , n=2 ):
        fm = int(p) - (-154+10*log10(int(rate)*10**6))
        return 10**((p0-0*fm-int(p)-10*n*log10(float(f)*1000)+30*n-32.44)/(10*n))

    def distance2(self, p, n=2):
        measured_power = -44
        return 10 ** ((measured_power - p) / (10 * n))

apt = APTracker()
apt.fetch_APs()
apt.show_APs()
apt.ChooseRefrenceAPs()

while True:
    print(apt.findPosition())
    apt.fetch_APs()
    time.sleep(1)
