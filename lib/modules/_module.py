#!/usr/bin/env python

# module parent class.
# All modules should inherit from this class.

from .. import hud_graphics
import pygame


class Module:
    def __init__(self):
        self.name = "Module"
        self.moduleVersion = 1.0
        self.width = 640
        self.height = 480
        self.pygamescreen = 0

    def initMod(self, pygamescreen, width, height):
        print("init module parent")
        self.pygamescreen = pygamescreen
        self.width = width
        self.height = height
        self.widthCenter = width / 2
        self.heightCenter = height / 2

    def processEvent(self, event):
        print(("processing module Event %s" % (event.key)))

    def draw(self, aircraft, smartdisplay):
        print("module parent")

    def clear(self):
        print("Clear screen")


# vi: modeline tabstop=8 expandtab shiftwidth=4 softtabstop=4 syntax=python
