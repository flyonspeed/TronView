#!/usr/bin/env python

#################################################
# Module: Hud Horizon
# Topher 2021.
# Created by Cecil Jones 

from lib.modules._module import Module
from lib import hud_graphics
from lib import hud_utils
from lib import smartdisplay
from lib import aircraft
import pygame
import math


class gcross(Module):
    # called only when object is first created.
    def __init__(self):
        Module.__init__(self)
        self.name = "HUD gcross"  # set name
        self.GunSight = 0

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

        self.GColor = (255, 200, 100)  # Gun Cross Color = Yellow

        #self.yBottomLineStart = height * 1.16 #
        #self.yTopLineEnd = height * 1.16
        self.y_center = height / 2

        self.x_center = width / 2

        self.showLDMax = True
        self.yLDMaxDots = height - (height/8)
        self.xLDMaxDotsFromCenter = width/2

        self.GColor_color = (255, 250, 10)  # Gun Cross Color = Yellow

    # called every redraw for the mod
    def draw(self, aircraft, smartdisplay, pos):

        self.surface.fill((0, 0, 0))  # clear surface

        x,y = pos
       
#  Test For Air_to_Air GunSight
         # Is GunSight Active?  self.vert_G > 0.1
         
        if self.GunSight == 1:
                aircraft.GunSight_string = 25
                pygame.draw.line(
                self.pygamescreen,
                self.GColor_color,
                (smartdisplay.x_center - 15, smartdisplay.y_center - 120), (smartdisplay.x_center + 15, smartdisplay.y_center - 120),
                4,
            )
                pygame.draw.line(
                self.pygamescreen,
                self.GColor_color,
                (smartdisplay.x_center, smartdisplay.y_center - 135), (smartdisplay.x_center, smartdisplay.y_center - 105),
                4,
            )
                pygame.draw.circle(
                self.pygamescreen,
                self.GColor_color,
                (
                    int(smartdisplay.x_center), 
                    int(smartdisplay.y_center - 60),
                ),
                8,
                0,
            )
                pygame.draw.circle(
                self.pygamescreen,
                self.GColor_color,
                (
                    int(smartdisplay.x_center), 
                    int(smartdisplay.y_center + 60),
                ),
                8,
                0,
            )
                pygame.draw.lines(
                self.pygamescreen,
                self.GColor_color,
                False,
                [[smartdisplay.x_center - 321, smartdisplay.y_center - 120], [smartdisplay.x_center - 160, smartdisplay.y_center - 60],
                [smartdisplay.x_center - 107, smartdisplay.y_center], [smartdisplay.x_center - 80, smartdisplay.y_center + 60], 
                [smartdisplay.x_center - 53, smartdisplay.y_center + 120], [smartdisplay.x_center - 40, smartdisplay.y_center + 180]],
                4,
            )
                pygame.draw.lines(
                self.pygamescreen,
                self.GColor_color,
                False,
                [[smartdisplay.x_center + 321, smartdisplay.y_center - 120], [smartdisplay.x_center + 160, smartdisplay.y_center - 60],
                [smartdisplay.x_center + 107, smartdisplay.y_center], [smartdisplay.x_center + 80, smartdisplay.y_center + 60], 
                [smartdisplay.x_center + 53, smartdisplay.y_center + 120], [smartdisplay.x_center + 40, smartdisplay.y_center + 180]],
                4,
            )

        if self.GunSight == 2:
                aircraft.GunSight_string = 30
                pygame.draw.line(
                self.pygamescreen,
                self.GColor_color,
                (smartdisplay.x_center - 15, smartdisplay.y_center - 120), (smartdisplay.x_center + 15, smartdisplay.y_center - 120),
                4,
            )
                pygame.draw.line(
                self.pygamescreen,
                self.GColor_color,
                (smartdisplay.x_center, smartdisplay.y_center - 135), (smartdisplay.x_center, smartdisplay.y_center - 105),
                4,
            )
                pygame.draw.circle(
                self.pygamescreen,
                self.GColor_color,
                (
                    int(smartdisplay.x_center), 
                    int(smartdisplay.y_center - 60),
                ),
                8,
                0,
            )
                pygame.draw.circle(
                self.pygamescreen,
                self.GColor_color,
                (
                    int(smartdisplay.x_center), 
                    int(smartdisplay.y_center + 60),
                ),
                8,
                0,
            )
                pygame.draw.lines(
                self.pygamescreen,
                self.GColor_color,
                False,
                [[smartdisplay.x_center - 385, smartdisplay.y_center - 120], [smartdisplay.x_center - 193, smartdisplay.y_center - 60],
                [smartdisplay.x_center - 128, smartdisplay.y_center], [smartdisplay.x_center - 96, smartdisplay.y_center + 60], 
                [smartdisplay.x_center - 64, smartdisplay.y_center + 120], [smartdisplay.x_center - 48, smartdisplay.y_center + 180]],
                4,
            )
                pygame.draw.lines(
                self.pygamescreen,
                self.GColor_color,
                False,
                [[smartdisplay.x_center + 385, smartdisplay.y_center - 120], [smartdisplay.x_center + 193, smartdisplay.y_center - 60],
                [smartdisplay.x_center + 128, smartdisplay.y_center], [smartdisplay.x_center + 96, smartdisplay.y_center + 60], 
                [smartdisplay.x_center + 64, smartdisplay.y_center + 120], [smartdisplay.x_center + 48, smartdisplay.y_center + 180]],
                4,
            )

        if self.GunSight == 3:
                aircraft.GunSight_string = 35
                pygame.draw.line(
                self.pygamescreen,
                self.GColor_color,
                (smartdisplay.x_center - 15, smartdisplay.y_center - 120), (smartdisplay.x_center + 15, smartdisplay.y_center - 120),
                4,
            )
                pygame.draw.line(
                self.pygamescreen,
                self.GColor_color,
                (smartdisplay.x_center, smartdisplay.y_center - 135), (smartdisplay.x_center, smartdisplay.y_center - 105),
                4,
            )
                pygame.draw.circle(
                self.pygamescreen,
                self.GColor_color,
                (
                    int(smartdisplay.x_center), 
                    int(smartdisplay.y_center - 60),
                ),
                8,
                0,
            )
                pygame.draw.circle(
                self.pygamescreen,
                self.GColor_color,
                (
                    int(smartdisplay.x_center), 
                    int(smartdisplay.y_center + 60),
                ),
                8,
                0,
            )
                pygame.draw.lines(
                self.pygamescreen,
                self.GColor_color,
                False,
                [[smartdisplay.x_center - 449, smartdisplay.y_center - 120], [smartdisplay.x_center - 225, smartdisplay.y_center - 60],
                [smartdisplay.x_center - 150, smartdisplay.y_center], [smartdisplay.x_center - 112, smartdisplay.y_center + 60], 
                [smartdisplay.x_center - 75, smartdisplay.y_center + 120], [smartdisplay.x_center - 56, smartdisplay.y_center + 180]],
                4,
            )
                pygame.draw.lines(
                self.pygamescreen,
                self.GColor_color,
                False,
                [[smartdisplay.x_center + 449, smartdisplay.y_center - 120], [smartdisplay.x_center + 225, smartdisplay.y_center - 60],
                [smartdisplay.x_center + 150, smartdisplay.y_center], [smartdisplay.x_center + 112, smartdisplay.y_center + 60], 
                [smartdisplay.x_center + 75, smartdisplay.y_center + 120], [smartdisplay.x_center + 56, smartdisplay.y_center + 180]],
                4,
            )

            # Gun Cross Funnel
            # End Test Graphics        


    # cycle through the modes.
    def cycleGunSight(self):
        self.GunSight = self.GunSight + 1
        if (self.GunSight > 3):
	        self.GunSight = 0

    # called before screen draw.  To clear the screen to your favorite color.
    def clear(self):
        #self.ahrs_bg.fill((0, 0, 0))  # clear screen
        print("clear")

    # handle key events
    def processEvent(self, event):
        print("processEvent")


# vi: modeline tabstop=8 expandtab shiftwidth=4 softtabstop=4 syntax=python
