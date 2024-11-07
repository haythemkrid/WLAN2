import subprocess
import re
from math import log10


result1 = subprocess.run("iwconfig wlp0s20f3", shell=True, stdout=subprocess.PIPE,
                         stderr=subprocess.STDOUT)
out1 = result1.stdout.decode("utf-8", errors="ignore")

m = re.findall('.*ESSID:"(.*)".*Frequency:([0-9].[0-9]*) GHz  Access Point: ([A-F0-9]*:[A-F0-9]*:[A-F0-9]*:[A-F0-9]*:[A-F0-9]*:[A-F0-9]*).*Bit Rate=([0-9]*.[0-9]*) Mb/s.*Signal level=(-[0-9]*) dBm.*',out1,re.DOTALL)
ESSID, Freq, BSSID, Rate, SignalLevel=m[0][0], m[0][1], m[0][2], m[0][3], m[0][4]


def distance(p, f, rate, p0=0, n=2.7 ):
    p = int(p)
    fm = p - (-154 + 10 * log10(float(rate) * 10 ** 6))
    print(p, fm)
    return 10 ** ((p0 - 0*fm - p - 10 * n * log10(float(f) * 1000) + 30 * n - 32.44) / (10 * n))

print("distance =", distance(SignalLevel,Freq,Rate))
print("SignalLevel =", SignalLevel)
print("Rate =", Rate)