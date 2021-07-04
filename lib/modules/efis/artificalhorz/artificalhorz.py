#!/usr/bin/env python

#################################################
# Module: Artifical horzion
# Topher 2021.

from lib.modules._module import Module
from lib import hud_graphics
from lib import hud_utils
from lib import smartdisplay
from lib import drawpos
import pygame


class ArtificalHorz(Module):
    # called only when object is first created.
    def __init__(self):
        Module.__init__(self)
        self.name = "ArtificalHorz"  # set name
        #self.imagefilename = "lib/modules/efis/artificalhorz/attitude-indicator-1280.png"
        self.imagefilename = "lib/modules/efis/artificalhorz/horiz.png"

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

        self.background = pygame.image.load(self.imagefilename).convert()
        ##self.background.set_colorkey((255, 255, 255))
        #self.background = pygame.transform.scale(self.background, (800, 800))

    # called every redraw for the mod
    def draw(self, aircraft, smartdisplay):
        self.background_rotated = pygame.transform.rotate(
            self.background, aircraft.roll
        )
    
        px_per_deg_y = smartdisplay.height / 60
        pitch_offset = px_per_deg_y * ( -aircraft.pitch )

        rect = self.background_rotated.get_rect()
        self.pygamescreen.blit(
            self.background_rotated,
            (
                (smartdisplay.width/2) - rect.center[0],
                (smartdisplay.height/2) - rect.center[1] + pitch_offset,
            ),
        )

        smartdisplay.draw_circle(
                 (255,255,255),
                 (smartdisplay.widthCenter,smartdisplay.heightCenter),
                 15,
                 1,
             )



    # called before screen draw.  To clear the screen to your favorite color.
    def clear(self):
        #self.ahrs_bg.fill((0, 0, 0))  # clear screen
        print("clear")

    # handle key events
    def processEvent(self, event):
        print("processEvent")


# vi: modeline tabstop=8 expandtab shiftwidth=4 softtabstop=4 syntax=python
