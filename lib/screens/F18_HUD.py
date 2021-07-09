#!/usr/bin/env python

#################################################
# F18 HUD Screen by Brian Chesteen. 01/31/2019  Modified by Cecil Jones 20 May 2019
# Optimized for Garmin G3X System and Kivic HUD using Composite Video Output.
# Credit for original module template goes to Christopher Jones.
# Updated 7/9/2021 Topher.  Now uses modules.

from ._screen import Screen
from .. import hud_graphics
from lib import hud_utils

import pygame
import math
from lib import smartdisplay

from lib.modules.hud.horizon import horizon
from lib.modules.hud.rollindicator import rollindicator
from lib.modules.hud.aoa import aoa
from lib.modules.hud.slipskid import slipskid
from lib.modules.hud.wind import wind
#from lib.modules.hud.hsi import hsi
from lib.modules.hud.heading import heading

class F18_HUD_CJv1(Screen):
    # called only when object is first created.
    def __init__(self):
        Screen.__init__(self)
        self.name = "F18 HUD"  # set name for this screen
        self.show_debug = False  # default off
        self.alt_box_mode = 1  # default on
        self.caged_mode = 1 # default on
        self.MainColor = (0, 255, 0)  # main color of hud graphics

    # called once for setuping up the screen
    def initDisplay(self, pygamescreen, width, height):
        Screen.initDisplay(
            self, pygamescreen, width, height
        )  # call parent init screen.
        print("Init ", self.name,self.width,self.height)

        # fonts
        self.myfont = pygame.font.SysFont("monospace", 20, bold=False) #debug font.
        self.fontIndicator = pygame.font.SysFont("monospace", 40, bold=False)  # ie IAS and ALT
        self.fontIndicatorSmaller = pygame.font.SysFont("monospace", 30, bold=False)  # ie. baro and VSI, etc

        self.heading = heading.Heading()
        self.heading.initMod(self.pygamescreen, self.width, self.height)
        self.heading.setup(            
            350,  # hdg size
            20,  # Gnd Trk Tick size
            (0, 255, 0),  # hdg rose color
            (255, 255, 0),  # hdg label color
        )

        self.roll_indicator = rollindicator.RollIndicator()
        self.roll_indicator.initMod(self.pygamescreen, self.width, self.height)

        self.horizon = horizon.Horizon()
        self.horizon.initMod(self.pygamescreen, self.width, self.height)

        self.aoa = aoa.AOA()
        self.aoa.initMod(self.pygamescreen, self.width, self.height)

        self.slipskid = slipskid.SlipSkid()
        self.slipskid.initMod(self.pygamescreen, self.width, self.height)

        self.wind = wind.Wind()
        self.wind.initMod(self.pygamescreen, self.width, self.height)

    # called every redraw for the screen
    def draw(self, aircraft, smartdisplay):

        # draw the usable area for this screen.
        smartdisplay.drawBorder = True

        # draw roll indicator
        self.horizon.draw(aircraft,smartdisplay)
 
        # IAS
        smartdisplay.draw_box_text(
            smartdisplay.LEFT_MID,
            self.fontIndicator,
            "%d" % (aircraft.ias),
            (255, 255, 0),
            100,
            35,
            self.MainColor,
            1,(0,0),2)
        # ALT
        smartdisplay.draw_box_text(
            smartdisplay.RIGHT_MID,
            self.fontIndicator,
            "%d" % (aircraft.BALT),
            (255, 255, 0),
            100,
            35,
            self.MainColor,
            1,(0,0),2)

        # time string
        smartdisplay.draw_text(smartdisplay.RIGHT_MID_DOWN, self.fontIndicatorSmaller, "%sz" % (aircraft.sys_time_string), (255, 255, 0))
        # baro setting
        smartdisplay.draw_text(smartdisplay.RIGHT_MID_DOWN, self.fontIndicatorSmaller, "%0.2fin" % (aircraft.baro), (255, 255, 0))
        
        # VSI text
        if aircraft.vsi < 0:
            smartdisplay.draw_text(smartdisplay.RIGHT_MID_UP, self.fontIndicatorSmaller, "%d" % (aircraft.vsi), (255, 255, 0))
        else:
            smartdisplay.draw_text(smartdisplay.RIGHT_MID_UP, self.fontIndicatorSmaller, "+%d" % (aircraft.vsi), (255, 255, 0))

        # True aispeed
        smartdisplay.draw_text(smartdisplay.LEFT_MID_UP, self.fontIndicatorSmaller, "TAS %d" % (aircraft.tas), (255, 255, 0))

        # OAT text
        smartdisplay.draw_text(smartdisplay.LEFT_MID_UP, self.fontIndicatorSmaller, "OAT %d\xb0c" % aircraft.oat, (255, 255, 0))

        #AOA text
        if aircraft.ias < 20 or aircraft.aoa == 0 or aircraft.aoa == None:
            smartdisplay.draw_text(smartdisplay.LEFT_MID_UP, self.fontIndicatorSmaller, "AOA: N/A", (255, 255, 0))
        else:
            smartdisplay.draw_text(smartdisplay.LEFT_MID_UP, self.fontIndicatorSmaller, "AOA: %d"%aircraft.aoa, (255, 255, 0))

        # Ground speed
        smartdisplay.draw_text(smartdisplay.LEFT_MID_DOWN, self.fontIndicatorSmaller, "GS %d" % (aircraft.gndspeed), (255, 255, 0))

        # Vertical G
        smartdisplay.draw_text(smartdisplay.LEFT_MID_DOWN, self.fontIndicatorSmaller, "G %0.1f" % (aircraft.vert_G), (255, 255, 0))


        # draw wind direction
        self.wind.draw(aircraft,smartdisplay,(10,smartdisplay.y_end-100))

        # draw Slip Skid
        self.slipskid.draw(aircraft,smartdisplay,(smartdisplay.x_center,smartdisplay.y_center+180))

        # draw AOA indicator
        self.aoa.draw(aircraft,smartdisplay,(smartdisplay.x_start + 20 ,smartdisplay.y_start + 5))

        # draw roll indicator
        self.roll_indicator.draw(aircraft,smartdisplay)

        # draw mag heading bar
        self.heading.draw(aircraft,smartdisplay)

        # Mag heading text
        smartdisplay.draw_box_text(
            smartdisplay.TOP_MID,
            self.fontIndicator,
            "%d" % (aircraft.mag_head),
            (255, 255, 0),
            70,
            35,
            self.MainColor,
            1,
            (0,0),
            2)

        # update entire display..
        pygame.display.flip()

        # render debug text
        if self.show_debug:
            hud_graphics.hud_draw_debug(aircraft,smartdisplay,self.myfont)


    # called before screen draw.  To clear the screen to your favorite color.
    def clearScreen(self):
        self.pygamescreen.fill((0, 0, 0))  # clear screen

    # handle key events
    def processEvent(self, event):
        if event.key == pygame.K_d:
            self.show_debug = not self.show_debug
        if event.key == pygame.K_a:
            self.alt_box_mode = not self.alt_box_mode
        if event.key == pygame.K_l:
            self.line_thickness += 1
            if self.line_thickness > 8:
                self.line_thickness = 2
        if event.key == pygame.K_c:
            self.horizon.center_circle_mode += 1
            if self.horizon.center_circle_mode > 4:
                self.horizon.center_circle_mode = 0
        if event.key == pygame.K_x:
            self.caged_mode = not self.caged_mode


# vi: modeline tabstop=8 expandtab shiftwidth=4 softtabstop=4 syntax=python
