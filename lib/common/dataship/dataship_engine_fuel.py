#!/usr/bin/env python

from enum import Enum
import inspect
from typing import List, Any
import time

#############################################
## Class: EngineData
class EngineData(object):
    def __init__(self):
        self.inputSrcName = None
        self.inputSrcNum = None

        self.NumberOfCylinders = 0
        self.RPM = 0
        self.ManPress = 0   # manifold pressure in PSI
        self.OilPress = 0   # oil pressure in PSI
        self.OilPress2 = 0  # oil pressure in PSI
        self.OilTemp = 0    # oil temperature in F
        self.OilTemp2 = 0    # oil temperature in F
        self.CoolantTemp = 0 # coolant temperature in F
        self.FuelFlow = 0    # fuel flow in GPH
        self.FuelFlow2 = 0    # fuel flow in GPH
        self.FuelPress = 0    # fuel pressure in PSI
        self.EGT = [0,0,0,0,0,0,0,0] # EGT in F
        self.CHT = [0,0,0,0,0,0,0,0] # CHT in F

        self.volts1 = None
        self.volts2 = None
        self.amps = None

        self.hobbs_time = None
        self.tach_time = None


        self.msg_count = 0
        self.msg_last = ""

#############################################
## Class: FuelData
class FuelData(object):
    def __init__(self):

        self.FuelLevels = [0,0,0,0]

        self.FuelRemain = None

        self.msg_count = 0
        self.msg_last = ""


# vi: modeline tabstop=8 expandtab shiftwidth=4 softtabstop=4 syntax=python
