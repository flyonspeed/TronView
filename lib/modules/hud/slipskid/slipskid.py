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
from lib.common.dataship.dataship import Dataship
from lib.common.dataship.dataship_imu import IMUData
from lib.common.dataship.dataship_air import AirData
from lib.common import shared
import pygame
import math


class slipskid(Module):
    # called only when object is first created.
    def __init__(self):
        Module.__init__(self)
        self.name = "Slip Skid"  # set name

        self.x_offset = 0

        self.imuData = IMUData()
        self.airData = AirData()

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
        self.BallSize = int(self.height / 2.5)  # ball size 
        self.yLineHeight = self.height
        self.yCenterForBall = int(self.height / 2)

        self.imuData = IMUData()
        self.airData = AirData()
        if len(shared.Dataship.imuData) > 0:
            self.imuData = shared.Dataship.imuData[0]
        if len(shared.Dataship.airData) > 0:
            self.airData = shared.Dataship.airData[0]

    # called every redraw for the mod
    def draw(self, dataship:Dataship, smartdisplay, pos=(None,None)):

        if pos[0] is None:
            x = smartdisplay.x_center
        else:
            x = pos[0] + self.width / 2
        if pos[1] is None:
            y = smartdisplay.y_center
        else:
            y = pos[1] 

        # Slip/Skid Indicator
        if self.imuData.slip_skid != None:
            pygame.draw.circle(
                self.pygamescreen,
                self.BallColor,
                (
                    int(x + self.x_offset) - int(self.imuData.slip_skid * 150),
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
