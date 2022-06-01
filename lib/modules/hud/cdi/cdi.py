#!/usr/bin/env python

#################################################
# Module: CDI for Localizer Glideslope
# Supported by Topher 2021.
# Created by Cecil Jones 

from lib.modules._module import Module
from lib import hud_graphics
from lib import hud_utils
from lib import smartdisplay
from lib import aircraft
import pygame  
import math


class cdi(Module):
    # called only when object is first created.
    def __init__(self):
        Module.__init__(self)
        self.name = "HUD CDI"  # set name

    # called once for setup
    def initMod(self, pygamescreen, width, height):
        Module.initMod(
            self, pygamescreen, width, height
        )  # call parent init screen.
        print(("Init Mod: %s %dx%d"%(self.name,self.width,self.height)))

        # fonts
        self.font = pygame.font.SysFont(
            None, int(self.height / 20)
        )
        self.surface = pygame.Surface((self.width, self.height))

        self.MainColor = (255, 255, 255)  # CDI Needles color = White 

        #self.yBottomLineStart = height * 1.16 #
        #self.yTopLineEnd = height * 1.16
        self.yCenter = height / 2

        self.xCenter = width / 2

        self.showLDMax = True
        self.yLDMaxDots = height - (height/8)
        self.xLDMaxDotsFromCenter = width/2

        self.cdi_color = (255, 255, 255)  # start with white.

    # called every redraw for the mod
    def draw(self, aircraft, smartdisplay, pos):

        self.surface.fill((0, 0, 0))  # clear surface

        x,y = pos
        
        
#  NAV Test Graphics for MGL
         # Is Glide Slope Active
         
        if aircraft.nav.HSISource == 1:
                pygame.draw.line(
                self.pygamescreen,
                self.cdi_color,
                (smartdisplay.x_center - (aircraft.nav.ILSDev / 60), smartdisplay.y_center - 67), (smartdisplay.x_center - (aircraft.nav.ILSDev / 60), smartdisplay.y_center - 8),
                4,
            )
                pygame.draw.line(
                self.pygamescreen,
                self.cdi_color,        
                (smartdisplay.x_center - (aircraft.nav.ILSDev / 60), smartdisplay.y_center + 8), (smartdisplay.x_center - (aircraft.nav.ILSDev / 60), smartdisplay.y_center + 67),
                4,
            )
                     
        if aircraft.nav.VNAVSource == 1:
                pygame.draw.line(
                self.pygamescreen,
                self.cdi_color,
                (smartdisplay.x_center-70,(aircraft.nav.GSDev / 60) + smartdisplay.y_center),(smartdisplay.x_center-8, (aircraft.nav.GSDev / 60) + smartdisplay.y_center),
                4,                              
              
            ) 
                pygame.draw.line(
                self.pygamescreen,
                self.cdi_color,
                (smartdisplay.x_center+8,(aircraft.nav.GSDev / 60) + smartdisplay.y_center),(smartdisplay.x_center+70, (aircraft.nav.GSDev / 60) + smartdisplay.y_center),
                4,                              
            )
            # Localizer 
            # End Test Graphics        



    # called before screen draw.  To clear the screen to your favorite color.
    def clear(self):
        #self.ahrs_bg.fill((0, 0, 0))  # clear screen
        print("clear")

    # handle key events
    def processEvent(self, event):
        print("processEvent")


# vi: modeline tabstop=8 expandtab shiftwidth=4 softtabstop=4 syntax=python
