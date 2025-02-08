#!/usr/bin/env python

# Screen praent class.
# All screens should inherit from this class.

from .. import hud_graphics
import pygame


class Screen:
    def __init__(self):
        self.name = "Parent Screen"
        self.screenVersion = 1.0
        self.width = 640
        self.height = 480
        self.pygamescreen = 0
        self.debug = False
        self.show_FPS = False
        
    def initDisplay(self, pygamescreen, width, height):
        #print("init screen parent")
        self.pygamescreen = pygamescreen
        self.width = width
        self.height = height
        self.widthCenter = width / 2
        self.heightCenter = height / 2

        self.mode_traffic = 0
        self.mode_traffic_max = 3

    # set modes for screen.
    def setMode(self, modetype, mode):
        if(modetype=="traffic"):
            if(mode==-1): # cycle through modes
                self.mode_traffic += 1
            else:
                self.mode_traffic = mode # else set a exact mode value

            if(self.mode_traffic > self.mode_traffic_max): # if greater then max then reset to 0
                self.mode_traffic = 0

    def processEvent(self, event):
        print(("processing Event %s" % (event.key)))

    def draw(self, aircraft):
        print("parent")

    def clearScreen(self):
        print("Clear screen")


# vi: modeline tabstop=8 expandtab shiftwidth=4 softtabstop=4 syntax=python
