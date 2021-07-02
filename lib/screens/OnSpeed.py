#!/usr/bin/env python


#################################################
# On Speed HUD
# Christopher Jones 2019.

from ._screen import Screen
from .. import hud_graphics
from lib import hud_utils
import pygame


class OnSpeed(Screen):
    def __init__(self):
        Screen.__init__(self)
        self.name = "OnSpeed"  # set name for this screen
        self.ahrs_bg = 0
        self.MainColor = (0, 255, 0)  # main color
        self.TextColor = (255, 255, 0)  # main color
        self.pxy_div = 60 # Y axis number of pixels per degree divisor

    def initDisplay(self, pygamescreen, width, height):
        Screen.initDisplay(
            self, pygamescreen, width, height
        )  # call parent init screen.
        print(("Init Screen: %s %dx%d"%(self.name,self.width,self.height)))

        self.ahrs_bg = pygame.Surface((self.width * 2, self.height * 2))
        self.ahrs_bg_width = self.ahrs_bg.get_width()
        self.ahrs_bg_height = self.ahrs_bg.get_height()
        self.ahrs_bg_center = (self.ahrs_bg_width / 2, self.ahrs_bg_height / 2)

        # fonts
        self.font = pygame.font.SysFont(
            None, int(self.height / 20)
        )  # font used by horz lines
        self.bigfontSize = 350
        self.bigfont = pygame.font.SysFont(
            "monospace", self.bigfontSize
        )  # font used by debug. initialize font; must be called after 'pygame.init()' to avoid 'Font not Initialized' error

        self.bigFontPosX = self.widthCenter - (self.bigfontSize/2) - 15
        self.bigFontPosY = self.heightCenter - (self.bigfontSize/2) + 30

    def draw(self, aircraft, FPS):

        # draw horz lines
        hud_graphics.hud_draw_horz_lines(
            self.pygamescreen,
            self.ahrs_bg,
            self.width,
            self.height,
            self.ahrs_bg_center,
            15,
            aircraft,
            self.MainColor,
            3,
            1,
            self.font,
            self.pxy_div,
        )

        #Draw airspeed
        label = self.bigfont.render(
            "%d" % (aircraft.ias), 1, self.TextColor
        )
        self.pygamescreen.blit(label, (self.bigFontPosX , self.bigFontPosY) )

        #draw circle
        pygame.draw.circle(
            self.pygamescreen,
            self.MainColor,
            (self.widthCenter, self.heightCenter),
            350,  
            10,
        )

        pygame.display.flip()

    def clearScreen(self):
        self.ahrs_bg.fill((0, 0, 0))  # clear screen

    def processEvent(self, event):
        return


# vi: modeline tabstop=8 expandtab shiftwidth=4 softtabstop=4 syntax=python
