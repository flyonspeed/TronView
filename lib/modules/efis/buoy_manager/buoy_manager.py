#!/usr/bin/env python

#################################################
# Module: Buoy Manager
# Topher 2024
# 2/9/2025 - added dataship refactor.
from lib.modules._module import Module
from lib import hud_graphics
from lib import hud_utils
from lib import smartdisplay
from lib.common.dataship.dataship import Dataship
from lib.common.dataship.dataship_targets import TargetData, Target
from lib.common.dataship.dataship_gps import GPSData
import pygame
import math
from lib.common import shared


class buoy_manager(Module):
    # called only when object is first created.
    def __init__(self):
        Module.__init__(self)
        self.name = "Buoy Manager"  # set name
        self.buoyDistance = 10
        self.buoyAlt = 0 # altitude above or below aircraft
        self.targetData = TargetData()
        self.gpsData = GPSData()

    # called once for setup, or when module is being resized in editor
    def initMod(self, pygamescreen, width=None, height=None):
        if width is None:
            width = 360 # default width
        if height is None:
            height = 250 # default height
        Module.initMod( self, pygamescreen, width, height )  # call parent init screen.
        if shared.Dataship.debug_mode > 0:
            print(("Init Mod: %s %dx%d"%(self.name,self.width,self.height)))

        self.buttonsInit()
        # Create a surface with per-pixel alpha
        self.surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)

        # create buttons
        self.buttonAdd("addBuoy", "Add Buoy", self.addBuoy)
        self.buttonAdd("Label_dist", "Set Distance:", newRow=True, type="label")
        self.buttonAdd("setDistance_1",  "1", self.setDistance, newRow=True)
        self.buttonAdd("setDistance_2",  "2", self.setDistance)
        self.buttonAdd("setDistance_3",  "3", self.setDistance)
        self.buttonAdd("setDistance_5",  "5", self.setDistance)
        self.buttonAdd("setDistance_10", "10", self.setDistance)
        self.buttonAdd("setDistance_20", "20", self.setDistance)
        self.buttonAdd("setDistance_30", "30", self.setDistance)
        self.buttonAdd("setDistance_40", "40", self.setDistance)
        self.buttonAdd("setDistance_50", "50", self.setDistance)
        self.buttonSelected("setDistance_"+str(self.buoyDistance)) # set the button to selected that matches the distance

        # set altitude buttons
        self.buttonAdd("Label_alt", "Set Altitude:", newRow=True, type="label")
        self.buttonAdd("setAlt_-2000", "-2000", self.setAlt, newRow=True)
        self.buttonAdd("setAlt_-1000", "-1000", self.setAlt)
        self.buttonAdd("setAlt_-500", "-500", self.setAlt)
        self.buttonAdd("setAlt_-100", "-100", self.setAlt)
        self.buttonAdd("setAlt_0", "0", self.setAlt)
        self.buttonAdd("setAlt_100", "100", self.setAlt, newRow=True)
        self.buttonAdd("setAlt_500", "500", self.setAlt)
        self.buttonAdd("setAlt_1000", "1000", self.setAlt)
        self.buttonAdd("setAlt_2000", "2000", self.setAlt)
        self.buttonSelected("setAlt_"+str(self.buoyAlt)) # set the button to selected that matches the altitude

        # get the gpsData object from the shared object
        self.gpsData = GPSData()
        if len(shared.Dataship.gpsData) > 0:
            self.gpsData = shared.Dataship.gpsData[0]
        # get the targetData object from the shared object
        self.targetData = TargetData()
        if len(shared.Dataship.targetData) > 0:
            self.targetData = shared.Dataship.targetData[0]

    # called every redraw for the module
    def draw(self, dataship: Dataship, smartdisplay, pos=(0, 0)):
        # Clear the surface with full transparency
        self.surface.fill((0, 0, 0, 0))
        self.buttonsDraw(dataship, smartdisplay, pos)  # draw buttons

        # draw text at the bottom of the module (use the button font from the parent class)
        text = self.button_font.render("Buoys: "+str(self.targetData.buoyCount), True, (200,200,200))
        self.surface.blit(text, (10, self.buttonLastY + 10))

        # Use alpha blending when blitting to the screen
        self.pygamescreen.blit(self.surface, pos, special_flags=pygame.BLEND_ALPHA_SDL2)


    # handle mouse clicks
    def processClick(self, aircraft: Dataship, mx, my):
        self.buttonsCheckClick(aircraft, mx, my) # call parent.

    # add a buoy (called by self.buttonsCheckClick)
    def addBuoy(self,dataship:Dataship,button):
        print("adding buoy at distance ", self.buoyDistance, " and altitude ", self.buoyAlt)
        self.targetData.dropTargetBuoy(dataship,distance=self.buoyDistance,direction="ahead",alt=self.buoyAlt)

    # set the distance to drop the buoy (called by self.buttonsCheckClick)
    def setDistance(self,dataship:Dataship,button):
        #print("setDistance clicked")
        # unselect all buttons that start with setDistance_
        for b in self.buttons:
            if b["id"].startswith("setDistance_"):
                b["selected"] = False
        # select the button that was clicked
        button["selected"] = True
        self.buoyDistance = int(button["text"])

    # set the altitude to drop the buoy (called by self.buttonsCheckClick)
    def setAlt(self,dataship:Dataship,button):
        #print("setAlt clicked")
        # unselect all buttons that start with setAlt_
        for b in self.buttons:
            if b["id"].startswith("setAlt_"):
                b["selected"] = False
        # select the button that was clicked
        button["selected"] = True
        self.buoyAlt = int(button["text"])

    # return a dict of objects that are used to configure the module.
    def get_module_options(self):
        # each item in the dict represents a configuration option.  These are variable in this class that are exposed to the user to edit.
        return {
            "button_font_size": {
                "type": "int",
                "default": self.button_font_size,
                "min": 10,
                "max": 100,
                "label": "Button Font Size",
                "description": "Font size for buttons",
                "post_change_function": "fontSizeChanged"
            },
            "buoyDistance": {  # This is here so it will get saved to the screen file.  But we don't want to show it in the options bar.
                "type": "int",
                "default": self.buoyDistance,
                "min": 1,
                "max": 50,
                "label": "Buoy Distance",
                "description": "Distance to drop the buoy",
                "hidden": True
            },
            "buoyAlt": {     # This is here so it will get saved to the screen file.
                "type": "int",
                "default": self.buoyAlt,
                "min": -2000,
                "max": 2000,
                "label": "Buoy Altitude",
                "description": "Altitude to drop the buoy",
                "hidden": True
            }
        }

    def fontSizeChanged(self):
        self.initMod(self.pygamescreen, self.width, self.height)


# vi: modeline tabstop=8 expandtab shiftwidth=4 softtabstop=4 syntax=python
