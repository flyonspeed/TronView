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
        self.aoa = 0
        self.mag_head = 0
        self.gndtrack = 0
        self.baro = 0
        self.baro_diff = 0
        self.vsi = 0
        self.gndspeed = 0
        self.oat = 0

        self.engine = EngineData()
        self.nav = NavData()

        self.msg_count = 0
        self.msg_bad = 0
        self.msg_unknown = 0
        self.msg_last = ""
        self.errorFoundNeedToExit = False
        self.demoMode = False
        self.textMode = False


#############################################
## Class: NavData
class NavData(object):
    def __init__(self):
        self.AP = 0
        self.HSINeedle = 0
        self.HSIRoseHeading = 0
        self.HeadBug = 0
        self.AltBug = 0

        self.WPDist = 0
        self.WPTrack = 0

        self.ILSDev = 0
        self.GSDev = 0
        self.GLSHorz = 0
        self.GLSVert = 0


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



# vi: modeline tabstop=8 expandtab shiftwidth=4 softtabstop=4 syntax=python

