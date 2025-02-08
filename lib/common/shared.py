#!/usr/bin/env python

#######################################################################################################################################
#######################################################################################################################################
# Shared globals objects
#

from lib.common.dataship import dataship
from lib import smartdisplay
from lib.common.graphic.growl_manager import GrowlManager
from lib.common.event_manager import EventManager

####################################
## DataShip object
## All input data is stuffed into this dataship object in a "standard format"
## Then dataship object is passed on to different screens for displaying data.
Dataship = dataship.Dataship()


####################################
## Input objects
## Input objects take in external data, process it if needed then
## stuff the data into the dataship object for the screens to use.
## Inputs can be from Serial, Files, wifi, etc...

Inputs = {}

####################################
## SmartDisplay Obect
## This is a helper object that knows the screen size and ratio.
## Makes it easier for screens to write data to the screen without having to 
## know all the details of the screen.
smartdisplay = smartdisplay.SmartDisplay()


####################################
## Screen Obect
## This is the current graphical screen object that is being displayed.
class Screen2d(object):
    def __init__(self):
        self.ScreenObjects = []
        self.show_FPS = False
CurrentScreen = Screen2d()


####################################
## Default flight log dir.
## default location where flight logs are saved. Can be overwritten in config file.
DefaultFlightLogDir = "./flightlog/"


####################################
## Default data dir.
## default location where data is saved. Can be overwritten in config file.
DataDir = "./data/"


####################################
## Change History
## This is a global object that is used to store the history of changes to the screen objects while in edit mode.
## This is used for the undo functionality.
Change_history = None

####################################
## Growl Manager
## This is a global object that is used to manage the growl messages.
GrowlManager = GrowlManager()

####################################
## Event Manager
## This is a global object that is used to manage events.
EventManager = EventManager()

# vi: modeline tabstop=8 expandtab shiftwidth=4 softtabstop=4 syntax=python

