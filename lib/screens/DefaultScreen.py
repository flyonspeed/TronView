#!/usr/bin/env python

#################################################
# Default example screen for hud system
# To create your own hud duplicate this file and rename class DefaultScreen to your new filename (without the .py)
# for example MyHud.py would have a class name of MyHud in it.
# Christopher Jones 2019.

from ._screen import Screen
from .. import hud_graphics
from lib import hud_utils
from lib import smartdisplay
from lib import drawpos
import pygame
from lib.modules.efis.artificalhorz import artificalhorz


class DefaultScreen(Screen):
    # called only when object is first created.
    def __init__(self):
        Screen.__init__(self)
        self.name = "Default Hud Screen"  # set name for this screen
        self.ahrs_bg = 0
        self.show_debug = False  # default off
        self.show_FPS = False #show screen refresh rate in frames per second for performance tuning
        self.line_mode = hud_utils.readConfigInt("HUD", "line_mode", 1)
        self.alt_box_mode = 1  # default on
        self.line_thickness = hud_utils.readConfigInt("HUD", "line_thickness", 2)
        self.center_circle_mode = hud_utils.readConfigInt("HUD", "center_circle", 2)
        self.ahrs_line_deg = hud_utils.readConfigInt("HUD", "vertical_degrees", 15)
        print(("ahrs_line_deg = %d"%(self.ahrs_line_deg)))
        self.MainColor = (0, 255, 0)  # main color of hud graphics
        self.pxy_div = 60 # Y axis number of pixels per degree divisor

    # called once for setuping up the screen
    def initDisplay(self, pygamescreen, width, height):
        Screen.initDisplay(
            self, pygamescreen, width, height
        )  # call parent init screen.
        print(("Init Screen: %s %dx%d"%(self.name,self.width,self.height)))
        self.x_start = 0;
        self.y_start = 0;
        self.ahrs_bg = pygame.Surface((self.width, self.height))
        self.ahrs_bg_width = self.ahrs_bg.get_width()
        self.ahrs_bg_height = self.ahrs_bg.get_height()
        self.ahrs_bg_center = (self.ahrs_bg_width / 2, self.ahrs_bg_height / 2)

        # fonts
        self.font = pygame.font.SysFont(
            None, int(self.height / 20)
        )  # font used by horz lines
        self.myfont = pygame.font.SysFont(
            "monospace", 22
        )  # font used by debug. initialize font; must be called after 'pygame.init()' to avoid 'Font not Initialized' error
        self.fontIndicator = pygame.font.SysFont("monospace", 40)  # ie IAS and ALT
        self.fontIndicatorSmaller = pygame.font.SysFont(
            "monospace", 30
        )  # ie. baro and VSI
        print(("surface : %dx%d"%(self.ahrs_bg.get_width(),self.ahrs_bg.get_height())))

        self.ah = artificalhorz.ArtificalHorz()
        self.ah.initMod(self.pygamescreen, self.width, self.height)



    # called every redraw for the screen
    def draw(self, aircraft, smartdisplay):

        self.ah.draw(aircraft,smartdisplay)

        # draw horz lines
        # hud_graphics.hud_draw_horz_lines(
        #     self.pygamescreen,
        #     self.ahrs_bg,
        #     self.width,
        #     self.height,
        #     self.ahrs_bg_center,
        #     self.ahrs_line_deg,
        #     aircraft,
        #     self.MainColor,
        #     self.line_thickness,
        #     self.line_mode,
        #     self.font,
        #     self.pxy_div,
        # )        
        # self.pygamescreen.blit(self.ahrs_bg, (-0,-0))

        if self.show_debug:
            hud_graphics.hud_draw_debug(aircraft,smartdisplay,self.myfont)


        if self.alt_box_mode:
            # IAS
            smartdisplay.draw_box_text(
                drawpos.DrawPos.LEFT_MID,
                self.fontIndicator,
                "%d" % (aircraft.ias),
                (255, 255, 0),
                100,
                35,
                self.MainColor,
                1,(0,0),2)
            # ALT
            smartdisplay.draw_box_text(
                drawpos.DrawPos.RIGHT_MID,
                self.fontIndicator,
                "%d" % (aircraft.BALT),
                (255, 255, 0),
                100,
                35,
                self.MainColor,
                1,(0,0),2)

            # baro setting
            smartdisplay.draw_text(drawpos.DrawPos.RIGHT_MID_DOWN, self.myfont, "%0.2f" % (aircraft.baro), (255, 255, 0))
            
            # VSI
            if aircraft.vsi < 0:
                smartdisplay.draw_text(drawpos.DrawPos.RIGHT_MID_UP, self.fontIndicatorSmaller, "%d" % (aircraft.vsi), (255, 255, 0))
            else:
                smartdisplay.draw_text(drawpos.DrawPos.RIGHT_MID_UP, self.fontIndicatorSmaller, "+%d" % (aircraft.vsi), (255, 255, 0))

            # True aispeed
            smartdisplay.draw_text(drawpos.DrawPos.LEFT_MID_UP, self.fontIndicatorSmaller, "TAS %d" % (aircraft.tas), (255, 255, 0))

            # Ground speed
            smartdisplay.draw_text(drawpos.DrawPos.LEFT_MID_DOWN, self.fontIndicatorSmaller, "GS %d" % (aircraft.gndspeed), (255, 255, 0))

            # Mag heading
            smartdisplay.draw_box_text(
                drawpos.DrawPos.TOP_MID,
                self.fontIndicator,
                "%d" % (aircraft.mag_head),
                (255, 255, 0),
                70,
                35,
                self.MainColor,
                1,
                (0,0),
                2)

    # called before screen draw.  To clear the screen to your favorite color.
    def clearScreen(self):
        self.pygamescreen.fill((0, 0, 0))  # clear screen

    # handle key events
    def processEvent(self, event):
        if event.key == pygame.K_d:
            self.show_debug = not self.show_debug
        if event.key == pygame.K_EQUALS:
            self.width = self.width + 10
        if event.key == pygame.K_MINUS:
            self.width = self.width - 10
        if event.key == pygame.K_SPACE:
            self.line_mode = not self.line_mode
        if event.key == pygame.K_a:
            self.alt_box_mode = not self.alt_box_mode
        if event.key == pygame.K_l:
            self.line_thickness += 1
            if self.line_thickness > 8:
                self.line_thickness = 2
        if event.key == pygame.K_c:
            self.center_circle_mode += 1
            if self.center_circle_mode > 3:
                self.center_circle_mode = 0


# vi: modeline tabstop=8 expandtab shiftwidth=4 softtabstop=4 syntax=python
