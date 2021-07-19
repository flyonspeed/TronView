#!/usr/bin/env python

#################################################
# Module: SlipSkid
# Topher 2021.
# Adapted from F18 HUD Screen code by Brian Chesteen.

from lib.modules._module import Module
from lib import hud_graphics
from lib import hud_utils
from lib import smartdisplay
from lib import aircraft
import pygame
import math


class SlipSkid(Module):
    # called only when object is first created.
    def __init__(self):
        Module.__init__(self)
        self.name = "Slip Skid"  # set name

        self.x_offset = 0

    # called once for setup
    def initMod(self, pygamescreen, width, height):
        Module.initMod(
            self, pygamescreen, width, height
        )  # call parent init screen.
        print(("Init Mod: %s %dx%d"%(self.name,self.width,self.height)))
        self.MainColor = (255, 255, 255)  # main color 
        self.BallColor = (255, 255, 255)  # ball color 

        self.xLineFromCenter = self.width / 8
        self.BallSize = self.xLineFromCenter - 15  # ball size 
        self.yLineHeight = self.height
        self.yCenterForBall = int(self.height /2)

    # called every redraw for the mod
    def draw(self, aircraft, smartdisplay, pos):

        x,y = pos

        # Slip/Skid Indicator
        if aircraft.slip_skid != None:
            pygame.draw.circle(
                self.pygamescreen,
                self.BallColor,
                (
                    int(x + self.x_offset) - int(aircraft.slip_skid * 150),
                    y + self.yCenterForBall,
                ),
                self.BallSize,
                0,
            )
        pygame.draw.line(
            self.pygamescreen,
            self.MainColor,
            (x + self.xLineFromCenter + self.x_offset, y ),
            (x + self.xLineFromCenter + self.x_offset, y + self.yLineHeight),
            3,
        )
        pygame.draw.line(
            self.pygamescreen,
            self.MainColor,
            (x - self.xLineFromCenter + self.x_offset, y ),
            (x - self.xLineFromCenter + self.x_offset, y + self.yLineHeight),
            3,
        )
        # pygame.draw.line(
        #     self.pygamescreen,
        #     (0, 0, 0),
        #     (x + 61, y + 179),
        #     (x + 61, y + 201),
        #     1,
        # )
        # pygame.draw.line(
        #     self.pygamescreen,
        #     (0, 0, 0),
        #     (x + 65, y + 179),
        #     (x + 65, y + 201),
        #     1,
        # )
        # pygame.draw.line(
        #     self.pygamescreen,
        #     (0, 0, 0),
        #     (x + 39, y + 179),
        #     (x + 39, y + 201),
        #     1,
        # )
        # pygame.draw.line(
        #     self.pygamescreen,
        #     (0, 0, 0),
        #     (x + 35, y + 179),
        #     (x + 35, y + 201),
        #     1,
        # )

    # called before screen draw.  To clear the screen to your favorite color.
    def clear(self):
        #self.ahrs_bg.fill((0, 0, 0))  # clear screen
        pass

    # handle key events
    def processEvent(self, event):
        pass



# vi: modeline tabstop=8 expandtab shiftwidth=4 softtabstop=4 syntax=python
