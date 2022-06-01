#!/usr/bin/env python

#######################################################################################################################################
#######################################################################################################################################
# Shared globals objects
#

from lib import aircraft
from lib import smartdisplay

####################################
## Aircraft object
## All input data is stuffed into this aircraft object in a "standard format"
## Then aircraft object is passed on to different screens for displaying data.
aircraft = aircraft.Aircraft()


####################################
## Input objects
## Input objects take in external data, process it if needed then
## stuff the data into the aircraft object for the screens to use.
## Inputs can be from Serial, Files, wifi, etc...
CurrentInput = None
CurrentInput2 = None

####################################
## SmartDisplay Obect
## This is a helper object that knows the screen size and ratio.
## Makes it easier for screens to write data to the screen without having to 
## know all the details of the screen.
smartdisplay = smartdisplay.SmartDisplay()


####################################
## Screen Obect
## This is the current graphical screen object that is being displayed.
CurrentScreen = None


####################################
## Default flight log dir.
## default location where flight logs are saved. Can be overwritten in config file.
DefaultFlightLogDir = "/flightlog/"


# vi: modeline tabstop=8 expandtab shiftwidth=4 softtabstop=4 syntax=python

