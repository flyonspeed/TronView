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


class AOA(Module):
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

    # called every redraw for the mod
    def draw(self, aircraft, smartdisplay, pos):

        self.surface.fill((0, 0, 0))  # clear surface

        x,y = pos

        # AOA Indicator
        if aircraft.aoa > 0:
            # circles.
            # hud_graphics.hud_draw_circle(
            #     smartdisplay.pygamescreen,
            #     self.MainColor,
            #     (x + 50, y + 70),
            #     3,
            #     1,
            # )
            hud_graphics.hud_draw_circle(
                self.pygamescreen,
                (255, 255, 255), 
                (x+20, y + 120), 
                5, 
                0,
            )
            hud_graphics.hud_draw_circle(
                self.pygamescreen, 
                (255, 255, 255), 
                (x+70, y + 120), 
                5, 
                0,
            )
            #draw center circle.
            hud_graphics.hud_draw_circle(
                self.pygamescreen, 
                ( 0, 155, 79), 
                (x+45, y + 70), 
                15, 
                8,
            )
            # draw bottom lines
            pygame.draw.line(
                self.pygamescreen,
                (241, 137, 12),
                (x+25, y + 140),
                (x+35, y + 87),
                8,
            )
            pygame.draw.line(
                self.pygamescreen,
                (241, 137, 12),
                (x+63, y + 140),
                (x+53, y + 87),
                8,
            )
            # draw top lines
            pygame.draw.line(
                self.pygamescreen,
                (210, 40, 49),
                (x+63, y ),
                (x+53, y + 53),
                8,
            )
            pygame.draw.line(
                self.pygamescreen,
                (210, 40, 49),
                (x+35, y + 53),
                (x+25, y ),
                8,
            )

            # set indicator bar color according to aoa value.
            if aircraft.aoa <= 40:
                aoa_color = (255, 255, 255)
            elif aircraft.aoa > 40 and aircraft.aoa <= 60:
                aoa_color = ( 0, 155, 79)
            elif aircraft.aoa > 60:
                aoa_color = (237, 28, 36)

            # draw indicator bar.
            if aircraft.aoa != None:
                # label = self.myfont.render("%d" % (aircraft.aoa), 1, (255, 255, 0))
                # self.pygamescreen.blit(label, (80, (self.heightCenter) - 160))
                pygame.draw.line(
                    self.pygamescreen,
                    aoa_color,
                    (x+23, y  + aircraft.aoa * 1.4),
                    (x+65, y  + aircraft.aoa * 1.4),
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
