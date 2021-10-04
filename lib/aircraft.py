#!/usr/bin/env python

from enum import Enum

#############################################
## Class: Aircraft
## Store status and converted datat from input modules into this class for use by screens.
##
class Aircraft(object):
    # measurment data formats (static vars)
    MPH = 0
    KNOTS = 1
    METERS = 2
    TEMP_F = 0
    TEMP_C = 1

    def __init__(self):
        self.sys_time_string = "" 
        self.pitch = 0.0 # degrees
        self.roll = 0.0  # degrees
        self.ias = 1 # in knots
        self.tas = 1
        self.alt = 0 # in Ft
        self.agl = 0
        self.PALT = 0 # in ft
        self.BALT = 0 # in ft
        self.DA = None # in ft
        self.aoa = 0 # percentage 0 to 100
        self.mag_head = 0 # 0 to 360
        self.gndtrack = 0 #TODO: Move to GPSData class?
        self.baro = 0 # inches of mercury
        self.baro_diff = 0
        self.vsi = 0 # ft/min
        self.gndspeed = 1 #TODO: Move to GPSData class?
        self.oat = 0
        self.vert_G = 0
        self.slip_skid = None # -99 to +99.  (-99 is full right)
        self.turn_rate = 0
        self.wind_speed = None
        self.wind_dir = None
        self.norm_wind_dir = None #corrected for aircraft heading for wind direction pointer TODO: Add wind direction pointer to HUD screen
        self.mag_decl = None #magnetic declination

        self.gps = GPSData()
        self.engine = EngineData()
        self.nav = NavData()
        self.traffic = TrafficData()
        self.internal = InteralData()

        self.msg_count = 0
        self.msg_bad = 0
        self.msg_unknown = 0
        self.msg_last = ""
        self.errorFoundNeedToExit = False
        self.demoMode = False
        self.demoFile = ""
        self.textMode = False
        self.show_FPS = False #show screen refresh rate in frames per second for performance tuning
        self.fps = 0

        self.data_format = 0 # 0 is ft/in
        self.data_format_temp = 0 # 0 is F, 1 is C

    # set set measurement to use for data.
    # 0 is US standard. (mph, ft)
    # 1 is knots
    # 2 is metric
    def setDataMeasurementFormat(self,format):
        self.data_format = format

    # get IAS in converted format.
    def get_ias(self):
        if(self.data_format==0):
            return self.ias # mph
        if(self.data_format==1):
            return self.ias * 0.868976 #knots
        if(self.data_format==2):
            return self.ias * 1.609 #km/h

    # get ground speed in converted format.
    def get_gs(self):
        if(self.data_format==0):
            return self.gndspeed # mph
        if(self.data_format==1):
            return self.gndspeed * 0.868976 #knots
        if(self.data_format==2):
            return self.gndspeed * 1.609 #km/h

    # get true airspeed in converted format.
    def get_tas(self):
        if(self.data_format==0):
            return self.tas # mph
        if(self.data_format==1):
            return self.tas * 0.868976 #knots
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
        if(self.data_format==0):
            return self.alt # ft
        if(self.data_format==1):
            return self.alt #ft
        if(self.data_format==2):
            return self.alt * 0.3048 #meters

    # get Baro Alt in converted format.
    def get_balt(self):
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
            return "inHg"
        if(self.data_format==1):
            return "inHg"
        if(self.data_format==2):
            return "mbar"

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
            v = self.vsi * 0.00508 #meters per second
            d = "mps"

        if v < 0:
            return "%d %s" % (v,d)
        else:
            return "+%d %s" % (v,d)

#############################################
## Class: InteralData
class InteralData(object):
    def __init__(self):
        self.Temp = 0 # internal temp of cpu


#############################################
## Class: GPSData
class GPSData(object):
    def __init__(self):
        self.LatHemi = None # North or South
        self.LatDeg = None
        self.LatMin = None  # x.xxx
        self.LonHemi = None # East or West
        self.LonDeg = None
        self.LonMin = None  # x.xxx
        self.GPSAlt = None  # ft MSL
        self.EWVelDir = None  # E or W
        self.EWVelmag = None  # x.x m/s
        self.NSVelDir = None  # N or S
        self.NSVelmag = None  # x.x m/s
        self.VVelDir = None  # U or D
        self.VVelmag = None  # x.xx m/s


#############################################
## Class: NavData
class NavData(object):
    def __init__(self):
        self.NavStatus = ""
        self.HSISource = 0
        self.VNAVSource = 0
        self.AP = 0
        self.HSINeedle = 0
        self.HSIRoseHeading = 0
        self.HSIHorzDev = 0
        self.HSIVertDev = 0

        self.HeadBug = 0
        self.AltBug = 0

        self.WPDist = 0
        self.WPTrack = 0

        self.ILSDev = 0
        self.GSDev = 0
        self.GLSHoriz = 0
        self.GLSVert = 0

        self.msg_count = 0
        self.msg_last = ""


#############################################
## Class: EngineData
class EngineData(object):
    def __init__(self):
        self.RPM = 0
        self.MP = 0
        self.OP = 0
        self.OT = 0
        self.FF = 0

        self.FL1 = 0
        self.FL2 = 0

        self.msg_count = 0
        self.msg_last = ""


#############################################
## Class: TrafficData
class TrafficData(object):
    def __init__(self):
        self.TrafficCount = 0

        self.TrafficMode = 0
        self.NumMsg = 0
        self.ThisMsgNum = 0

        self.msg_count = 0
        self.msg_last = ""


# vi: modeline tabstop=8 expandtab shiftwidth=4 softtabstop=4 syntax=python

