# -*- coding: utf-8 -*-
"""
Created on Thu Oct 27 10:26:26 2022

@author: wenj
"""

from obspy.core import UTCDateTime
from obspy.clients.fdsn import Client
from obspy.io.sac import SACTrace
from obspy.signal import rotate
import matplotlib.pyplot as plt
import os
from pathlib import Path

client = Client('IRIS')

stime = UTCDateTime('2019-06-17T14:55:00')
etime = UTCDateTime('2019-06-18T00:00:00')

clat = 28.34
clon = 104.96
cat = client.get_events(starttime=stime,endtime=etime,
                        latitude=clat,longitude=clon,maxradius=0.5,
                        minmagnitude=5)
print(cat)

evt = cat[1].origins[0]

evtdir = "%4d.%2.2d.%2.2d.%2.2d.%2.2d.%2.2d" %(evt.time.year , evt.time.month, evt.time.day, evt.time.hour, evt.time.minute, evt.time.second)
if Path(evtdir).exists() :
    print(evtdir, " is existed!")
else:
    os.mkdir(evtdir)
if not Path(evtdir + "/data").exists():
    os.mkdir(evtdir + "/data")
if not Path(evtdir + "/pzs").exists():
    os.mkdir(evtdir + "/pzs")
    
t1 = evt.time - 60
t2 = t1 + 600
inventory = client.get_stations(starttime=stime,endtime=etime,
                                # network='IC,IU,II,JP,KS,CB,XG,PS',sta='*',loc=',10,',channel='?H?',
                                network='*',station='*',location='*',channel='BH?',
                                latitude=clat,longitude=clon,maxradius=7,
                                level="response")

# inventory.plot()
print(inventory)

chan = inventory.get_contents()["channels"]
stinfo = chan[0].split(".")
print(stinfo)
ste = client.get_waveforms(network=stinfo[0],station=stinfo[1],
                  location=stinfo[2],channel=stinfo[3],
                  starttime=t1,endtime=t2)

cmpe = inventory.get_orientation(chan[0])

stinfo = chan[1].split(".")
print(stinfo)
stn = client.get_waveforms(network=stinfo[0],station=stinfo[1],
                  location=stinfo[2],channel=stinfo[3],
                  starttime=t1,endtime=t2)
cmpn = inventory.get_orientation(chan[1])

stinfo = chan[2].split(".")
print(stinfo)
stz = client.get_waveforms(network=stinfo[0],station=stinfo[1],
                  location=stinfo[2],channel=stinfo[3],
                  starttime=t1,endtime=t2)
cmpz = inventory.get_orientation(chan[2])

newst = rotate.rotate2zne(ste[0].data, cmpe['azimuth'], cmpe['dip'], stn[0].data, cmpn['azimuth'], cmpn['dip'], stz[0].data, cmpz['azimuth'], cmpz['dip'])

plt.figure()
plt.plot(newst[0],'b',stz[0].data,'r')
plt.xlim([10000, 12000])
plt.show()

plt.figure()
plt.plot(newst[1],'b',stn[0].data,'r')
plt.xlim([10000, 12000])
plt.show()

plt.figure()
plt.plot(newst[2],'b',ste[0].data,'r')
plt.xlim([10000, 12000])
plt.show()

for chan in inventory.get_contents()["channels"]:
    stinfo = chan.split(".")
    try:
        st = client.get_waveforms(network=stinfo[0],station=stinfo[1],
                          location=stinfo[2],channel=stinfo[3],
                          starttime=t1,endtime=t2)
#        st = client.get_waveforms(stinfo[0], stinfo[1], stinfo[2], stinfo[3], t1, t2)
        sac = SACTrace.from_obspy_trace(st[0])
        sac.lcalda = True
        sac.evla = evt.latitude
        sac.evlo = evt.longitude
        sac.evdp = evt.depth*1e-3
        stcoor = inventory.get_coordinates(chan) 
        sac.stla = stcoor["latitude"]
        sac.stlo = stcoor["longitude"]
        sac.stdp = stcoor["local_depth"]
        cmp_ori = inventory.get_orientation(chan)
        sac.cmpaz = cmp_ori["azimuth"]
        sac.cmpinc = cmp_ori["dip"] + 90
        sac.write(evtdir + "/data/" + chan + ".sac")
# get instrument response
        pz = inventory.get_response(chan, t1).get_sacpz()
        file = open(evtdir + "/pzs/" + chan + ".pz","w")
        file.write(pz)
        file.close()
    except:
        print("there is no data for",chan)