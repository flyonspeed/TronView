#!/usr/bin/env python

#################################################
# Module: HSI
# Topher 2021.
# Adapted from hsi code by Brian Chesteen.

from lib.modules._module import Module
from lib import hud_graphics
from lib import hud_utils
from lib import smartdisplay
from lib import aircraft
import pygame
import math


class hsi(Module):
    # called only when object is first created.
    def __init__(self):
        Module.__init__(self)
        self.name = "HSI"  # set name
        self.x_offset = 0

    # called once for setup
    def initMod(self, pygamescreen, width=None, height=None):
        if width is None:
            width = 500 # default width
        if height is None:
            height = 500 # default height
        Module.initMod(
            self, pygamescreen, width, height
        )  # call parent init screen.
        print(("Init Mod: %s %dx%d"%(self.name,self.width,self.height)))

        self.myfont1 = pygame.font.SysFont("Comic Sans MS", 30, bold=True)  # hsi font
        self.MainColor = (0, 255, 0)  # main color 

    # setup must have default values for all parameters
    def setup(self, hsi_size = -1 , gnd_trk_tick_size = -1, rose_color = (70,130,40), label_color = (255, 255, 0)):
        print("HSI setup() %d %d %s %s" % (hsi_size, gnd_trk_tick_size, rose_color, label_color))
        if(hsi_size == -1):
            hsi_size = self.width
        if(gnd_trk_tick_size == -1):
            gnd_trk_tick_size = self.width / 10

        # HSI Setup
        self.hsi_size = hsi_size
        self.gnd_trk_tick_size = gnd_trk_tick_size
        self.color = rose_color
        self.label_color = label_color
        self.rose = pygame.Surface((self.hsi_size, self.hsi_size), pygame.SRCALPHA)
        self.labels = pygame.Surface((self.hsi_size, self.hsi_size), pygame.SRCALPHA)
        self.ticks = pygame.Surface((self.hsi_size, self.hsi_size), pygame.SRCALPHA)

        self.old_hsi_hdg = None

        # Setup Compass Rose
        # Minor Tick Marks
        for little_tick in range(72):
            cos = math.cos(math.radians(360.0 / 72 * little_tick))
            sin = math.sin(math.radians(360.0 / 72 * little_tick))
            x0 = self.roint(self.hsi_size / 2 + self.hsi_size / 13 * cos * 4)
            y0 = self.roint(self.hsi_size / 2 + self.hsi_size / 13 * sin * 4)
            x1 = self.roint(self.hsi_size / 2 + self.hsi_size / 3 * cos)
            y1 = self.roint(self.hsi_size / 2 + self.hsi_size / 3 * sin)
            pygame.draw.line(self.rose, self.color, [x0, y0], [x1, y1], 4)

        # Setup Compass Rose
        # Major Tick Marks
        for big_tick in range(36):
            cos = math.cos(math.radians(360.0 / 36 * big_tick))
            sin = math.sin(math.radians(360.0 / 36 * big_tick))
            x0 = self.roint(self.hsi_size / 2 + self.hsi_size / 15 * cos * 4)
            y0 = self.roint(self.hsi_size / 2 + self.hsi_size / 15 * sin * 4)
            x1 = self.roint(self.hsi_size / 2 + self.hsi_size / 2.8 * cos)
            y1 = self.roint(self.hsi_size / 2 + self.hsi_size / 2.8 * sin)
            pygame.draw.line(self.rose, self.color, [x0, y0], [x1, y1], 4)

        # Setup Labels
        self.N = self.myfont1.render("N", False, self.label_color)
        self.N_rect = self.N.get_rect()
        self.R3 = self.myfont1.render("3", False, self.label_color)
        self.R3_rect = self.R3.get_rect()
        self.R6 = self.myfont1.render("6", False, self.label_color)
        self.R6_rect = self.R6.get_rect()
        self.E = self.myfont1.render("E", False, self.label_color)
        self.E_rect = self.E.get_rect()
        self.R12 = self.myfont1.render("12", False, self.label_color)
        self.R12_rect = self.R12.get_rect()
        self.R15 = self.myfont1.render("15", False, self.label_color)
        self.R15_rect = self.R15.get_rect()
        self.S = self.myfont1.render("S", False, self.label_color)
        self.S_rect = self.S.get_rect()
        self.R21 = self.myfont1.render("21", False, self.label_color)
        self.R21_rect = self.R21.get_rect()
        self.R24 = self.myfont1.render("24", False, self.label_color)
        self.R24_rect = self.R24.get_rect()
        self.W = self.myfont1.render("W", False, self.label_color)
        self.W_rect = self.W.get_rect()
        self.R30 = self.myfont1.render("30", False, self.label_color)
        self.R30_rect = self.R30.get_rect()
        self.R33 = self.myfont1.render("33", False, self.label_color)
        self.R33_rect = self.R33.get_rect()

        # Setup Ground Track Tick
        self.gnd_trk_tick = pygame.image.load("lib/modules/hud/hsi/tick_m.png").convert()
        self.gnd_trk_tick.set_colorkey((255, 255, 255))
        self.gnd_trk_tick_scaled = pygame.transform.scale(
            self.gnd_trk_tick, (self.gnd_trk_tick_size, self.gnd_trk_tick_size)
        )
        self.gnd_trk_tick_scaled_rect = self.gnd_trk_tick_scaled.get_rect()

        self.ticks.fill(pygame.SRCALPHA)
        self.ticks.blit(
            self.gnd_trk_tick_scaled,
            (
                (self.hsi_size / 2) - self.gnd_trk_tick_scaled_rect.center[0],
                (self.hsi_size / 2) - 130 - self.gnd_trk_tick_scaled_rect[1],
            ),
        )

    def roint(self,num):
        return int(round(num))

    # Create HSI label coordinates
    def labeler(self, hsi_hdg):
        self.labels.fill(pygame.SRCALPHA)
        for label in range(360):
            cos = math.cos(math.radians(label))
            sin = math.sin(math.radians(label))
            y = self.roint(self.hsi_size / 2 + self.hsi_size / 2.5 * cos)
            x = self.roint(self.hsi_size / 2 + self.hsi_size / 2.5 * sin)

            if label == hsi_hdg:
                self.labels.blit(
                    self.E, (x - self.E_rect.center[0], y - self.E_rect.center[1])
                )
            if label == (hsi_hdg + 330) % 360:
                self.labels.blit(
                    self.R12, (x - self.R12_rect.center[0], y - self.R12_rect.center[1])
                )
            if label == (hsi_hdg + 300) % 360:
                self.labels.blit(
                    self.R15, (x - self.R15_rect.center[0], y - self.R15_rect.center[1])
                )
            if label == (hsi_hdg + 270) % 360:
                self.labels.blit(
                    self.S, (x - self.S_rect.center[0], y - self.S_rect.center[1])
                )
            if label == (hsi_hdg + 240) % 360:
                self.labels.blit(
                    self.R21, (x - self.R21_rect.center[0], y - self.R21_rect.center[1])
                )
            if label == (hsi_hdg + 210) % 360:
                self.labels.blit(
                    self.R24, (x - self.R24_rect.center[0], y - self.R24_rect.center[1])
                )
            if label == (hsi_hdg + 180) % 360:
                self.labels.blit(
                    self.W, (x - self.W_rect.center[0], y - self.W_rect.center[1])
                )
            if label == (hsi_hdg + 150) % 360:
                self.labels.blit(
                    self.R30, (x - self.R30_rect.center[0], y - self.R30_rect.center[1])
                )
            if label == (hsi_hdg + 120) % 360:
                self.labels.blit(
                    self.R33, (x - self.R33_rect.center[0], y - self.R33_rect.center[1])
                )
            if label == (hsi_hdg + 90) % 360:
                self.labels.blit(
                    self.N, (x - self.N_rect.center[0], y - self.N_rect.center[1])
                )
            if label == (hsi_hdg + 60) % 360:
                self.labels.blit(
                    self.R3, (x - self.R3_rect.center[0], y - self.R3_rect.center[1])
                )
            if label == (hsi_hdg + 30) % 360:
                self.labels.blit(
                    self.R6, (x - self.R6_rect.center[0], y - self.R6_rect.center[1])
                )

    def gnd_trk_tick(self, smartdisplay, gnd_trk):
        #Draw Ground Track Tick
        gnd_trk_tick_rotated = pygame.transform.rotate(self.ticks, gnd_trk)
        gnd_trk__rect = gnd_trk_tick_rotated.get_rect()
        self.pygamescreen.blit(
            gnd_trk_tick_rotated,
            (
                smartdisplay.x_center - gnd_trk__rect.center[0],
                smartdisplay.y_center - gnd_trk__rect.center[1],
            ),
        )
        pass


    def turn_rate_disp(self, smartdisplay,turn_rate, pos=(None, None)):
        if pos[0] is not None:
            draw_x = pos[0] + self.width / 2
        else:
            draw_x = smartdisplay.x_center
        if pos[1] is not None:
            draw_y = pos[1] + self.height / 2
        else:
            draw_y = smartdisplay.y_center
        if abs(turn_rate) > 0.2:
            pygame.draw.line(
                self.pygamescreen,
                (255, 0, 255),
                (draw_x, draw_y - 158),
                (draw_x + (turn_rate * 10), draw_y - 158),
                10,
            )
        pygame.draw.line(
            self.pygamescreen,
            (255, 255, 255),
            (draw_x + 31, draw_y - 153),
            (draw_x + 31, draw_y - 163),
            3,
        )
        pygame.draw.line(
            self.pygamescreen,
            (255, 255, 255),
            (draw_x - 31, draw_y - 153),
            (draw_x - 31, draw_y - 163),
            3,
        )
        pygame.draw.line(
            self.pygamescreen,
            (0, 0, 0),
            (draw_x + 33, draw_y - 153),
            (draw_x + 33, draw_y - 163),
            1,
        )
        pygame.draw.line(
            self.pygamescreen,
            (0, 0, 0),
            (draw_x + 29, draw_y - 153),
            (draw_x + 29, draw_y - 163),
            1,
        )
        pygame.draw.line(
            self.pygamescreen,
            (0, 0, 0),
            (draw_x - 33, draw_y - 153),
            (draw_x - 33, draw_y - 163),
            1,
        )
        pygame.draw.line(
            self.pygamescreen,
            (0, 0, 0),
            (draw_x - 29, draw_y - 153),
            (draw_x - 29, draw_y - 163),
            1,
        )


    # called every redraw for the mod
    def draw(self, aircraft, smartdisplay, pos=(None, None)):

        x_pos = smartdisplay.x_center
        y_pos = smartdisplay.y_center
        if pos[0] is not None:
            x_pos = pos[0] + self.width / 2  # center the hsi in the middle of this module
        if pos[1] is not None:
            y_pos = pos[1] + self.height / 2

        hsi_hdg = aircraft.mag_head
        gnd_trk = aircraft.gndtrack
        turn_rate = aircraft.turn_rate

        hsi_hdg = (hsi_hdg + 90) % 360
        gnd_trk = self.roint(hsi_hdg - gnd_trk - 90) % 360

        # Draw Compass Rose Tick Marks
        tick_rotated = pygame.transform.rotate(self.rose, hsi_hdg)
        tick_rect = tick_rotated.get_rect()
        self.pygamescreen.blit(
            tick_rotated,
            (x_pos - tick_rect.center[0], y_pos - tick_rect.center[1]),
        )

        # Draw Labels
        #if self.old_hsi_hdg != None and self.old_hsi_hdg != hsi_hdg :  # Don't waste time recalculating/redrawing until the variable changes
        self.labeler(hsi_hdg)
        label_rect = self.labels.get_rect()
        self.pygamescreen.blit(
            self.labels,
            (x_pos - label_rect.center[0], y_pos - label_rect.center[1]),
        )
        #self.old_hsi_hdg = hsi_hdg  # save the last heading.

        # Draw Ticks
        #self.gnd_trk_tick(smartdisplay,gnd_trk)

        # Draw Turn Rate
        self.turn_rate_disp(smartdisplay,turn_rate, pos)


    # called before screen draw.  To clear the screen to your favorite color.
    def clear(self):
        #self.ahrs_bg.fill((0, 0, 0))  # clear screen
        print("clear")

    # handle key events
    def processEvent(self, event):
        print("processEvent")


# vi: modeline tabstop=8 expandtab shiftwidth=4 softtabstop=4 syntax=python
