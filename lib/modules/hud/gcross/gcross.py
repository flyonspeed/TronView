#!/usr/bin/env python

#################################################
# Module: Gun Cross
# Topher 2023.
# Created by Cecil Jones 

from lib.modules._module import Module
from lib import hud_graphics
from lib import hud_utils
from lib import smartdisplay
from lib import aircraft
import pygame
import math
import time

class gcross(Module):
    # called only when object is first created.
    def __init__(self):
        Module.__init__(self)
        self.name = "HUD gcross"  # set name
        self.GunSightMode = 0 # Visual mode this gun sight is in.
        self.TargetWingSpan = 0 # value to show user of target wing span.
        self.DogFightWithCallsign = ""

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

        self.GColor = ( 0,255, 0)  # Gun Cross Color = Yellow
        self.y_offset = hud_utils.readConfigInt("HUD", "Horizon_Offset", 0)  #  Horizon/Waterline Pixel Offset
        # use aircraft.flightPathMarker_x this value comes from the horizon code.
        self.y_center = height / 2
        self.x_center = width / 2
        self.x_offset = 0
        self.showLDMax = True
        self.yLDMaxDots = height - (height/8)
        self.xLDMaxDotsFromCenter = width/2

        self.GColor_color = ( 0,255, 0)  # Gun Cross Color = Yellow

        self.TargetWingSpan - 0

    # called every redraw for the mod
    def draw(self, aircraft, smartdisplay, pos):

        self.surface.fill((0, 0, 0))  # clear surface

        x,y = pos

        #  below for Gun Dir Test --------------------------------------
        #  working Posn pipper_posn = (int(smartdisplay.x_center), int(smartdisplay.y_center))
        #  pipper_posn = (int(smartdisplay.x_center), int((smartdisplay.y_center + self.y_offset) - (aircraft.vsi / 4)))  # Adjust pipper poaition for Waterline/Boresight and Vertical FPV No FltPath_V
        pipper_posn = (int(smartdisplay.x_center - aircraft.fpv_x), int((smartdisplay.y_center + self.y_offset) - (aircraft.vsi / 2)))  # Adjust pipper poaition for Waterline/Boresight and Vertical FPV   + self.x_offset
        #  pipper_posn = (-1 * (aircraft_fpv_x), int((smartdisplay.y_center + self.y_offset) - (aircraft.vsi / 4)))  # Adjust pipper poaition for Waterline/Boresight and Vertical FPV   + self.x_offset
        color = self.GColor_color   
        screen = self.pygamescreen

        # find nearest target.
        nearestTarget = aircraft.traffic.getNearestTarget(10)
        if(nearestTarget != None):
            #print("Nearest Target is %s", nearestTarget.callsign)
            traffic_nm = nearestTarget.dist
            self.DogFightWithCallsign = nearestTarget.callsign
        else:
            traffic_nm = 0
            self.DogFightWithCallsign = ""


        # Set circle radius and line width
        circle_radius = 150
        arc_radius = 148
        circle_radius_ctrdot = 5
        line_width = 2
        arc_width = 10
        #   End Gun Dir Test Setup Values --------------------------------
        if self.GunSightMode == 0:
                pygame.draw.line(
                smartdisplay.pygamescreen,
                self.GColor,
                [smartdisplay.x_center - 10 + self.x_offset, smartdisplay.y_center + self.y_offset + 20],
                [smartdisplay.x_center + self.x_offset , smartdisplay.y_center + self.y_offset],
                3,
            )
                pygame.draw.line(
                smartdisplay.pygamescreen,
                self.GColor,
                [smartdisplay.x_center - 10 + self.x_offset, smartdisplay.y_center + self.y_offset + 20],
                [smartdisplay.x_center - 20 + self.x_offset, smartdisplay.y_center + self.y_offset],
                3,
            )
                pygame.draw.line(
                smartdisplay.pygamescreen,
                self.GColor,
                [smartdisplay.x_center - 35 + self.x_offset, smartdisplay.y_center + self.y_offset],
                [smartdisplay.x_center - 20 + self.x_offset, smartdisplay.y_center + self.y_offset],
                3,
            )
                pygame.draw.line(
                smartdisplay.pygamescreen,
                self.GColor,
                [smartdisplay.x_center + 10 + self.x_offset, smartdisplay.y_center + self.y_offset + 20],
                [smartdisplay.x_center  + self.x_offset, smartdisplay.y_center + self.y_offset],
                3,
            )
                pygame.draw.line(
                smartdisplay.pygamescreen,
                self.GColor,
                [smartdisplay.x_center + 10 + self.x_offset, smartdisplay.y_center + self.y_offset + 20],
                [smartdisplay.x_center + 20 + self.x_offset, smartdisplay.y_center + self.y_offset],
                3,
            )
                pygame.draw.line(
                smartdisplay.pygamescreen,
                self.GColor,
                [smartdisplay.x_center + 35 + self.x_offset, smartdisplay.y_center + self.y_offset],
                [smartdisplay.x_center + 20 + self.x_offset, smartdisplay.y_center + self.y_offset],
                3,
            )

        if self.GunSightMode == 1:
                pygame.draw.line(
                self.pygamescreen,
                self.GColor_color,
                (smartdisplay.x_center - 15, smartdisplay.y_center - 120), (smartdisplay.x_center + 15, smartdisplay.y_center - 120),
                4,
            )
                pygame.draw.line(
                self.pygamescreen,
                self.GColor_color,
                (smartdisplay.x_center, smartdisplay.y_center - 135), (smartdisplay.x_center, smartdisplay.y_center - 105),
                4,
            )
                pygame.draw.circle(
                self.pygamescreen,
                self.GColor_color,
                (
                    int(smartdisplay.x_center), 
                    int(smartdisplay.y_center - 60),
                ),
                8,
                0,
            )
                pygame.draw.circle(
                self.pygamescreen,
                self.GColor_color,
                (
                    int(smartdisplay.x_center), 
                    int(smartdisplay.y_center + 60),
                ),
                8,
                0,
            )
                pygame.draw.lines(
                self.pygamescreen,
                self.GColor_color,
                False,
                [[smartdisplay.x_center - 321, smartdisplay.y_center - 120], [smartdisplay.x_center - 160, smartdisplay.y_center - 60],
                [smartdisplay.x_center - 107, smartdisplay.y_center], [smartdisplay.x_center - 80, smartdisplay.y_center + 60], 
                [smartdisplay.x_center - 53, smartdisplay.y_center + 120], [smartdisplay.x_center - 40, smartdisplay.y_center + 180]],
                4,
            )
                pygame.draw.lines(
                self.pygamescreen,
                self.GColor_color,
                False,
                [[smartdisplay.x_center + 321, smartdisplay.y_center - 120], [smartdisplay.x_center + 160, smartdisplay.y_center - 60],
                [smartdisplay.x_center + 107, smartdisplay.y_center], [smartdisplay.x_center + 80, smartdisplay.y_center + 60], 
                [smartdisplay.x_center + 53, smartdisplay.y_center + 120], [smartdisplay.x_center + 40, smartdisplay.y_center + 180]],
                4,
            )

       
        if self.GunSightMode == 2:
                pygame.draw.line(
                self.pygamescreen,
                self.GColor_color,
                (smartdisplay.x_center - 15, smartdisplay.y_center - 120), (smartdisplay.x_center + 15, smartdisplay.y_center - 120),
                4,
            )
                pygame.draw.line(
                self.pygamescreen,
                self.GColor_color,
                (smartdisplay.x_center, smartdisplay.y_center - 135), (smartdisplay.x_center, smartdisplay.y_center - 105),
                4,
            )
                pygame.draw.circle(
                self.pygamescreen,
                self.GColor_color,
                (
                    int(smartdisplay.x_center), 
                    int(smartdisplay.y_center - 60),
                ),
                8,
                0,
            )
                pygame.draw.circle(
                self.pygamescreen,
                self.GColor_color,
                (
                    int(smartdisplay.x_center), 
                    int(smartdisplay.y_center + 60),
                ),
                8,
                0,
            )
                pygame.draw.lines(
                self.pygamescreen,
                self.GColor_color,
                False,
                [[smartdisplay.x_center - 385, smartdisplay.y_center - 120], [smartdisplay.x_center - 193, smartdisplay.y_center - 60],
                [smartdisplay.x_center - 128, smartdisplay.y_center], [smartdisplay.x_center - 96, smartdisplay.y_center + 60], 
                [smartdisplay.x_center - 64, smartdisplay.y_center + 120], [smartdisplay.x_center - 48, smartdisplay.y_center + 180]],
                4,
            )
                pygame.draw.lines(
                self.pygamescreen,
                self.GColor_color,
                False,
                [[smartdisplay.x_center + 385, smartdisplay.y_center - 120], [smartdisplay.x_center + 193, smartdisplay.y_center - 60],
                [smartdisplay.x_center + 128, smartdisplay.y_center], [smartdisplay.x_center + 96, smartdisplay.y_center + 60], 
                [smartdisplay.x_center + 64, smartdisplay.y_center + 120], [smartdisplay.x_center + 48, smartdisplay.y_center + 180]],
                4,
            )

        if self.GunSightMode == 3:
                pygame.draw.line(
                self.pygamescreen,
                self.GColor_color,
                (smartdisplay.x_center - 15, smartdisplay.y_center - 120), (smartdisplay.x_center + 15, smartdisplay.y_center - 120),
                4,
            )
                pygame.draw.line(
                self.pygamescreen,
                self.GColor_color,
                (smartdisplay.x_center, smartdisplay.y_center - 135), (smartdisplay.x_center, smartdisplay.y_center - 105),
                4,
            )
                pygame.draw.circle(
                self.pygamescreen,
                self.GColor_color,
                (
                    int(smartdisplay.x_center), 
                    int(smartdisplay.y_center - 60),
                ),
                8,
                0,
            )
                pygame.draw.circle(
                self.pygamescreen,
                self.GColor_color,
                (
                    int(smartdisplay.x_center), 
                    int(smartdisplay.y_center + 60),
                ),
                8,
                0,
            )
                pygame.draw.lines(
                self.pygamescreen,
                self.GColor_color,
                False,
                [[smartdisplay.x_center - 449, smartdisplay.y_center - 120], [smartdisplay.x_center - 225, smartdisplay.y_center - 60],
                [smartdisplay.x_center - 150, smartdisplay.y_center], [smartdisplay.x_center - 112, smartdisplay.y_center + 60], 
                [smartdisplay.x_center - 75, smartdisplay.y_center + 120], [smartdisplay.x_center - 56, smartdisplay.y_center + 180]],
                4,
            )
                pygame.draw.lines(
                self.pygamescreen,
                self.GColor_color,
                False,
                [[smartdisplay.x_center + 449, smartdisplay.y_center - 120], [smartdisplay.x_center + 225, smartdisplay.y_center - 60],
                [smartdisplay.x_center + 150, smartdisplay.y_center], [smartdisplay.x_center + 112, smartdisplay.y_center + 60], 
                [smartdisplay.x_center + 75, smartdisplay.y_center + 120], [smartdisplay.x_center + 56, smartdisplay.y_center + 180]],
                4,
            )

            # End Gun Cross Funnel  -------------------------------

	# Start Gun Director Mode
        if self.GunSightMode == 4:
                pygame.draw.line(
                self.pygamescreen,
                self.GColor_color,
                (smartdisplay.x_center - 15, smartdisplay.y_center - 120), (smartdisplay.x_center + 15, smartdisplay.y_center - 120),
                4,
            )
                pygame.draw.line(
                self.pygamescreen,
                self.GColor_color,
                (smartdisplay.x_center, smartdisplay.y_center - 135), (smartdisplay.x_center, smartdisplay.y_center - 105),
                4,
            )
                pygame.draw.lines(
                self.pygamescreen,
                (255, 255, 255),      #  Bullet line color,
                False,
                [[smartdisplay.x_center + 0, smartdisplay.y_center - 120], [smartdisplay.x_center - (5 * aircraft.fpv_x), smartdisplay.y_center + 180]],
                2,
            )

            
                if traffic_nm <= 1.5:
                    gun_rng = ((270 * traffic_nm) / 1.5)  # gun_director in decressing range in degrees

                    gun_arc = ((270 - gun_rng) + 180)   # changing to pygame arc in degrees
                    if gun_arc > 360: 
                        gun_arc = gun_arc-360    
                        
                    pygame.draw.circle(screen, color, pipper_posn, circle_radius, line_width)    # Draw the gun circle

                    pygame.draw.circle(screen, color, pipper_posn, circle_radius_ctrdot)  # Draw the green gun pipper

                    start_angle = math.radians(gun_arc)  # Gun Range ARC is drawn counterclockwise in degrees from start angle to the Zero Range "end_angle"
                    end_angle = math.radians(90)
                    start_pos = (pipper_posn[0] + arc_radius * math.cos(start_angle), pipper_posn[1] + arc_radius * math.sin(start_angle))
                    end_pos = (pipper_posn[0] + arc_radius * math.cos(end_angle), pipper_posn[1] + arc_radius * math.sin(end_angle))
                    pygame.draw.arc(screen, color, (pipper_posn[0] - arc_radius, pipper_posn[1] - arc_radius, arc_radius * 2, arc_radius * 2), start_angle, end_angle, 5)


                    green_arc_radius = arc_radius - 5   # Draw the green range Tick Mark at beginning of Range Arc
                    green_arc_width = 15
                    start_angle = math.radians(gun_arc)
                    end_angle = math.radians(gun_arc+5)
                    start_pos = (pipper_posn[0] + green_arc_radius * math.cos(start_angle), pipper_posn[1] + green_arc_radius * math.sin(start_angle))
                    end_pos = (pipper_posn[0] + green_arc_radius * math.cos(end_angle), pipper_posn[1] + green_arc_radius * math.sin(end_angle))
                    pygame.draw.arc(screen, color, (pipper_posn[0] - green_arc_radius, pipper_posn[1] - green_arc_radius, green_arc_radius * 2, green_arc_radius * 2), start_angle, end_angle, green_arc_width)

             # end of gun director
#  -----------------------------------------------------
			


    # cycle through the modes.
    def cycleGunSight(self):
        self.GunSightMode = self.GunSightMode + 1
        if (self.GunSightMode > 4):
	        self.GunSightMode = 0
        # based on mode show a different target wing span.
        if (self.GunSightMode == 1):
            self.TargetWingSpan = 25
        elif (self.GunSightMode == 2):
            self.TargetWingSpan = 30
        elif (self.GunSightMode == 3):
            self.TargetWingSpan = 35


    # called before screen draw.  To clear the screen to your favorite color.
    def clear(self):
        #self.ahrs_bg.fill((0, 0, 0))  # clear screen
        print("clear")

    # handle key events
    def processEvent(self, event):
        print("processEvent")


# vi: modeline tabstop=8 expandtab shiftwidth=4 softtabstop=4 syntax=python

