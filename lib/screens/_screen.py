#!/usr/bin/env python

# HUD Screen praent class.
# All hud screens should inherit from this class.

from .. import hud_graphics
import pygame


class Screen:
    def __init__(self):
        self.name = "HUD Screen"
        self.screenVersion = 1.0
        self.width = 640
        self.height = 480
        self.pygamescreen = 0

    def initDisplay(self, pygamescreen, width, height):
        print("init screen parent")
        self.pygamescreen = pygamescreen
        self.width = width
        self.height = height
        self.widthCenter = width / 2
        self.heightCenter = height / 2

    def processEvent(self, event):
        print(("processing Event %s" % (event.key)))

    def draw(self, aircraft):
        print("parent")

        def clearScreen(self):
            print("Clear screen")


# vi: modeline tabstop=8 expandtab shiftwidth=4 softtabstop=4 syntax=python
