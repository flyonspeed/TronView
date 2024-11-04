#!/usr/bin/env python

#################################################
# Module: CDI for Localizer Glideslope
# Supported by Topher 2021.
# Created by Cecil Jones 

from lib.modules._module import Module
from lib import hud_graphics
from lib import hud_utils
from lib import smartdisplay
from lib.common.dataship import dataship
import pygame  
import math


class cdi(Module):
    # called only when object is first created.
    def __init__(self):
        Module.__init__(self)
        self.name = "HUD CDI"  # set name

    # called once for setup
    def initMod(self, pygamescreen, width = None, height = None):
        if width is None:
            width = 200 # default width
        if height is None:
            height = 200 # default height
        Module.initMod(
            self, pygamescreen, width, height
        )  # call parent init screen.
        print(("Init Mod: %s %dx%d"%(self.name,self.width,self.height)))

        # fonts
        self.font = pygame.font.SysFont(
            None, int(self.height / 20)
        )
        self.surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)

        self.MainColor = (255, 255, 255)  # CDI Needles color = White 

        self.yCenter = self.height / 2
        self.xCenter = self.width / 2

        self.showLDMax = True
        self.yLDMaxDots = self.height - (self.height/8)
        self.xLDMaxDotsFromCenter = self.width/2

        self.cdi_color = (255, 255, 255)  # start with white.
        # pull water line offset from HUD config area.
        self.y_offset = hud_utils.readConfigInt("HUD", "Horizon_Offset", 0)  #  Horizon/Waterline Pixel Offset from HUD Center Neg Numb moves Up, Default=0



    # called every redraw for the mod
    def draw(self, aircraft, smartdisplay, pos):

        self.surface.fill((0, 0, 0, 0))  # clear surface

        x,y = pos
        
        new_y_center = self.yCenter + self.y_offset
         
        if aircraft.nav.HSISource == 1:
            pygame.draw.line(
                self.surface,
                self.cdi_color,
                (self.xCenter - (aircraft.nav.ILSDev / 60), new_y_center - 67),
                (self.xCenter - (aircraft.nav.ILSDev / 60), new_y_center - 8),
                4,
            )
            pygame.draw.line(
                self.surface,
                self.cdi_color,        
                (self.xCenter - (aircraft.nav.ILSDev / 60), new_y_center + 8),
                (self.xCenter - (aircraft.nav.ILSDev / 60), new_y_center + 67),
                4,
            )
                     
        if aircraft.nav.VNAVSource == 1:
            pygame.draw.line(
                self.surface,
                self.cdi_color,
                (self.xCenter-70, (aircraft.nav.GSDev / 60) + new_y_center),
                (self.xCenter-8, (aircraft.nav.GSDev / 60) + new_y_center),
                4,                              
            ) 
            pygame.draw.line(
                self.surface,
                self.cdi_color,
                (self.xCenter+8, (aircraft.nav.GSDev / 60) + new_y_center),
                (self.xCenter+70, (aircraft.nav.GSDev / 60) + new_y_center),
                4,                              
            )

        # Draw the surface at the given position
        self.pygamescreen.blit(self.surface, pos)

    # cycle through NAV sources
    def cycleNavSource(self,aircraft):
        if aircraft.nav.HSISource == 0 and aircraft.nav.VNAVSource == 0:
            aircraft.nav.HSISource = 1
            aircraft.nav.SourceDesc = "Localizer"
        elif aircraft.nav.HSISource == 1 and aircraft.nav.VNAVSource == 0:
            aircraft.nav.VNAVSource = 1
            aircraft.nav.SourceDesc = "ILS"
        else:
            aircraft.nav.HSISource = 0
            aircraft.nav.VNAVSource = 0
            aircraft.nav.SourceDesc = ""


    # called before screen draw.  To clear the screen to your favorite color.
    def clear(self):
        #self.ahrs_bg.fill((0, 0, 0))  # clear screen
        print("clear")

    # handle key events
    def processEvent(self, event):
        print("processEvent")
    
    def get_module_options(self):
        return {
            "cdi_color": {
                "type": "color",
                "default": self.cdi_color,
                "label": "CDI Color",
                "description": "Color of the CDI needles.",
            }
        }


# vi: modeline tabstop=8 expandtab shiftwidth=4 softtabstop=4 syntax=python
