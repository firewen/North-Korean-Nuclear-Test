# -*- coding: utf-8 -*-
"""
Created on Sun Sep  4 23:46:42 2022

@author: wenj
"""

from obspy.core import UTCDateTime
from obspy.clients.fdsn import Client
from obspy.io.sac import SACTrace
import os
from pathlib import Path

client = Client('IRIS')

stime = UTCDateTime('2006-10-05T00:00:00')
etime = UTCDateTime('2021-12-09T00:00:00')

clat = 41.30
clon = 129.07
cat = client.get_events(starttime=stime,endtime=etime,
                        latitude=clat,longitude=clon,maxradius=0.5,
                        minmagnitude=1)
print(cat)


file = open('eventlist.txt','w')
for i in range(len(cat)):
    evto = cat[i].origins[0]
    mag = cat[i].magnitudes[0].mag
    evto.time = evto.time + 8*3600
    file.write("%4d-%2.2d-%2.2d %2.2d:%2.2d:%2.2d %8.3f %8.3f %8.3f\n" %(evto.time.year , evto.time.month, evto.time.day, evto.time.hour, evto.time.minute, evto.time.second,evto.longitude,evto.latitude,mag))
file.close()


for i in range(0,9):
    # obtain earthquake information
    evt = cat[i].origins[0]
    
    evtdir = "%4d.%2.2d.%2.2d.%2.2d.%2.2d.%2.2d" %(evt.time.year , evt.time.month, evt.time.day, evt.time.hour, evt.time.minute, evt.time.second)
    if Path(evtdir).exists() :
        print(evtdir, " is existed!")
    else:
        os.mkdir(evtdir)
    if not Path(evtdir + "/data").exists():
        os.mkdir(evtdir + "/data")
    if not Path(evtdir + "/pzs").exists():
        os.mkdir(evtdir + "/pzs")
        
    t1 = evt.time - 160
    t2 = t1 + 800
    inventory = client.get_stations(starttime=stime,endtime=etime,
                                    # network='IC,IU,II,JP,KS,CB,XG,PS',sta='*',loc=',10,',channel='?H?',
                                    network='*',station='*',location='*',channel='BH?',
                                    latitude=clat,longitude=clon,maxradius=12,
                                    level="response")
    
    # inventory.plot()
    print(inventory)
    
                              
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