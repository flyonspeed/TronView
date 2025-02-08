#!/usr/bin/env python

#################################################
# Module: AOA
# Topher 2021.
# TRON 2024 Added Pilot AOA configuration array to support different AOA's and Aircraft
# Adapted from F18 HUD Screen code by Brian Chesteen.

from lib.modules._module import Module
from lib import hud_graphics
from lib import hud_utils
from lib import smartdisplay
from lib.common.dataship.dataship import Dataship
from lib.common.dataship.dataship_imu import IMUData
from lib.common.dataship.dataship_air import AirData
import pygame
import math
import numpy as np
from lib.common import shared

class aoa(Module):
    # called only when object is first created.
    def __init__(self):
        Module.__init__(self)
        self.name = "HUD AOA"  # set name
        
     # called every redraw to adjust G3x AOA display using OnSpeed Profile
     # must adjust this array as needed for each Aircraft & AOA device
    def adjust_aoa(self, aoa_value):
        input_values = np.array([0, 50, 55, 60, 68, 79, 90, 99])
        output_values = np.array([0, 25, 39, 50, 59, 75, 85, 99])
         
    # Interpolate to find the output value for the given input
        adjusted_value = np.interp(aoa_value, input_values, output_values)
        return adjusted_value

    # called once for setup
    def initMod(self, pygamescreen, width=None, height=None):
        if width is None:
            width = 80 # default width
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
        self.surface = pygame.Surface((self.width, self.height))

        self.MainColor = (0, 255, 0)   

        self.centerCircleHeight = width / 3

        self.yBottomLineStart = height * 1.16 #
        self.yTopLineEnd = height * 1.16
        self.yCenter = height / 2

        self.xCenter = width / 2

        self.showLDMax = True
        self.yLDMaxDots = height - (height/8)
        self.xLDMaxDotsFromCenter = width/1.4

        self.aoa_color = (255, 255, 255)  # start with white.

        self.imuData = IMUData()
        self.airData = AirData()
        if len(shared.Dataship.imuData) > 0:
            self.imuData = shared.Dataship.imuData[0]
        if len(shared.Dataship.airData) > 0:
            self.airData = shared.Dataship.airData[0]

    # called every redraw for the mod
    def draw(self, dataship, smartdisplay, pos):
        self.surface.fill((0, 0, 0))  # clear surface
        x,y = pos

        # Get the current time in milliseconds
        current_time = pygame.time.get_ticks()      
        # Call above AOA array data to adjust display for changing aoa input
        adjusted_aoa = self.adjust_aoa(self.airData.AOA)
        
        # Define the flashing interval in milliseconds
        flash_interval = 500   # AOA Flash interval for dangerous AOA/stall condition
          
        # AOA Graphic Color changes per AOA input
        if self.airData.AOA is not None and self.airData.AOA > 89 and (current_time // flash_interval) % 2 == 0:
            hud_graphics.hud_draw_circle(
                self.pygamescreen, 
                (127, 127, 127), # color Gray
                (x+self.xCenter, y + self.yCenter), 
                int(self.centerCircleHeight), 
                5,
            )
            pygame.draw.line(  # draw bottom left line
                self.pygamescreen,
                ( 127, 127, 127), # color Gray
                (x+ (self.xCenter) - 10, y + self.yCenter + self.centerCircleHeight),
                (x, y + self.height),
                8,
            )
            pygame.draw.line(  # draw bottom right line.
                self.pygamescreen,
                ( 127, 127, 127), # color Gray
                (x+(self.xCenter) + 8, y + self.yCenter + self.centerCircleHeight),
                (x+self.width, y + self.height),
                8,
            )
            pygame.draw.line( # draw upper right line.
                self.pygamescreen,
                (255, 0, 0),  # colorRed
                (x+self.width, y ),
                (x+ (self.xCenter) + 10, y + self.yCenter - self.centerCircleHeight),
                8,
            )
            pygame.draw.line( # draw upper left line
                self.pygamescreen,
                (255, 0, 0),  # color Red
                (x+ (self.xCenter) - 10, y + self.yCenter - self.centerCircleHeight),
                (x, y ),
                8,
            )
        elif self.airData.AOA is not None and self.airData.AOA > 68 and self.airData.AOA <= 89:
            hud_graphics.hud_draw_circle(
                self.pygamescreen, 
                ( 127, 127, 127), # color Gray
                (x+self.xCenter, y + self.yCenter), 
                int(self.centerCircleHeight), 
                5,
            )
            pygame.draw.line(  # draw bottom left line
                self.pygamescreen,
                ( 127, 127, 127), # color Gray
                (x+ (self.xCenter) - 10, y + self.yCenter + self.centerCircleHeight),
                (x, y + self.height),
                8,
            )
            pygame.draw.line(  # draw bottom right line.
                self.pygamescreen,
                ( 127, 127, 127), # color Gray
                (x+(self.xCenter) + 8, y + self.yCenter + self.centerCircleHeight),
                (x+self.width, y + self.height),
                8,
            )
            pygame.draw.line( # draw upper right line.
                self.pygamescreen,
                (255, 255, 0),  # color Yellow
                (x+self.width, y ),
                (x+ (self.xCenter) + 10, y + self.yCenter - self.centerCircleHeight),
                8,
            )
            pygame.draw.line( # draw upper left line
                self.pygamescreen,
                (255, 255, 0),  # color Yellow
                (x+ (self.xCenter) - 10, y + self.yCenter - self.centerCircleHeight),
                (x, y ),
                8,
            )
        elif self.airData.AOA is not None and self.airData.AOA > 63 and self.airData.AOA <= 68:
            hud_graphics.hud_draw_circle(
                self.pygamescreen, 
                ( 0, 176, 80), # color Green
                (x+self.xCenter, y + self.yCenter), 
                int(self.centerCircleHeight), 
                5,
            )
            pygame.draw.line(  # draw bottom left line
                self.pygamescreen,
                ( 127, 127, 127), # color Gray
                (x+ (self.xCenter) - 10, y + self.yCenter + self.centerCircleHeight),
                (x, y + self.height),
                8,
            )
            pygame.draw.line(  # draw bottom right line.
                self.pygamescreen,
                ( 127, 127, 127), # color Gray
                (x+(self.xCenter) + 8, y + self.yCenter + self.centerCircleHeight),
                (x+self.width, y + self.height),
                8,
            )
            pygame.draw.line( # draw upper right line.
                self.pygamescreen,
                (255, 255, 0),  # color Yellow
                (x+self.width, y ), # start drawing top
                (x+ (self.xCenter) + 10, y + self.yCenter - self.centerCircleHeight),
                8,
            )
            pygame.draw.line( # draw upper left line
                self.pygamescreen,
                (255, 255, 0),  # color Yellow
                (x+ (self.xCenter) - 10, y + self.yCenter - self.centerCircleHeight),
                (x, y ),
                8,
            )
        elif self.airData.AOA is not None and self.airData.AOA > 54 and self.airData.AOA <= 62:
            hud_graphics.hud_draw_circle(
                self.pygamescreen, 
                ( 0, 176, 80), # color Green
                (x+self.xCenter, y + self.yCenter), 
                int(self.centerCircleHeight), 
                5,
            )
            pygame.draw.line(  # draw bottom left line
                self.pygamescreen,
                ( 0,176, 240),  # color blue
                (x+ (self.xCenter) - 10, y + self.yCenter + self.centerCircleHeight),
                (x, y + self.height),
                8,
            )
            pygame.draw.line(  # draw bottom right line.
                self.pygamescreen,
                ( 0,176, 240),  # color blue
                (x+(self.xCenter) + 8, y + self.yCenter + self.centerCircleHeight),
                (x+self.width, y + self.height),
                8,
            )
            pygame.draw.line( # draw upper right line.
                self.pygamescreen,
                (127, 127, 127),  # color gray
                (x+self.width, y ), # start drawing top
                (x+ (self.xCenter) + 10, y + self.yCenter - self.centerCircleHeight),
                8,
            )
            pygame.draw.line( # draw upper left line
                self.pygamescreen,
                (127, 127, 127),  # color gray
                (x+ (self.xCenter) - 10, y + self.yCenter - self.centerCircleHeight),
                (x, y ),
                8,
            )
        elif self.airData.AOA is not None and self.airData.AOA > 49 and self.airData.AOA <=54:
            hud_graphics.hud_draw_circle(
                self.pygamescreen, 
                (127, 127, 127), # color gray
                (x+self.xCenter, y + self.yCenter), 
                int(self.centerCircleHeight),
                5,
            )
            pygame.draw.line(  # draw bottom left line
                self.pygamescreen,
                ( 0, 176, 240),  # color blue
                (x+ (self.xCenter) - 10, y + self.yCenter + self.centerCircleHeight),
                (x, y + self.height),
                8,
            )
            pygame.draw.line(  # draw bottom right line.
                self.pygamescreen,
                ( 0, 176, 240),  # color blue
                (x+(self.xCenter) + 8, y + self.yCenter + self.centerCircleHeight),
                (x+self.width, y + self.height),
                8,
            )
            pygame.draw.line( # draw upper right line.
                self.pygamescreen,
                (127, 127, 127),  # color gray
                (x+self.width, y ), # start drawing top
                (x+ (self.xCenter) + 10, y + self.yCenter - self.centerCircleHeight),
                8,
            )
            pygame.draw.line( # draw upper left line
                self.pygamescreen,
                (127, 127, 127),  # color gray
                (x+ (self.xCenter) - 10, y + self.yCenter - self.centerCircleHeight),
                (x, y ),
                8,
            )
        elif self.airData.AOA is not None and self.airData.AOA > 0:
            hud_graphics.hud_draw_circle(    #draw center circle. 
                self.pygamescreen, 
                (127, 127, 127), # color gray
                (x+self.xCenter, y + self.yCenter), 
                int(self.centerCircleHeight), 
                5,
            )
            # draw bottom lines 
            pygame.draw.line(  # draw bottom left line
                self.pygamescreen,
                (127, 127, 127),  # color gray
                (x+ (self.xCenter) - 10, y + self.yCenter + self.centerCircleHeight),
                (x, y + self.height),
                8,
            )
            pygame.draw.line(  # draw bottom right line.
                self.pygamescreen,
                (127, 127, 127),  # color gray
                (x+(self.xCenter) + 8, y + self.yCenter + self.centerCircleHeight),
                (x+self.width, y + self.height),
                8,
            )
            pygame.draw.line( # draw upper right line.
                self.pygamescreen,
                (127, 127, 127),  # color gray
                (x+self.width, y ), 
                (x+ (self.xCenter) + 10, y + self.yCenter - self.centerCircleHeight),
                8,
            )
            pygame.draw.line( # draw upper left line
                self.pygamescreen,
                (127, 127, 127),  # color gray
                (x+ (self.xCenter) - 10, y + self.yCenter - self.centerCircleHeight),
                (x, y ),
                8,
            )

      #-------------------------------------------------
        if self.airData.AOA is not None and self.airData.AOA > 0:  #if self.showLDMax == True:if aircraft.aoa != None and aircraft.aoa > 0:
              # white circles L/D Max Dots. (Carson's Number)
            hud_graphics.hud_draw_circle(
                self.pygamescreen,
                (255, 255, 255), 
                (x+self.xCenter-self.xLDMaxDotsFromCenter, y - 16 + self.yLDMaxDots), 
                6, 
                0,
            )
            hud_graphics.hud_draw_circle(
                self.pygamescreen, 
                (255, 255, 255), 
                (x+self.xCenter+2+self.xLDMaxDotsFromCenter, y -16 + self.yLDMaxDots), 
                6, 
                0,
            )

        #-------------------------------
            #draw Solid Center DOT when OnSpeed 
            if self.airData.AOA is not None and self.airData.AOA > 57 and self.airData.AOA <63:
                hud_graphics.hud_draw_circle(
                self.pygamescreen, 
                ( 0, 176, 80), # color Green
                (x+self.xCenter, y + self.yCenter), 
                int(self.centerCircleHeight-8), 
                0,
                )

            #  This function draws AOA indicator bar.

        if self.airData.AOA is not None and self.airData.AOA > 0:
            pygame.draw.line(
                self.pygamescreen,
                self.aoa_color,
                (x-12, y + ((100-adjusted_aoa) * 0.01) * self.height),
                (x+12+self.width, y + ((100-adjusted_aoa) * 0.01) * self.height),
                5,
            )

    # called before screen draw.  To clear the screen to your favorite color.
    def clear(self):
        #self.ahrs_bg.fill((0, 0, 0))  # clear screen
        print("clear")

    # handle key events
    def processEvent(self, event):
        print("processEvent")

    # return a dict of objects that are used to configure the module.
    def get_module_options(self):

        # each item in the dict represents a configuration option.  These are variable in this class that are exposed to the user to edit.
        
        return {
            "showLDMax": {
                "type": "bool",
                "default": False,
                "label": "Show LD/Max",
                "description": "LD/Max is Carson's Number"
            },
            "aoa_color": {
                "type": "color",
                "default": (255, 255, 255),
                "label": "AOA Color",
                "description": "The color of the AOA indicator."
            }
        }

# vi: modeline tabstop=8 expandtab shiftwidth=4 softtabstop=4 syntax=python
