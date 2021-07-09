#!/usr/bin/env python

#################################################
# Module: Wind
# Topher 2021.
# Adapted from F18 HUD Screen code by Brian Chesteen.

from lib.modules._module import Module
from lib import hud_graphics
from lib import hud_utils
from lib import smartdisplay
from lib import aircraft
import pygame
import math


class Wind(Module):
    # called only when object is first created.
    def __init__(self):
        Module.__init__(self)
        self.name = "Wind"  # set name

        self.x_offset = 0

    # called once for setup
    def initMod(self, pygamescreen, width, height):
        Module.initMod(
            self, pygamescreen, width, height
        )  # call parent init screen.
        print(("Init Mod: %s %dx%d"%(self.name,self.width,self.height)))

        self.myfont = pygame.font.SysFont("monospace", 20, bold=False)  # 
        self.MainColor = (0, 255, 0)  # main color 

        self.arrow = pygame.image.load("lib/modules/hud/wind/arrow_g.png").convert()
        self.arrow.set_colorkey((255, 255, 255))
        self.arrow_scaled = pygame.transform.scale(self.arrow, (50, 50))


    # called every redraw for the mod
    def draw(self, aircraft, smartdisplay, pos):

        x,y = pos

        # Wind Speed
        if aircraft.wind_speed != None:
            label = self.myfont.render(
                "%dkt" % aircraft.wind_speed, 1, (255, 255, 0)
            )
            smartdisplay.pygamescreen.blit(label, (x, y + 80))
        else:
            label = self.myfont.render("--kt", 1, (255, 255, 0))
            smartdisplay.pygamescreen.blit(label, (x, y + 80))

        # Wind Dir
        if aircraft.wind_dir != None:
            label = self.myfont.render(
                "%d\xb0" % aircraft.wind_dir, 1, (255, 255, 0)
            )
            self.pygamescreen.blit(label, (x, y ))
        else:
            label = self.myfont.render("--\xb0", 1, (255, 255, 0))
            self.pygamescreen.blit(label, (x, y ))

        # draw the arrow.  first rotate it.
        if aircraft.norm_wind_dir != None:
                arrow_rotated = pygame.transform.rotate(
                    self.arrow_scaled, aircraft.norm_wind_dir
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


# vi: modeline tabstop=8 expandtab shiftwidth=4 softtabstop=4 syntax=python
