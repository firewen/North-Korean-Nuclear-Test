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

# stime = UTCDateTime('1988-02-12T00:00:00')
# etime = UTCDateTime('1989-10-20T00:00:00')

# cat = client.get_events(starttime=stime,endtime=etime,
#                         minlatitude=49.7,maxlatitude=50.1,
#                         minlongitude=78,maxlongitude=79.1,
#                         minmagnitude=5)

stime = UTCDateTime('1998-07-11T00:00:00')
etime = UTCDateTime('1998-07-13T00:00:00')

cat = client.get_events(starttime=stime,endtime=etime,
                        minlatitude=45.7,maxlatitude=50.1,
                        minlongitude=81,maxlongitude=84,
                        minmagnitude=4.5)

print(cat)
for i in range(0,len(cat)):
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
        
    t1 = evt.time - 100
    t2 = t1 + 700
    inventory = client.get_stations(starttime=stime,endtime=etime,
                                    # network='IC,IU,II,JP,KS,CB,XG,PS',sta='*',loc=',10,',channel='?H?',
                                    network='*',station='*',location='*',channel='BH*',
                                    latitude=evt.latitude,longitude=evt.longitude,maxradius=12,
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