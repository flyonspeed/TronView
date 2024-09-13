#!/usr/bin/env python

#################################################
# Module: AOA
# Topher 2021.
# Adapted from F18 HUD Screen code by Brian Chesteen.

from lib.modules._module import Module
from lib import hud_graphics
from lib import hud_utils
from lib import smartdisplay
from lib import aircraft
import pygame
import math


class aoa(Module):
    # called only when object is first created.
    def __init__(self):
        Module.__init__(self)
        self.name = "HUD AOA"  # set name

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

        self.MainColor = (0, 255, 0)  # main color 

        self.centerCircleHeight = width / 3

        self.yBottomLineStart = height * 1.16 #
        self.yTopLineEnd = height * 1.16
        self.yCenter = height / 2

        self.xCenter = width / 2

        self.showLDMax = True
        self.yLDMaxDots = height - (height/8)
        self.xLDMaxDotsFromCenter = width/2

        self.aoa_color = (255, 255, 255)  # start with white.

    # called every redraw for the mod
    def draw(self, aircraft, smartdisplay, pos):

        self.surface.fill((0, 0, 0))  # clear surface

        x,y = pos

        # AOA Indicator
        if aircraft.aoa != None and aircraft.aoa > 0:

            #draw center circle.
            hud_graphics.hud_draw_circle(
                self.pygamescreen, 
                ( 0, 155, 79), 
                (x+self.xCenter, y + self.yCenter), 
                int(self.centerCircleHeight), 
                8,
            )
            # draw bottom lines
            pygame.draw.line(  # draw bottom left line
                self.pygamescreen,
                (241, 137, 12),  # color orange
                (x+ (self.xCenter) - 10, y + self.yCenter + self.centerCircleHeight), #start drawing at the bottom.
                (x, y + self.height),
                8,
            )
            pygame.draw.line(  # draw bottom right line.
                self.pygamescreen,
                (241, 137, 12),
                (x+(self.xCenter) + 10, y + self.yCenter + self.centerCircleHeight), #start drawing at the bottom.
                (x+self.width, y + self.height),
                8,
            )
            # draw top lines
            pygame.draw.line( # draw top right line.
                self.pygamescreen,
                (210, 40, 49),  # color red
                (x+self.width, y ), # start drawing top
                (x+ (self.xCenter) + 10, y + self.yCenter - self.centerCircleHeight),
                8,
            )
            pygame.draw.line( # draw top left line
                self.pygamescreen,
                (210, 40, 49),
                (x+ (self.xCenter) - 10, y + self.yCenter - self.centerCircleHeight), # start drawing at the bottom
                (x, y ),
                8,
            )

            if self.showLDMax == True:
                # white circles L/D Max Dots. (Carson’s Number)
                hud_graphics.hud_draw_circle(
                    self.pygamescreen,
                    (255, 255, 255), 
                    (x+self.xCenter-self.xLDMaxDotsFromCenter, y + self.yLDMaxDots), 
                    7, 
                    0,
                )
                hud_graphics.hud_draw_circle(
                    self.pygamescreen, 
                    (255, 255, 255), 
                    (x+self.xCenter+self.xLDMaxDotsFromCenter, y + self.yLDMaxDots), 
                    7, 
                    0,
                )

            # set indicator bar color according to aoa value.
            if aircraft.aoa <= 40:
                self.aoa_color = (255, 255, 255)
            elif aircraft.aoa > 40 and aircraft.aoa <= 60:
                self.aoa_color = ( 0, 155, 79)
            elif aircraft.aoa > 60:
                self.aoa_color = (237, 28, 36)

            # draw indicator bar.
            if aircraft.aoa != None:
                # label = self.myfont.render("%d" % (aircraft.aoa), 1, (255, 255, 0))
                # self.pygamescreen.blit(label, (80, (self.heightCenter) - 160))
                pygame.draw.line(
                    self.pygamescreen,
                    self.aoa_color,
                    (x, y  + (aircraft.aoa * 0.01) * self.height),
                    (x+self.width, y  + (aircraft.aoa * 0.01) * self.height),
                    5,
                )

    # called before screen draw.  To clear the screen to your favorite color.
    def clear(self):
        #self.ahrs_bg.fill((0, 0, 0))  # clear screen
        print("clear")

    # handle key events
    def processEvent(self, event):
        print("processEvent")


# vi: modeline tabstop=8 expandtab shiftwidth=4 softtabstop=4 syntax=python
