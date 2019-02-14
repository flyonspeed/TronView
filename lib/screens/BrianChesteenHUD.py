#!/usr/bin/env python

#################################################
#Custom HUD Screen by Brian Chesteen. 01/31/2019
#Optimized for Garmin G3X Systems.
#Credit for original module template goes to Christopher Jones.
from __future__ import print_function
from _screen import Screen
from .. import hud_graphics
from lib import hud_utils
import _hsi
import pygame
import math


class BrianChesteenHUD(Screen):
    # called only when object is first created.
    def __init__(self):
        Screen.__init__(self)
        self.name = "Brian Chesteen Hud Screen"  # set name for this screen
        self.ahrs_bg = 0
        self.show_debug = False  # default off
        self.show_FPS = False #show screen refresh rate in frames per second for performance tuning
        self.line_mode = hud_utils.readConfigInt("HUD", "line_mode", 1)
        self.alt_box_mode = 1  # default on
        self.line_thickness = hud_utils.readConfigInt("HUD", "line_thickness", 2)
        self.center_circle_mode = hud_utils.readConfigInt("HUD", "center_circle", 2)
        self.ahrs_line_deg = hud_utils.readConfigInt("HUD", "vertical_degrees", 10)
        print("ahrs_line_deg = %d"%(self.ahrs_line_deg))
        self.MainColor = (0, 255, 0)  # main color of hud graphics

        # called once for setuping up the screen

    def initDisplay(self, pygamescreen, width, height):
        Screen.initDisplay(
            self, pygamescreen, width, height
        )  # call parent init screen.
        print("Init ", self.name)
        print(self.width)
        print(self.height)

        self.ahrs_bg = pygame.Surface((self.width * 2, self.height * 2))
        self.ahrs_bg_width = self.ahrs_bg.get_width()
        self.ahrs_bg_height = self.ahrs_bg.get_height()
        self.ahrs_bg_center = (self.ahrs_bg_width / 2, self.ahrs_bg_height / 2)

        #images
        self.arrow = pygame.image.load("lib/screens/_images/arrow_g.png").convert()
        self.arrow.set_colorkey((255,255,255))
        self.arrow_scaled = pygame.transform.scale(self.arrow, (50, 50))

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

        #set up the HSI
        _hsi.hsi_init(
            self,
            350, #HSI size
            20, #Gnd Trk Tick size
            (255,0,0) # HSI color
        )

    # called every redraw for the screen
    def draw(self, aircraft, FPS):
        # draw horz lines
        hud_graphics.hud_draw_horz_lines(
            self.pygamescreen,
            self.ahrs_bg,
            self.width,
            self.height,
            self.ahrs_bg_center,
            self.ahrs_line_deg,
            aircraft,
            self.MainColor,
            self.line_thickness,
            self.line_mode,
            self.font,
        )

        # render debug text
        if self.show_debug:
            label = self.myfont.render("Pitch: %d" % (aircraft.pitch), 1, (255, 255, 0))
            self.pygamescreen.blit(label, (0, 0))
            label = self.myfont.render("Roll: %d" % (aircraft.roll), 1, (255, 255, 0))
            self.pygamescreen.blit(label, (0, 20))
            label = self.myfont.render(
                "IAS: %d  VSI: %d" % (aircraft.ias, aircraft.vsi), 1, (255, 255, 0)
            )
            self.pygamescreen.blit(label, (0, 40))
            label = self.myfont.render(
                "Alt: %d  PresALT:%d  BaroAlt:%d   AGL: %d"
                % (aircraft.alt, aircraft.PALT, aircraft.BALT, aircraft.agl),
                1,
                (255, 255, 0),
            )
            self.pygamescreen.blit(label, (0, 60))
            label = self.myfont.render("AOA: %d" % (aircraft.aoa), 1, (255, 255, 0))
            self.pygamescreen.blit(label, (0, 80))
            label = self.myfont.render(
                "MagHead: %d\xb0d  GndTrack: %d\xb0" % (aircraft.mag_head, aircraft.gndtrack),
                1,
                (255, 255, 0),
            )
            self.pygamescreen.blit(label, (0, 100))
            label = self.myfont.render(
                "Baro: %0.2f diff: %0.4f" % (aircraft.baro, aircraft.baro_diff),
                1,
                (255, 255, 0),
            )
            self.pygamescreen.blit(label, (0, 120))
            label = self.myfont.render(
                "size: %d,%d" % (self.width, self.height), 1, (20, 255, 0)
            )
            self.pygamescreen.blit(label, (0, 140))
            label = self.myfont.render(
                "surface: %d,%d" % (self.ahrs_bg_width, self.ahrs_bg_width),
                1,
                (20, 255, 0),
            )
            self.pygamescreen.blit(label, (0, 160))
            label = self.myfont.render(
                "msg_count: %d" % (aircraft.msg_count), 1, (20, 255, 0)
            )
            self.pygamescreen.blit(label, (0, 180))

        if self.show_FPS:
            label = self.myfont.render(
                "%0.2f FPS" % (FPS), 1, (20, 255, 0)
            )
            self.pygamescreen.blit(label, (self.width/2 - 55, self.height - 25))

        if self.alt_box_mode:
            # IAS
            hud_graphics.hud_draw_box_text(
                self.pygamescreen,
                self.fontIndicator,
                "%d" % (aircraft.ias),
                (255, 255, 0),
                0,
                self.heightCenter,
                100,
                35,
                self.MainColor,
                1,
            )
            # ALT
            hud_graphics.hud_draw_box_text(
                self.pygamescreen,
                self.fontIndicator,
                "%d" % (aircraft.BALT),
                (255, 255, 0),
                self.width - 100,
                self.heightCenter,
                100,
                35,
                self.MainColor,
                1,
            )

            # baro setting
            label = self.fontIndicatorSmaller.render(
                "%0.2f" % (aircraft.baro), 1, (255, 255, 0)
            )
            self.pygamescreen.blit(label, (self.width - 100, (self.heightCenter) + 35))
            # VSI
            if aircraft.vsi < 0:
                label = self.fontIndicatorSmaller.render(
                    "%d" % (aircraft.vsi), 1, (255, 255, 0)
                )
            else:
                label = self.fontIndicatorSmaller.render(
                    "+%d" % (aircraft.vsi), 1, (255, 255, 0)
                )
            self.pygamescreen.blit(label, (self.width - 100, (self.heightCenter) - 30))
            # True aispeed
            label = self.fontIndicatorSmaller.render(
                "TAS %dKT" % (aircraft.tas), 1, (255, 255, 0)
            )
            self.pygamescreen.blit(label, (1, (self.heightCenter) - 30))
            # Ground speed
            label = self.fontIndicatorSmaller.render(
                "GS  %dKT" % (aircraft.gndspeed), 1, (255, 255, 0)
            )
            self.pygamescreen.blit(label, (1, (self.heightCenter) + 35))
             # Vertical G
            label = self.myfont.render(
                "G   %0.1f" % (aircraft.vert_G), 1, (255, 255, 0)
            )
            self.pygamescreen.blit(label, (1, (self.heightCenter) + 120))
             # AOA
            label = self.myfont.render(
                "AOA %d" % (aircraft.aoa), 1, (255, 255, 0)
            )
            self.pygamescreen.blit(label, (1, (self.heightCenter) + 100))
             # AGL
            label = self.myfont.render(
                "AGL %dFT" % (aircraft.agl), 1, (255, 255, 0)
            )
            self.pygamescreen.blit(label, (1, (self.heightCenter) - 100))
             # Gnd Track
            label = self.myfont.render(
                "TRK %d\xb0"  % (aircraft.gndtrack), 1, (255, 255, 0)
            )
            self.pygamescreen.blit(label, (self.width / 2 - 45, (self.heightCenter) - 180))
             # OAT
            label = self.myfont.render(
                "OAT %d\xb0C %d\xb0F" % (aircraft.oat, ((aircraft.oat * 9.0/5.0) + 32.0)), 1, (255, 255, 0)
            )
            self.pygamescreen.blit(label, (1, (self.heightCenter) - 120))
             # Wind Speed
            if aircraft.wind_speed != None:
                label = self.myfont.render(
                    "%dKT" % (aircraft.wind_speed), 1, (255, 255, 0)
                )
                self.pygamescreen.blit(label, (self.width - 100, (self.heightCenter) - 200))
            else:
                label = self.myfont.render(
                    "--KT" , 1, (255, 255, 0)
                )
                self.pygamescreen.blit(label, (self.width - 100, (self.heightCenter) - 200))
             # Wind Dir
            if aircraft.wind_dir != None:
                label = self.myfont.render(
                    "%d\xb0" % (aircraft.wind_dir), 1, (255, 255, 0)
                )
                self.pygamescreen.blit(label, (self.width - 100, (self.heightCenter) - 120))
            else:                
                label = self.myfont.render(
                    "--\xb0", 1, (255, 255, 0)
                )
                self.pygamescreen.blit(label, (self.width - 100, (self.heightCenter) - 120))
            # Mag heading
            hud_graphics.hud_draw_box_text(
                self.pygamescreen,
                self.fontIndicator,
                "%d\xb0" % (aircraft.mag_head),
                (255, 255, 0),
                (self.width / 2) - 40,
                25,
                95,
                35,
                self.MainColor,
                1,
            )
        if self.center_circle_mode == 1:
            pygame.draw.circle(
                self.pygamescreen,
                self.MainColor,
                (self.width / 2, self.heightCenter),
                3,
                1,
            )
        if self.center_circle_mode == 2:
            pygame.draw.circle(
                self.pygamescreen,
                self.MainColor,
                (self.width / 2, self.heightCenter),
                15,
                1,
            )
        if self.center_circle_mode == 3:
            pygame.draw.circle(
                self.pygamescreen,
                self.MainColor,
                (self.width / 2, self.heightCenter),
                50,
                1,
            )

        if aircraft.norm_wind_dir != None:
            arrow_rotated = pygame.transform.rotate(self.arrow_scaled, aircraft.norm_wind_dir)
            arrow_rect = arrow_rotated.get_rect()
            self.pygamescreen.blit(arrow_rotated, ((self.width - 70) - arrow_rect.center[0],
                                    (self.height / 2 - 150) - arrow_rect.center[1]))

        # main HSI processing
        _hsi.hsi_main(
            self, 
            aircraft.mag_head,
            aircraft.gndtrack,
            aircraft.turn_rate
        )

        # print Screen.name
        pygame.display.flip()

    # called before screen draw.  To clear the screen to your favorite color.
    def clearScreen(self):
        self.ahrs_bg.fill((0, 0, 0))  # clear screen


        # handle key events
    def processEvent(self, event):
        if event.key == pygame.K_d:
            self.show_debug = not self.show_debug
        if event.key == pygame.K_f:
            self.show_FPS = not self.show_FPS #show screen refresh rate in frames per second for performance tuning
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

