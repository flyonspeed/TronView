#!/usr/bin/env python

from enum import Enum
import inspect
from typing import List, Any
import time

#############################################
## Class: Analog Input Data 
class AnalogData(object):
    def __init__(self):
        self.inputSrcName = None
        self.inputSrcNum = None

        self.Name = None
        self.Num = 0
        self.Min = None
        self.Max = None
        self.Data = [0,0,0,0,0,0,0,0]

    def setup(self, name, num, min, max):
        self.Name = name
        self.Num = num
        self.Min = min
        self.Max = max
        # create self.Data list with size of num
        self.Data = [0] * num



# vi: modeline tabstop=8 expandtab shiftwidth=4 softtabstop=4 syntax=python
