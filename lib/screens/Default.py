#!/usr/bin/env python

#################################################
# Default example screen for hud system
# To create your own hud duplicate this file and rename class DefaultScreen to your new filename (without the .py)
# for example MyHud.py would have a class name of MyHud in it.
# 7/9/2021 Topher.

from ._screen import Screen
from .. import hud_graphics
from lib import hud_utils
from lib import smartdisplay
import pygame
from lib.modules.efis.artificalhorz import artificalhorz
from lib.modules.hud.horizon import horizon
from lib.modules.hud.aoa import aoa
from lib.modules.hud.slipskid import slipskid
from lib.modules.gui.menu import menu


class Default(Screen):
    # called only when object is first created.
    def __init__(self):
        Screen.__init__(self)
        self.name = "Default"  # set name for this screen
        self.show_hud = False
        self.MainColor = (0, 255, 0)  # main color of hud graphics
        self.flyOnSpeedMode = False

    # called once for setuping up the screen
    def initDisplay(self, pygamescreen, width, height):
        Screen.initDisplay(
            self, pygamescreen, width, height
        )  # call parent init screen.
        print(("Init Screen: %s %dx%d"%(self.name,self.width,self.height)))

        # fonts
        self.font = pygame.font.SysFont(
            None, int(self.height / 20)
        )  # font used by horz lines
        self.myfont = pygame.font.SysFont(
            "monospace", 22
        )  # font used by debug. initialize font; must be called after 'pygame.init()' to avoid 'Font not Initialized' error
        self.fontIndicator = pygame.font.SysFont("monospace", 100)  # ie IAS and ALT
        self.fontAltSmall = pygame.font.SysFont("monospace", 50)  # or ALT small right chars.
        self.fontIndicatorSmaller = pygame.font.SysFont(
            "monospace", 30
        )  # ie. baro and VSI
        self.bigfont = pygame.font.SysFont(
            "monospace", 300
        )  # big font used for AOA.

        self.ah = artificalhorz.ArtificalHorz()
        self.ah.initMod(self.pygamescreen, self.width, self.height)

        self.hud_horizon = horizon.Horizon()
        self.hud_horizon.initMod(self.pygamescreen, self.width, self.height)

        self.aoa = aoa.AOA()
        self.aoa.initMod(self.pygamescreen, 120, self.height - 10)  # make a big AOA!

        self.slipskid = slipskid.SlipSkid()
        self.slipskid.initMod(self.pygamescreen, 250, 50)

        self.menu = menu.Menu()
        self.menu.initMod(self.pygamescreen, 400, 300, "Options")

    # called every redraw for the screen
    def draw(self, aircraft, smartdisplay):


        # onspeed mode?
        if(aircraft.ias < 100 and aircraft.ias > 10 and aircraft.aoa > 5 ):
            self.flyOnSpeedMode = True  # don't draw the normal efis screen.

            #draw a big AOA indicator
            self.aoa.draw(aircraft,smartdisplay,(smartdisplay.x_center /3 ,smartdisplay.x_start + 5))

            smartdisplay.draw_circle_text( # draw large airspeed indicator
                smartdisplay.CENTER_CENTER, 
                self.bigfont, 
                "%d" % (aircraft.ias), 
                self.aoa.aoa_color,
                250 , 
                self.aoa.aoa_color, 
                20,
                (0,0),
                2)
        else:
            self.flyOnSpeedMode = False

        if(self.flyOnSpeedMode == False):
            # draw hud of efis horizon
            if(self.show_hud):
                self.hud_horizon.draw(aircraft,smartdisplay)
            else:
                self.ah.draw(aircraft,smartdisplay)

            # IAS
            smartdisplay.draw_box_text_padding(
                smartdisplay.LEFT_MID, # postion
                self.fontIndicator, # font
                "%d" % (aircraft.get_ias()), # text
                (255, 255, 0), # text color
                3, # padding chars..
                self.MainColor, # line color
                4 # box line thickness
                )
            # True aispeed
            smartdisplay.draw_text(smartdisplay.LEFT_MID_UP, self.fontIndicatorSmaller, "TAS %d" % (aircraft.tas), (255, 255, 0))

            # Ground speed
            smartdisplay.draw_text(smartdisplay.LEFT_MID_DOWN, self.fontIndicatorSmaller, "GS %d" % (aircraft.gndspeed), (255, 255, 0))

        # ALT
        smartdisplay.draw_box_text_with_big_and_small_text(
            smartdisplay.RIGHT_MID, # postion
            self.fontIndicator, # big font
            self.fontAltSmall, # little font
            "%d" % (aircraft.BALT), # text
            3, # how many chars on the right do I want in small text.
            (255, 255, 0), # text color
            5, # total char space length (padding)
            self.MainColor, # line color
            4 # box line thickness
            )

        # baro setting
        smartdisplay.draw_text(smartdisplay.RIGHT_MID_DOWN, self.myfont, "%0.2f" % (aircraft.baro), (255, 255, 0))
        
        # VSI
        smartdisplay.draw_text(smartdisplay.RIGHT_MID_UP, self.fontIndicatorSmaller, aircraft.get_vsi_string(), (255, 255, 0))


        # Mag heading
        smartdisplay.draw_box_text(
            smartdisplay.TOP_MID,
            self.fontIndicator,
            "%d" % (aircraft.mag_head),
            (255, 255, 0),
            170,
            90,
            self.MainColor,
            1,
            (0,0),
            2)

        # draw Slip Skid
        self.slipskid.draw(aircraft,smartdisplay,(smartdisplay.x_center,smartdisplay.y_end-50))

        # Time
        smartdisplay.draw_text(smartdisplay.TOP_RIGHT, self.fontIndicatorSmaller, "%sz" % (aircraft.sys_time_string), (255, 255, 0))

        # Internal CPU temp
        smartdisplay.draw_text(smartdisplay.BOTTOM_RIGHT, self.fontIndicatorSmaller, "%d°C" % (aircraft.internal.Temp), (255, 255, 0))

        if self.debug:
            hud_graphics.hud_draw_debug(aircraft,smartdisplay,self.myfont)


    # called before screen draw.  To clear the screen to your favorite color.
    def clearScreen(self):
        self.pygamescreen.fill((0, 0, 0))  # clear screen

    # handle key events
    def processEvent(self, event, aircraft, smartdisplay):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_h:
                self.show_hud = not self.show_hud

        if event.type == pygame.MOUSEBUTTONDOWN:
                mx, my = pygame.mouse.get_pos()
                if(mx<100 and my <100):
                    self.menu.draw(aircraft,smartdisplay)
                else:
                    self.show_hud = not self.show_hud


# vi: modeline tabstop=8 expandtab shiftwidth=4 softtabstop=4 syntax=python
