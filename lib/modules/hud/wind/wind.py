#!/usr/bin/env python

#################################################
# Module: Wind
# Topher 2021.
# Adapted from F18 HUD Screen code by Brian Chesteen.
# 2/9/2025 - added dataship refactor.

from lib.modules._module import Module
from lib import hud_graphics
from lib import hud_utils
from lib import smartdisplay
from lib.common.dataship.dataship import Dataship
from lib.common.dataship.dataship_air import AirData
from lib.common import shared
import pygame
import math


class wind(Module):
    # called only when object is first created.
    def __init__(self):
        Module.__init__(self)
        self.name = "Wind"  # set name
        self.arrow_size = 50
        self.x_offset = 0
        self.y_offset = 0
        self.arrow_size = 50

        self.airData = AirData()

    # called once for setup
    def initMod(self, pygamescreen, width=None, height=None):
        if width is None:
            width = 60 # default width
        if height is None:
            height = 100 # default height
        Module.initMod(
            self, pygamescreen, width, height
        )  # call parent init screen.
        print(("Init Mod: %s %dx%d"%(self.name,self.width,self.height)))

        self.myfont = pygame.font.SysFont("monospace", 20, bold=True)  # 
        self.MainColor = (0, 255, 0)  # main color 

        self.arrow = pygame.image.load("lib/modules/hud/wind/arrow_g.bmp").convert()
        self.arrow.set_colorkey((255, 255, 255))
        self.arrow_scaled = pygame.transform.scale(self.arrow, (50, 50))
        self.update_arrow_size()
        
        # get the airData object from the shared object
        self.airData = AirData()
        if len(shared.Dataship.airData) > 0:
            self.airData = shared.Dataship.airData[0]

    # called every redraw for the mod
    def draw(self, dataship:Dataship, smartdisplay, pos):

        x,y = pos

        # Wind Speed
        if self.airData.Wind_speed != None:
            label = self.myfont.render(
                "%dkt" % self.airData.Wind_speed, 1, (255, 255, 0)
            )
            self.pygamescreen.blit(label, (x, y + 80))
        else:
            label = self.myfont.render("--kt", 1, (255, 255, 0))
            self.pygamescreen.blit(label, (x, y + 80))

        # Wind Dir
        if self.airData.Wind_dir != None:
            label = self.myfont.render(
                "%d\xb0" % self.airData.Wind_dir, 1, (255, 255, 0)
            )
            self.pygamescreen.blit(label, (x, y ))
        else:
            label = self.myfont.render("--\xb0", 1, (255, 255, 0))
            self.pygamescreen.blit(label, (x, y ))

        # draw the arrow.  first rotate it.
        if self.airData.Wind_dir != None:
                arrow_rotated = pygame.transform.rotate(
                    self.arrow_scaled, self.airData.Wind_dir
                )
                arrow_rect = arrow_rotated.get_rect()
                self.pygamescreen.blit(
                    arrow_rotated,
                    (
                        x + 20 - arrow_rect.center[0],
                        (y + 50) - arrow_rect.center[1],
                    ),
                )


    # called before screen draw.  To clear the screen to your favorite color.
    def clear(self):
        #self.ahrs_bg.fill((0, 0, 0))  # clear screen
        print("clear")

    # handle key events
    def processEvent(self, event):
        print("processEvent")
    
    def get_module_options(self):
        return {
            "arrow_size": {
                "type": "int",
                "default": self.arrow_size,
                "min": 10,
                "max": 150,
                "label": "Arrow Size",
                "description": "Size of the arrow.",
                "post_change_function": "update_arrow_size"
            }
        }
    
    def update_arrow_size(self):
        self.arrow_scaled = pygame.transform.scale(
            self.arrow, (self.arrow_size, self.arrow_size)
        )
        self.arrow_scaled_rect = self.arrow_scaled.get_rect()



# vi: modeline tabstop=8 expandtab shiftwidth=4 softtabstop=4 syntax=python
