#!/usr/bin/env python

#################################################
# Module: SlipSkid
# Topher 2021.
# Adapted from F18 HUD Screen code by Brian Chesteen.
# reads data in from aircraft object slip data. -100 to 100.  Postive is to the left.

from lib.modules._module import Module
from lib import hud_graphics
from lib import hud_utils
from lib import smartdisplay
from lib import aircraft
import pygame
import math


class slipskid(Module):
    # called only when object is first created.
    def __init__(self):
        Module.__init__(self)
        self.name = "Slip Skid"  # set name

        self.x_offset = 0

    # called once for setup
    def initMod(self, pygamescreen, width=None, height=None):
        if width is None:
            width = 400 # default width
        if height is None:
            height = 80 # default height
        Module.initMod(
            self, pygamescreen, width, height
        )  # call parent init screen.
        print(("Init Mod: %s %dx%d"%(self.name,self.width,self.height)))
        self.MainColor = (255, 255, 255)  # main color 
        self.BallColor = (255, 255, 255)  # ball color 

        self.xLineFromCenter = int(self.width / 8)
        self.BallSize = int(self.xLineFromCenter - 15)  # ball size 
        self.yLineHeight = self.height
        self.yCenterForBall = int(self.height /2)

    # called every redraw for the mod
    def draw(self, aircraft, smartdisplay, pos=(None,None)):

        if pos[0] is None:
            x = smartdisplay.x_center
        else:
            x = pos[0] + self.width / 2
        if pos[1] is None:
            y = smartdisplay.y_center
        else:
            y = pos[1] 

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

    # called before screen draw.  To clear the screen to your favorite color.
    def clear(self):
        #self.ahrs_bg.fill((0, 0, 0))  # clear screen
        pass

    # handle key events
    def processEvent(self, event):
        pass

    def get_module_options(self):
        return {
            "MainColor": {
                "type": "color",
                "default": self.MainColor,
                "label": "Main Color",
                "description": "Color of the main line.",
            },
            "BallColor": {
                "type": "color",
                "default": self.BallColor,
                "label": "Ball Color",
                "description": "Color of the ball.",
            }
        }



# vi: modeline tabstop=8 expandtab shiftwidth=4 softtabstop=4 syntax=python
