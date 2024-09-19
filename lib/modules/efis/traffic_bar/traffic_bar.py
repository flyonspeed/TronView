#!/usr/bin/env python

#################################################
# Module: Traffic Bar
# Topher 2024

from lib.modules._module import Module
from lib import hud_graphics
from lib import hud_utils
from lib import smartdisplay
from lib import aircraft
import pygame
import math


class traffic_bar(Module):
    # called only when object is first created.
    def __init__(self):
        Module.__init__(self)
        self.name = "Traffic Bar"  # set name

    # called once for setup
    def initMod(self, pygamescreen, width, height):
        Module.initMod(
            self, pygamescreen, width, height
        )  # call parent init screen.
        print(("Init Mod: %s %dx%d"%(self.name,self.width,self.height)))
        target_font_size = hud_utils.readConfigInt("HUD", "target_font_size", 40)

        # fonts
        self.font_target = pygame.font.SysFont(None, target_font_size)

        # Create a surface with per-pixel alpha
        self.surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)

        # traffic range
        self.showTrafficMiles = hud_utils.readConfigInt("HUD", "show_traffic_within_miles", 25)

        self.fov_x = hud_utils.readConfigInt("HUD", "fov_x", 13.942)
        self.fov_x_each_side = self.fov_x / 2
        self.x_degree_per_pixel = self.fov_x / self.width


    # called every redraw for the mod
    def draw(self, aircraft, smartdisplay, pos=(0, 0)):
        x, y = pos
        
        # Clear the surface with full transparency
        self.surface.fill((0, 0, 0, 0))
        
        useHeading = aircraft.mag_head # use magnetic heading if available.

        if useHeading is None: # if no mag head, use gps ground track.
            useHeading = aircraft.gps.GndTrack

        # Traffic rendering (adjust for new position)
        if useHeading is not None and self.showTrafficMiles > 0:
            for t in aircraft.traffic.targets:
                if t.dist is not None and t.dist < self.showTrafficMiles:
                    result = useHeading - t.brng
                    if -self.fov_x_each_side < result < self.fov_x_each_side:
                        center_deg = result + self.fov_x_each_side
                        x_offset = self.width - (center_deg / self.x_degree_per_pixel)

                        # draw distance and altitude
                        txtTargetDist = self.font_target.render(f"{t.dist:.2f}mi {t.alt}ft", False, (0,0,0), (255,200,130))
                        text_widthD, text_heightD = txtTargetDist.get_size()
                        self.surface.blit(txtTargetDist, (x + x_offset - int(text_widthD/2), self.height - text_heightD))

                        # draw callsign
                        textTargetCall = self.font_target.render(str(t.callsign), False, (0,0,0), (255,200,130))
                        text_widthC, text_heightC = textTargetCall.get_size()
                        self.surface.blit(textTargetCall, (x + x_offset - int(text_widthC/2), self.height - text_heightC - text_heightD))

        # Use alpha blending when blitting to the screen
        smartdisplay.pygamescreen.blit(self.surface, pos, special_flags=pygame.BLEND_ALPHA_SDL2)



    def clear(self):
        #self.ahrs_bg.fill((0, 0, 0))  # clear screen
        print("clear")

    # handle key events
    def processEvent(self, event):
        print("processEvent")

# vi: modeline tabstop=8 expandtab shiftwidth=4 softtabstop=4 syntax=python
