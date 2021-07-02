#!/usr/bin/env python


from enum import Enum

#############################################
## Class: DrawPos
## different postions we can draw in.
##

class DrawPos(Enum):
    LEFT = 7
    LEFT_TOP = 8
    LEFT_MID = 9
    LEFT_MID_UP = 10
    LEFT_MID_DOWN = 11
    LEFT_BOTTOM = 12

    RIGHT = 30
    RIGHT_TOP = 31
    RIGHT_MID = 32
    RIGHT_MID_UP = 33
    RIGHT_MID_DOWN = 34
    RIGHT_BOTTOM = 35

    TOP = 50
    TOP_MID = 51
    TOP_RIGHT = 52

    BOTTOM = 70
    BOTTOM_MID = 71
    BOTTOM_RIGHT = 72

# vi: modeline tabstop=8 expandtab shiftwidth=4 softtabstop=4 syntax=python

