#!/usr/bin/env python

##Library of useful functions that can be used inside of input modules
##02/06/2019 Brian Chesteen

import math
from lib.geomag import declination

#############################################
## Function: ias2tas By: Brian Chesteen
## Converts indicated airspeed to true airspeed based on
## outside air temp and pressure altitude.

def ias2tas(ias, oat, palt):
    tas = ias * (math.sqrt((273.0 + oat) / 288.0)) * ((1.0 - palt / 144000.0) ** -2.75)
    
    return tas

#############################################
## Function: geomag By: Brian Chesteen 
## Called Function By: Christopher Weiss cmweiss@gmail.com
## Looks up magnetic declination dynamically from GPS Lat and Lon
## Uses coefficients from the World Magnetic Model of the NOAA
## Satellite and Information Service, National Geophysical Data Center
## http://www.ngdc.noaa.gov/geomag/WMM/DoDWMM.shtml

def geomag(LatHemi, LatDeg, LatMin, LonHemi, LonDeg, LonMin):
    if LatHemi == "N":
        GeoMagLat = LatDeg + (LatMin / 60)
    else:
        GeoMagLat = ((LatDeg + (LatMin / 60))  * -1)
    if LonHemi == "W":
        GeoMagLon = ((LonDeg + (LonMin/60))  * -1)
    else:
        GeoMagLon = LonDeg + (LonMin/60)
    mag_decl = declination(GeoMagLat, GeoMagLon)
    
    return mag_decl

#############################################
## Function: gndspeed By: Brian Chesteen
## Calculates GPS ground speed in knots from GPS EW NS velocities in meters/sec.

def gndspeed(EWVelmag, NSVelmag):
    gndspeed = (math.sqrt(((int(EWVelmag) * 0.1)**2) + ((int(NSVelmag) * 0.1)**2))) * 1.94384
    
    return gndspeed

#############################################
## Function: gndtrack By: Brian Chesteen
## Calculates GPS ground track in knots from GPS EW NS quadrant direction and
## velocities in meters/sec.

def gndtrack(EWVelDir, EWVelmag, NSVelDir, NSVelmag):
    if EWVelDir == "W":
        EWVelmag = int(EWVelmag) * -0.1
    else:
        EWVelmag = int(EWVelmag) * 0.1
    if NSVelDir == "S":
        NSVelmag = int(NSVelmag) * -0.1
    else:
        NSVelmag = int(NSVelmag) * 0.1

    gndtrack = (math.degrees(math.atan2(EWVelmag, NSVelmag))) % 360
    
    return gndtrack

#############################################
## Function: windSpdDir By: Brian Chesteen
## Calculates wind speed and direction

def windSpdDir(tas, gndspeed, gndtrack, mag_head, mag_decl):
    if tas > 30 and gndspeed > 30:
        crs = math.radians(gndtrack) #convert degrees to radians
        head = math.radians(mag_head + mag_decl) #convert degrees to radians
        wind_speed = math.sqrt(math.pow(tas - gndspeed, 2) + 4 * tas * gndspeed * math.pow(math.sin((head - crs) / 2), 2))
        wind_dir = crs + math.atan2(tas * math.sin(head-crs), tas * math.cos(head-crs) - gndspeed)
        if wind_dir < 0:
            wind_dir = wind_dir + 2 * math.pi
        if wind_dir > 2 * math.pi:
            wind_dir = wind_dir - 2 * math.pi
        wind_dir = math.degrees(wind_dir) #convert radians to degrees
        norm_wind_dir = (wind_dir + mag_head + mag_decl) % 360 #normalize the wind direction to the airplane heading

    else:
        wind_speed = None
        wind_dir = None
        norm_wind_dir = None
        
    return (wind_speed, wind_dir, norm_wind_dir) 











