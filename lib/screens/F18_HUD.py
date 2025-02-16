#!/usr/bin/env python

#################################################
# F18 HUD Screen by Brian Chesteen. 01/31/2019  Modified by Cecil Jones 20 May 2019
# Optimized for Garmin G3X System and Kivic HUD using Composite Video Output.
# Credit for original module template goes to Topher
# Updated 7/9/2021 Topher.  Now uses modules.

from ._screen import Screen
from .. import hud_graphics
from lib import hud_utils

import pygame
import math
from lib import smartdisplay
from lib.modules.hud.horizon import horizon
from lib.modules.hud.cdi import cdi
from lib.modules.hud.gcross import gcross
from lib.modules.hud.rollindicator import rollindicator
from lib.modules.hud.aoa import aoa
from lib.modules.hud.slipskid import slipskid
from lib.modules.hud.wind import wind
#from lib.modules.hud.hsi import hsi
from lib.modules.hud.heading import heading
from lib.modules.efis.trafficscope import trafficscope

class F18_HUD(Screen):
    # called only when object is first created.
    def __init__(self):
        Screen.__init__(self)
        self.name = "F18 HUD"  # set name for this screen
        self.caged_mode = 1 # default on
        self.MainColor = (0, 255, 0)  # main color of hud graphics

    # called once for setting up the screen
    def initDisplay(self, pygamescreen, width, height):
        Screen.initDisplay(
            self, pygamescreen, width, height
        )  # call parent init screen.
        print("Init ", self.name,self.width,self.height)

        self.show_lat_lon = hud_utils.readConfigBool("F18_HUD", "show_lat_lon", False)

        # fonts
        self.myfont = pygame.font.SysFont("monospace", 20, bold=True) #small font.
        self.fontIndicator = pygame.font.SysFont("monospace", 100, bold=True)  # ie IAS and ALT
        self.fontAltSmall = pygame.font.SysFont("monospace", 50, bold=True)  # smaller font for right side of ALT
        self.fontIndicatorSmaller = pygame.font.SysFont("monospace", 30, bold=True)  # ie. baro and VSI, etc

        self.heading = heading.heading()
        self.heading.initMod(self.pygamescreen, self.width, self.height)
        self.heading.setup(
        )

        self.roll_indicator = rollindicator.rollindicator()
        self.roll_indicator.initMod(self.pygamescreen, self.width, self.height)

        self.horizon = horizon.horizon()
        self.horizon.initMod(self.pygamescreen, self.width, self.height)

        self.aoa = aoa.aoa()
        self.aoa.initMod(self.pygamescreen, 40, 133)
        #Sets Width(X) and Height (Y) of AOA HUD Size

        self.slipskid = slipskid.slipskid()
        self.slipskid.initMod(self.pygamescreen, 250, 30)

        self.wind = wind.wind()
        self.wind.initMod(self.pygamescreen, self.width, self.height)
        
        self.cdi = cdi.cdi()
        self.cdi.initMod(self.pygamescreen, self.width, self.height)

        self.gcross = gcross.gcross()
        self.gcross.initMod(self.pygamescreen, self.width, self.height)

        self.trafficScope = trafficscope.trafficscope()
        self.trafficScope.initMod(self.pygamescreen, 400, 400)

    # called every redraw for the screen
    def draw(self, aircraft, smartdisplay):

        # draw the usable area for this screen.
        smartdisplay.drawBorder = False

        # draw roll indicator
        self.horizon.draw(aircraft,smartdisplay)
 
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

        # ALT
        baroalt = round(aircraft.BALT/10)
        baroalt = baroalt * 10
        smartdisplay.draw_box_text_with_big_and_small_text(
            smartdisplay.RIGHT_MID, # postion
            self.fontIndicator, # big font
            self.fontAltSmall, # little font
            "%s" % (baroalt), # text
            2, # how many chars on the right do I want in small text.
            (255, 255, 0), # text color
            5, # total char space length (padding)
            self.MainColor, # line color
            4 # box line thickness
            )
            
        # Draw CDI Needles
        self.cdi.draw(aircraft,smartdisplay,(smartdisplay.x_center,smartdisplay.y_center))

        # Draw Air_Air Gunsight
        self.gcross.draw(aircraft,smartdisplay,(smartdisplay.x_center,smartdisplay.y_center))

        # RadAlt  aircraft AGL Above Terrain #
        smartdisplay.draw_text(smartdisplay.RIGHT_MID_DOWN, self.fontIndicatorSmaller, "RadAlt %s" % (aircraft.agl), (255, 255, 0))

        # time string
        smartdisplay.draw_text(smartdisplay.RIGHT_MID_DOWN, self.fontIndicatorSmaller, "%s Lcl" % (aircraft.sys_time_string), (255, 255, 0))

        # Engine RPM
        smartdisplay.draw_text(smartdisplay.RIGHT_MID_DOWN, self.fontIndicatorSmaller, "RPM %d" % (aircraft.engine.RPM), (255, 255, 0))

        # Next Way Point Distance
        smartdisplay.draw_text(smartdisplay.RIGHT_MID_DOWN, self.fontIndicatorSmaller, "WP Dist %0.1f" % (aircraft.nav.WPDist), (255, 255, 0))

        # Gun Cross Mode, Target Wing span and DogFight Mode.
        if(self.gcross.GunSightMode == 4):
            smartdisplay.draw_text(smartdisplay.RIGHT_MID_DOWN, self.fontIndicatorSmaller, "DGFT", (255, 255, 0))
        elif(self.gcross.GunSightMode != 0):
            smartdisplay.draw_text(smartdisplay.RIGHT_MID_DOWN, self.fontIndicatorSmaller, "TgtWgSpan %d" % (self.gcross.TargetWingSpan), (255, 255, 0))

        # VSI text
        smartdisplay.draw_text(smartdisplay.RIGHT_MID_UP, self.fontIndicatorSmaller, aircraft.get_vsi_string(), (255, 255, 0))

        # True aispeed
        smartdisplay.draw_text(smartdisplay.LEFT_MID_UP, self.fontIndicatorSmaller, "TAS %d %s" % (aircraft.get_tas(), aircraft.get_speed_description()), (255, 255, 0))

        # Ground speed
        smartdisplay.draw_text(smartdisplay.LEFT_MID_DOWN, self.fontIndicatorSmaller, "GS %d" % (aircraft.get_gs()), (255, 255, 0))

        # OAT text
        smartdisplay.draw_text(smartdisplay.LEFT_MID_DOWN, self.fontIndicatorSmaller, "%0.1f%s" % (aircraft.get_oat(),aircraft.get_temp_description()), (255, 255, 0))

        # Vertical G
        smartdisplay.draw_text(smartdisplay.LEFT_MID_DOWN, self.fontIndicatorSmaller, "G %0.1f" % (aircraft.vert_G), (255, 255, 0))

        # draw wind direction
        self.wind.draw(aircraft,smartdisplay,(30,smartdisplay.y_end - 210))

        # draw Slip Skid
        self.slipskid.draw(aircraft,smartdisplay,(smartdisplay.x_center,smartdisplay.y_end-35))

        # draw AOA indicator
        self.aoa.draw(aircraft,smartdisplay,(smartdisplay.x_start + 75 ,smartdisplay.y_end - 400))
      
        # draw roll indicator
        self.roll_indicator.draw(aircraft,smartdisplay)

        # draw mag heading bar
        self.heading.draw(aircraft,smartdisplay)

        # Mag heading text
        smartdisplay.draw_box_text_padding(
            smartdisplay.TOP_MID, # postion 
            self.fontAltSmall, # font
            "%d°" % (aircraft.mag_head), # text
            (255, 255, 0), # text color
            3, # padding chars..
            self.MainColor, # line color
            2 # box line thickness
            )

        # Show traffic?
        if(self.mode_traffic>0):
            self.trafficScope.draw(aircraft,smartdisplay,(smartdisplay.x_center-self.trafficScope.width/2,smartdisplay.y_center-self.trafficScope.height/2))

        # nearest traffic alert.
        target = aircraft.traffic.getNearestTarget()
        if(target!=None):
            line2 = str(target.speed)+"mph"
            if(target.altDiff != None):
                if(target.altDiff>0): prefix = "+"
                else: prefix = ""
                line2 = line2 + " "+prefix+'{:,}ft'.format(target.altDiff)
            line1 = target.callsign + " %.1fmi. %d\xb0 "%(target.dist,target.brng)
            line3 = "Target Trk: "+str(target.track) + "\xb0"

            smartdisplay.draw_text(smartdisplay.RIGHT_MID_UP, self.myfont, " " , (255, 255, 0))
            smartdisplay.draw_text(smartdisplay.RIGHT_MID_UP, self.myfont, line3 , (255, 255, 0))
            smartdisplay.draw_text(smartdisplay.RIGHT_MID_UP, self.myfont, line2 , (255, 255, 0))
            smartdisplay.draw_text(smartdisplay.RIGHT_MID_UP, self.myfont, line1 , (255, 255, 0))
            smartdisplay.draw_text(smartdisplay.RIGHT_MID_UP, self.myfont, "Nearest Target:" , (255, 255, 0))


        # update entire display..
        pygame.display.flip()


    # called before screen draw.  To clear the screen to your favorite color.
    def clearScreen(self):
        #self.pygamescreen.fill((0, 0, 0))  # clear screen
        pass

    # handle key events
    def processEvent(self, event, aircraft, smartdisplay):
        if(event.type=="modechange"):
            self.setMode(event.key, event.value)
            if(event.key=="traffic"):
                event.value = self.mode_traffic
                self.trafficScope.processEvent(event,aircraft,smartdisplay)

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_KP9 or event.key == pygame.K_9:
                self.horizon.cyclecaged_mode()
            elif event.key == pygame.K_8 or event.key == pygame.K_KP8:
                self.gcross.cycleGunSight()
            elif event.key == pygame.K_0 or event.key == pygame.K_KP0:
                self.cdi.cycleNavSource(aircraft)



# vi: modeline tabstop=8 expandtab shiftwidth=4 softtabstop=4 syntax=python
