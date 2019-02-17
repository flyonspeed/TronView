#!/usr/bin/env python


#############################################
## Class: Aircraft
## Store status and converted datat from input modules into this class for use by screens.
##
class Aircraft(object):
    def __init__(self):
        self.pitch = 0.0
        self.roll = 0.0
        self.ias = 0
        self.tas = 0
        self.alt = 0
        self.agl = 0
        self.PALT = 0
        self.BALT = 0
        self.DA = None
        self.aoa = 0
        self.mag_head = 0
        self.gndtrack = 0 #TODO: Move to GPSData class?
        self.baro = 0
        self.baro_diff = 0
        self.vsi = 0
        self.gndspeed = 0 #TODO: Move to GPSData class?
        self.oat = 0
        self.vert_G = 0
        self.slip_skid = None
        self.turn_rate = 0
        self.wind_speed = None
        self.wind_dir = None
        self.norm_wind_dir = None #corrected for aircraft heading for wind direction pointer TODO: Add wind direction pointer to HUD screen
        self.mag_decl = None #magnetic declination

        self.gps = GPSData()
        self.engine = EngineData()
        self.nav = NavData()
        self.traffic = TrafficData()

        self.msg_count = 0
        self.msg_bad = 0
        self.msg_unknown = 0
        self.msg_last = ""
        self.errorFoundNeedToExit = False
        self.demoMode = False
        self.demoFile = ""
        self.textMode = False
        self.show_FPS = False #show screen refresh rate in frames per second for performance tuning


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

