#!/usr/bin/env python

#################################################
# Module: Heading
# Topher 2021.
# Adapted from hdg code by Brian Chesteen.

from lib.modules._module import Module
from lib import hud_graphics
from lib import hud_utils
from lib import smartdisplay
from lib import aircraft
import pygame
import math


class heading(Module):
    # called only when object is first created.
    def __init__(self):
        Module.__init__(self)
        self.name = "Heading"  # set name
        self.x_offset = 0

    # called once for setup
    def initMod(self, pygamescreen, width, height):
        Module.initMod(
            self, pygamescreen, width, height
        )  # call parent init screen.
        print(("Init Mod: %s %dx%d"%(self.name,self.width,self.height)))

        self.myfont1 = pygame.font.SysFont("Comic Sans MS", 30, bold=True)  # hsi font
        self.MainColor = (0, 255, 0)  # main color 

    # setup must have defaults for all parameters
    def setup(self, label_color= (255, 255, 0)):

        self.myfont = pygame.font.SysFont("Arial", 20, bold=True)
        self.myfont1 = pygame.font.SysFont("Arial", 30, bold=True)

        # Setup mask
        self.mask = pygame.Surface((66, 30))
        self.mask.fill((0, 0, 0))

        # hdg Setup
        self.label_color = label_color
        self.hdg = pygame.Surface((360, 80))
        self.hdg_rect = self.hdg.get_rect()
        self.hdg.fill((0, 0, 0))
        self.hdg1 = pygame.Surface((640, 80))
        self.hdg1.fill((0, 0, 0))
        self.trk = pygame.Surface((640, 80), pygame.SRCALPHA)

        ## Setup Labels
        self.N = self.myfont.render("360", False, self.label_color)
        self.N_rect = self.N.get_rect()
        self.R1 = self.myfont.render("010", False, self.label_color)
        self.R1_rect = self.R1.get_rect()
        self.R2 = self.myfont.render("020", False, self.label_color)
        self.R2_rect = self.R2.get_rect()
        self.R3 = self.myfont.render("030", False, self.label_color)
        self.R3_rect = self.R3.get_rect()
        self.R4 = self.myfont.render("040", False, self.label_color)
        self.R4_rect = self.R4.get_rect()
        self.R5 = self.myfont.render("050", False, self.label_color)
        self.R5_rect = self.R5.get_rect()
        self.R6 = self.myfont.render("060", False, self.label_color)
        self.R6_rect = self.R6.get_rect()
        self.R7 = self.myfont.render("070", False, self.label_color)
        self.R7_rect = self.R7.get_rect()
        self.R8 = self.myfont.render("080", False, self.label_color)
        self.R8_rect = self.R8.get_rect()
        self.E = self.myfont.render("090", False, self.label_color)
        self.E_rect = self.E.get_rect()
        self.R10 = self.myfont.render("100", False, self.label_color)
        self.R10_rect = self.R10.get_rect()
        self.R11 = self.myfont.render("110", False, self.label_color)
        self.R11_rect = self.R11.get_rect()
        self.R12 = self.myfont.render("120", False, self.label_color)
        self.R12_rect = self.R12.get_rect()
        self.R13 = self.myfont.render("130", False, self.label_color)
        self.R13_rect = self.R13.get_rect()
        self.R14 = self.myfont.render("140", False, self.label_color)
        self.R14_rect = self.R13.get_rect()
        self.R15 = self.myfont.render("150", False, self.label_color)
        self.R15_rect = self.R15.get_rect()
        self.R16 = self.myfont.render("160", False, self.label_color)
        self.R16_rect = self.R16.get_rect()
        self.R17 = self.myfont.render("170", False, self.label_color)
        self.R17_rect = self.R17.get_rect()
        self.S = self.myfont.render("180", False, self.label_color)
        self.S_rect = self.S.get_rect()
        self.R19 = self.myfont.render("190", False, self.label_color)
        self.R19_rect = self.R19.get_rect()
        self.R20 = self.myfont.render("200", False, self.label_color)
        self.R20_rect = self.R20.get_rect()
        self.R21 = self.myfont.render("210", False, self.label_color)
        self.R21_rect = self.R21.get_rect()
        self.R22 = self.myfont.render("220", False, self.label_color)
        self.R22_rect = self.R22.get_rect()
        self.R23 = self.myfont.render("230", False, self.label_color)
        self.R23_rect = self.R23.get_rect()
        self.R24 = self.myfont.render("240", False, self.label_color)
        self.R24_rect = self.R24.get_rect()
        self.R25 = self.myfont.render("250", False, self.label_color)
        self.R25_rect = self.R25.get_rect()
        self.R26 = self.myfont.render("260", False, self.label_color)
        self.R26_rect = self.R26.get_rect()
        self.W = self.myfont.render("270", False, self.label_color)
        self.W_rect = self.W.get_rect()
        self.R28 = self.myfont.render("280", False, self.label_color)
        self.R28_rect = self.R28.get_rect()
        self.R29 = self.myfont.render("290", False, self.label_color)
        self.R29_rect = self.R29.get_rect()
        self.R30 = self.myfont.render("300", False, self.label_color)
        self.R30_rect = self.R30.get_rect()
        self.R31 = self.myfont.render("310", False, self.label_color)
        self.R31_rect = self.R31.get_rect()
        self.R32 = self.myfont.render("320", False, self.label_color)
        self.R32_rect = self.R32.get_rect()
        self.R33 = self.myfont.render("330", False, self.label_color)
        self.R33_rect = self.R33.get_rect()
        self.R34 = self.myfont.render("340", False, self.label_color)
        self.R34_rect = self.R34.get_rect()
        self.R35 = self.myfont.render("350", False, self.label_color)
        self.R35_rect = self.R35.get_rect()

        self.old_hdg_hdg = None
        self.old_gnd_trk = None


    def roint(self,num):
        return int(round(num))


    # called every redraw for the mod
    def draw(self, aircraft, smartdisplay, pos=(None, None)):


        if pos[0] is None:
            x = 0
            y = 0 
        else:
            x = pos[0]
            y = pos[1]         

        hdg_hdg = aircraft.mag_head
        gnd_trk = self.roint(aircraft.gndtrack)

        if (
            self.old_hdg_hdg != hdg_hdg or self.old_gnd_trk != gnd_trk
        ):  # Don't waste time recalculating/redrawing until the variable changes

            ## Draw Labels
            q = (-hdg_hdg) % 360
            d = (-q + 5) * 12
            p = q * 12
            t = p - (((-gnd_trk) % 360) * 12) % 4320

            self.hdg = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
            self.trk = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
            for hdg_ticks in range(44):
                x0 = self.roint(hdg_ticks * 120)
                y0 = self.roint(30)
                x1 = self.roint(hdg_ticks * 120)
                y1 = self.roint(60)

                pygame.draw.line(
                    self.hdg, (0, 255, 0), [x0 - 4440 - d, y0], [x1 - 4440 - d, y1], 3
                )

            for hdg_lticks in range(88):
                x3 = self.roint(hdg_lticks * 60)
                y3 = self.roint(45)
                x4 = self.roint(hdg_lticks * 60)
                y4 = self.roint(60)
                pygame.draw.line(
                    self.hdg, (0, 255, 0), [x3 - 4440 - d, y3], [x4 - 4440 - d, y4], 3
                )

            for hdg_tick_label in range(641):
                x2 = self.roint(hdg_tick_label)
                y2 = self.roint(30)
                if hdg_tick_label == (t + 320) % 4320:
                    pygame.draw.line(self.trk, (255, 0, 255), [x2, 60], [x2, 80], 3)
                    pygame.draw.line(
                        self.trk, (255, 0, 255), [x2 - 10, 60], [x2 + 10, 60], 3
                    )
                if hdg_tick_label == (p + 180) % 4320:
                    self.hdg.blit(
                        self.N,
                        (x2 - self.N_rect.center[0], y2 - self.N_rect.center[1] - 12),
                    )
                if hdg_tick_label == (p + 300) % 4320:
                    self.hdg.blit(
                        self.R1,
                        (x2 - self.R1_rect.center[0], y2 - self.R1_rect.center[1] - 12),
                    )
                if hdg_tick_label == (p + 420) % 4320:
                    self.hdg.blit(
                        self.R2,
                        (x2 - self.R2_rect.center[0], y2 - self.R2_rect.center[1] - 12),
                    )
                if hdg_tick_label == (p + 540) % 4320:
                    self.hdg.blit(
                        self.R3,
                        (x2 - self.R3_rect.center[0], y2 - self.R3_rect.center[1] - 12),
                    )
                if hdg_tick_label == (p + 660) % 4320:
                    self.hdg.blit(
                        self.R4,
                        (x2 - self.R4_rect.center[0], y2 - self.R4_rect.center[1] - 12),
                    )
                if hdg_tick_label == (p + 780) % 4320:
                    self.hdg.blit(
                        self.R5,
                        (x2 - self.R5_rect.center[0], y2 - self.R5_rect.center[1] - 12),
                    )
                if hdg_tick_label == (p + 900) % 4320:
                    self.hdg.blit(
                        self.R6,
                        (x2 - self.R6_rect.center[0], y2 - self.R6_rect.center[1] - 12),
                    )
                if hdg_tick_label == (p + 1020) % 4320:
                    self.hdg.blit(
                        self.R7,
                        (x2 - self.R7_rect.center[0], y2 - self.R7_rect.center[1] - 12),
                    )
                if hdg_tick_label == (p + 1140) % 4320:
                    self.hdg.blit(
                        self.R8,
                        (x2 - self.R8_rect.center[0], y2 - self.R8_rect.center[1] - 12),
                    )
                if hdg_tick_label == (p + 1260) % 4320:
                    self.hdg.blit(
                        self.E,
                        (x2 - self.E_rect.center[0], y2 - self.E_rect.center[1] - 12),
                    )
                if hdg_tick_label == (p + 1380) % 4320:
                    self.hdg.blit(
                        self.R10,
                        (x2 - self.R10_rect.center[0], y2 - self.R10_rect.center[1] - 12),
                    )
                if hdg_tick_label == (p + 1500) % 4320:
                    self.hdg.blit(
                        self.R11,
                        (x2 - self.R11_rect.center[0], y2 - self.R11_rect.center[1] - 12),
                    )
                if hdg_tick_label == (p + 1620) % 4320:
                    self.hdg.blit(
                        self.R12,
                        (x2 - self.R12_rect.center[0], y2 - self.R12_rect.center[1] - 12),
                    )
                if hdg_tick_label == (p + 1740) % 4320:
                    self.hdg.blit(
                        self.R13,
                        (x2 - self.R13_rect.center[0], y2 - self.R13_rect.center[1] - 12),
                    )
                if hdg_tick_label == (p + 1860) % 4320:
                    self.hdg.blit(
                        self.R14,
                        (x2 - self.R14_rect.center[0], y2 - self.R14_rect.center[1] - 12),
                    )
                if hdg_tick_label == (p + 1980) % 4320:
                    self.hdg.blit(
                        self.R15,
                        (x2 - self.R15_rect.center[0], y2 - self.R15_rect.center[1] - 12),
                    )
                if hdg_tick_label == (p + 2100) % 4320:
                    self.hdg.blit(
                        self.R16,
                        (x2 - self.R16_rect.center[0], y2 - self.R16_rect.center[1] - 12),
                    )
                if hdg_tick_label == (p + 2220) % 4320:
                    self.hdg.blit(
                        self.R17,
                        (x2 - self.R17_rect.center[0], y2 - self.R17_rect.center[1] - 12),
                    )
                if hdg_tick_label == (p + 2340) % 4320:
                    self.hdg.blit(
                        self.S,
                        (x2 - self.S_rect.center[0], y2 - self.S_rect.center[1] - 12),
                    )
                if hdg_tick_label == (p + 2460) % 4320:
                    self.hdg.blit(
                        self.R19,
                        (x2 - self.R19_rect.center[0], y2 - self.R19_rect.center[1] - 12),
                    )
                if hdg_tick_label == (p + 2580) % 4320:
                    self.hdg.blit(
                        self.R20,
                        (x2 - self.R20_rect.center[0], y2 - self.R20_rect.center[1] - 12),
                    )
                if hdg_tick_label == (p + 2700) % 4320:
                    self.hdg.blit(
                        self.R21,
                        (x2 - self.R21_rect.center[0], y2 - self.R21_rect.center[1] - 12),
                    )
                if hdg_tick_label == (p + 2820) % 4320:
                    self.hdg.blit(
                        self.R22,
                        (x2 - self.R22_rect.center[0], y2 - self.R22_rect.center[1] - 12),
                    )
                if hdg_tick_label == (p + 2940) % 4320:
                    self.hdg.blit(
                        self.R23,
                        (x2 - self.R23_rect.center[0], y2 - self.R23_rect.center[1] - 12),
                    )
                if hdg_tick_label == (p + 3060) % 4320:
                    self.hdg.blit(
                        self.R24,
                        (x2 - self.R24_rect.center[0], y2 - self.R24_rect.center[1] - 12),
                    )
                if hdg_tick_label == (p + 3180) % 4320:
                    self.hdg.blit(
                        self.R25,
                        (x2 - self.R25_rect.center[0], y2 - self.R25_rect.center[1] - 12),
                    )
                if hdg_tick_label == (p + 3300) % 4320:
                    self.hdg.blit(
                        self.R26,
                        (x2 - self.R26_rect.center[0], y2 - self.R26_rect.center[1] - 12),
                    )
                if hdg_tick_label == (p + 3420) % 4320:
                    self.hdg.blit(
                        self.W,
                        (x2 - self.W_rect.center[0], y2 - self.W_rect.center[1] - 12),
                    )
                if hdg_tick_label == (p + 3540) % 4320:
                    self.hdg.blit(
                        self.R28,
                        (x2 - self.R28_rect.center[0], y2 - self.R28_rect.center[1] - 12),
                    )
                if hdg_tick_label == (p + 3660) % 4320:
                    self.hdg.blit(
                        self.R29,
                        (x2 - self.R29_rect.center[0], y2 - self.R29_rect.center[1] - 12),
                    )
                if hdg_tick_label == (p + 3780) % 4320:
                    self.hdg.blit(
                        self.R30,
                        (x2 - self.R30_rect.center[0], y2 - self.R30_rect.center[1] - 12),
                    )
                if hdg_tick_label == (p + 3900) % 4320:
                    self.hdg.blit(
                        self.R31,
                        (x2 - self.R31_rect.center[0], y2 - self.R31_rect.center[1] - 12),
                    )
                if hdg_tick_label == (p + 4020) % 4320:
                    self.hdg.blit(
                        self.R32,
                        (x2 - self.R32_rect.center[0], y2 - self.R32_rect.center[1] - 12),
                    )
                if hdg_tick_label == (p + 4140) % 4320:
                    self.hdg.blit(
                        self.R33,
                        (x2 - self.R33_rect.center[0], y2 - self.R33_rect.center[1] - 12),
                    )
                if hdg_tick_label == (p + 4260) % 4320:
                    self.hdg.blit(
                        self.R34,
                        (x2 - self.R34_rect.center[0], y2 - self.R34_rect.center[1] - 12),
                    )
                if hdg_tick_label == (p + 4380) % 4320:
                    self.hdg.blit(
                        self.R35,
                        (x2 - self.R35_rect.center[0], y2 - self.R35_rect.center[1] - 12),
                    )

            pygame.draw.line(self.hdg, (0, 255, 0), [self.width//2 - 10, 80], [self.width//2, 60], 3)
            pygame.draw.line(self.hdg, (0, 255, 0), [self.width//2, 60], [self.width//2 + 10, 80], 3)

            self.old_hdg_hdg = hdg_hdg
            self.old_gnd_trk = gnd_trk
        
        drawPos = (smartdisplay.x_center - self.width//2 + self.x_offset, smartdisplay.y_start)

        if x != 0:
            drawPos = (x, y)
            
        self.pygamescreen.blit(self.hdg, drawPos)

    # called before screen draw.  To clear the screen to your favorite color.
    def clear(self):
        #self.ahrs_bg.fill((0, 0, 0))  # clear screen
        print("clear")

    # handle key events
    def processEvent(self, event):
        print("processEvent")


# vi: modeline tabstop=8 expandtab shiftwidth=4 softtabstop=4 syntax=python
