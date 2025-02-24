#!/usr/bin/env python

from enum import Enum
import inspect
from typing import List, Any

#############################################
## Class: AirData
##
class AirData(object):

    def __init__(self):
        self.inputSrcName = None
        self.inputSrcNum = None

        self.sys_time_string = None

        self.IAS = None # Indicated Air Speed in mph
        self.TAS = None # True Air Speed in mph
        self.Alt = None # Altitude in Ft

        self.Alt_agl = None # Above Ground Level ft
        self.Alt_pres = None # Pressure Altitude ft (when baro is set to sea level)
        self.Alt_baro  = None # Barometric Altitude ft
        self.Alt_da = None # Density Altitude ft
        self.AOA = None # Angle of Attack percentage 0 to 100 (if available)
        self.Baro = None # Barometric Pressure in inches of mercury
        self.Baro_diff = None # Barometric Pressure difference in inches of mercury

        self.VSI = None # Vertical Speed Indicator ft/min
        self.OAT = None # outside air temp in F

        self.AOA = None # Angle of Attack percentage 0 to 100 (if available)

        self.Wind_speed = None # Wind Speed in mph
        self.Wind_dir = None # Wind Direction in degrees
        self.Wind_dir_corr = None # corrected for aircraft heading for wind direction pointer
        self.Mag_decl = None #magnetic declination

        self.data_format = 0 # 0 is ft/in, 1 is m/mm, 2 is km/km, 3 is nm/nm
        self.data_format_temp = 0 # 0 is F, 1 is C

        self.msg_count = 0
        self.msg_last = None
        self.msg_bad = 0

    # get IAS in converted format.
    def get_ias(self):
        if(self.data_format==0):
            return self.ias # mph
        if(self.data_format==1):
            return self.ias * 0.8689758 #knots
        if(self.data_format==2):
            return self.ias * 1.609 #km/h

    # get true airspeed in converted format.
    def get_tas(self):
        if(self.data_format==0):
            return self.tas # mph
        if(self.data_format==1):
            return self.tas * 0.8689758 #knots
        if(self.data_format==2):
            return self.tas * 1.609 #km/h

    # get speed format description
    def get_speed_description(self):
        if(self.data_format==0):
            return "mph"
        if(self.data_format==1):
            return "kts"
        if(self.data_format==2):
            return "km/h"

    # get ALT in converted format.
    def get_alt(self):
        #use GPS Alt?
        if(self.data_format==0):
            return self.alt # ft
        if(self.data_format==1):
            return self.alt #ft
        if(self.data_format==2):
            return self.alt * 0.3048 #meters

    # get Baro Alt in converted format.
    def get_balt(self):
        if((self.BALT == None and self.gps.GPSAlt != None) or self.altUseGPS == True):
            self.BALT = self.gps.GPSAlt
            self.altUseGPS = True
        elif(self.BALT == None):
            return 0
        if(self.data_format==0):
            return self.BALT # ft
        if(self.data_format==1):
            return self.BALT #ft
        if(self.data_format==2):
            return self.BALT * 0.3048 #meters

    # get distance format description
    def get_distance_description(self):
        if(self.data_format==0):
            return "ft"
        if(self.data_format==1):
            return "ft"
        if(self.data_format==2):
            return "m"

    # get baro in converted format.
    def get_baro(self):
        if(self.data_format==0):
            return self.baro # inHg
        if(self.data_format==1):
            return self.baro #inHg
        if(self.data_format==2):
            return self.baro * 33.863886666667 #mbars

    # get baro format description
    def get_baro_description(self):
        if(self.data_format==0):
            return "in"
        if(self.data_format==1):
            return "in"
        if(self.data_format==2):
            return "mb"

    # get oat in converted format.
    def get_oat(self):
        if(self.data_format_temp==0):
            return self.oat # f
        if(self.data_format_temp==1):
            return  ((self.oat - 32) / 1.8)

    # get temp format description
    def get_temp_description(self):
        if(self.data_format_temp==0):
            return "\xb0f"
        if(self.data_format_temp==1):
            return "\xb0c"

    # get Vertical speed in converted format.
    def get_vsi_string(self):
        if(self.data_format==0):
            v = self.vsi # ft
            d = "fpm"
        elif(self.data_format==1):
            v = self.vsi #ft
            d = "fpm"
        elif(self.data_format==2):
            v = round(self.vsi * 0.00508) #meters per second
            d = "mps"

        if v == 0:
            return " %d %s" % (v,d)
        elif v < 0:
            return "%d %s" % (v,d)
        else:
            return "+%d %s" % (v,d)


# vi: modeline tabstop=8 expandtab shiftwidth=4 softtabstop=4 syntax=python
