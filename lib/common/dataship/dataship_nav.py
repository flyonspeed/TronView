#!/usr/bin/env python

from enum import Enum
import inspect
from typing import List, Any
import time

#############################################
## Class: NavData
class NavData(object):
    def __init__(self):
        self.inputSrcName = None
        self.inputSrcNum = None

        self.NavStatus = ""
        self.HSISource = 0
        self.VNAVSource = 0
        self.SourceDesc = ""
        self.HSINeedle = 0
        self.HSIRoseHeading = 0
        self.HSIHorzDev = 0
        self.HSIVertDev = 0

        self.AP = None # AP enabled? 0 = off, 1 = on

        self.AP_RollForce = None
        self.AP_RollPos = None
        self.AP_RollSlip = None

        self.AP_PitchForce = None
        self.AP_PitchPos = None
        self.AP_PitchSlip = None

        self.AP_YawForce = None
        self.AP_YawPos = None
        self.AP_YawSlip = None

        self.HeadBug = 0
        self.AltBug = 0
        self.ASIBug = 0
        self.VSBug = 0

        self.WPDist = 0
        self.WPTrack = 0
        self.WPName = None

        self.ILSDev = 0
        self.GSDev = 0
        self.GLSHoriz = 0
        self.GLSVert = 0

        self.XPDR_Status = None
        self.XPDR_Reply = None
        self.XPDR_Code = None
        self.XPDR_Ident = None



        self.msg_count = 0
        self.msg_last = ""


# vi: modeline tabstop=8 expandtab shiftwidth=4 softtabstop=4 syntax=python
