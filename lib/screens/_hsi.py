#!/usr/bin/env python

###########################################
## HSI Module by Brian Chesteen. 02/08/2019

from __future__ import print_function
import pygame
import math


def hsi_init(self, hsi_size, gnd_trk_tick_size, rose_color, label_color):
    self.myfont1 = pygame.font.SysFont("Comic Sans MS", 30, bold=True)  # hsi

    # HSI Setup
    self.hsi_size = hsi_size
    self.gnd_trk_tick_size = gnd_trk_tick_size
    self.color = rose_color
    self.label_color = label_color
    self.rose = pygame.Surface((self.hsi_size, self.hsi_size), pygame.SRCALPHA)
    self.labels = pygame.Surface((self.hsi_size, self.hsi_size), pygame.SRCALPHA)
    self.ticks = pygame.Surface((self.hsi_size, self.hsi_size), pygame.SRCALPHA)

    global old_hsi_hdg
    old_hsi_hdg = None

    # Setup Compass Rose
    # Minor Tick Marks
    for little_tick in range(72):
        cos = math.cos(math.radians(360.0 / 72 * little_tick))
        sin = math.sin(math.radians(360.0 / 72 * little_tick))
        x0 = roint(self.hsi_size / 2 + self.hsi_size / 13 * cos * 4)
        y0 = roint(self.hsi_size / 2 + self.hsi_size / 13 * sin * 4)
        x1 = roint(self.hsi_size / 2 + self.hsi_size / 3 * cos)
        y1 = roint(self.hsi_size / 2 + self.hsi_size / 3 * sin)
        pygame.draw.line(self.rose, self.color, [x0, y0], [x1, y1], 4)

    # Setup Compass Rose
    # Major Tick Marks
    for big_tick in range(36):
        cos = math.cos(math.radians(360.0 / 36 * big_tick))
        sin = math.sin(math.radians(360.0 / 36 * big_tick))
        x0 = roint(self.hsi_size / 2 + self.hsi_size / 15 * cos * 4)
        y0 = roint(self.hsi_size / 2 + self.hsi_size / 15 * sin * 4)
        x1 = roint(self.hsi_size / 2 + self.hsi_size / 2.8 * cos)
        y1 = roint(self.hsi_size / 2 + self.hsi_size / 2.8 * sin)
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
    self.gnd_trk_tick = pygame.image.load("lib/screens/_images/tick_m.png").convert()
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


def roint(num):
    return int(round(num))


# Create HSI label coordinates
def labeler(self, hsi_hdg):
    self.labels.fill(pygame.SRCALPHA)
    for label in range(360):
        cos = math.cos(math.radians(label))
        sin = math.sin(math.radians(label))
        y = roint(self.hsi_size / 2 + self.hsi_size / 2.5 * cos)
        x = roint(self.hsi_size / 2 + self.hsi_size / 2.5 * sin)

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


def gnd_trk_tick(self, gnd_trk):
    # Draw Ground Track Tick
    gnd_trk_tick_rotated = pygame.transform.rotate(self.ticks, gnd_trk)
    gnd_trk__rect = gnd_trk_tick_rotated.get_rect()
    self.pygamescreen.blit(
        gnd_trk_tick_rotated,
        (
            self.width / 2 - gnd_trk__rect.center[0],
            self.height / 2 - gnd_trk__rect.center[1],
        ),
    )


def turn_rate_disp(self, turn_rate):
    if abs(turn_rate) > 0.2:
        pygame.draw.line(
            self.pygamescreen,
            (255, 0, 255),
            (self.width / 2, self.height / 2 - 158),
            (self.width / 2 + (turn_rate * 10), self.height / 2 - 158),
            10,
        )
    pygame.draw.line(
        self.pygamescreen,
        (255, 255, 255),
        (self.width / 2 + 31, self.height / 2 - 153),
        (self.width / 2 + 31, self.height / 2 - 163),
        3,
    )
    pygame.draw.line(
        self.pygamescreen,
        (255, 255, 255),
        (self.width / 2 - 31, self.height / 2 - 153),
        (self.width / 2 - 31, self.height / 2 - 163),
        3,
    )
    pygame.draw.line(
        self.pygamescreen,
        (0, 0, 0),
        (self.width / 2 + 33, self.height / 2 - 153),
        (self.width / 2 + 33, self.height / 2 - 163),
        1,
    )
    pygame.draw.line(
        self.pygamescreen,
        (0, 0, 0),
        (self.width / 2 + 29, self.height / 2 - 153),
        (self.width / 2 + 29, self.height / 2 - 163),
        1,
    )
    pygame.draw.line(
        self.pygamescreen,
        (0, 0, 0),
        (self.width / 2 - 33, self.height / 2 - 153),
        (self.width / 2 - 33, self.height / 2 - 163),
        1,
    )
    pygame.draw.line(
        self.pygamescreen,
        (0, 0, 0),
        (self.width / 2 - 29, self.height / 2 - 153),
        (self.width / 2 - 29, self.height / 2 - 163),
        1,
    )


def hsi_main(self, hsi_hdg, gnd_trk, turn_rate):
    hsi_hdg = (hsi_hdg + 90) % 360
    gnd_trk = roint(hsi_hdg - gnd_trk - 90) % 360

    # Draw Compass Rose Tick Marks
    tick_rotated = pygame.transform.rotate(self.rose, hsi_hdg)
    tick_rect = tick_rotated.get_rect()
    self.pygamescreen.blit(
        tick_rotated,
        (self.width / 2 - tick_rect.center[0], self.height / 2 - tick_rect.center[1]),
    )

    # Draw Labels
    global old_hsi_hdg
    if (
        old_hsi_hdg != hsi_hdg
    ):  # Don't waste time recalculating/redrawing until the variable changes
        labeler(self, hsi_hdg)
    label_rect = self.labels.get_rect()
    self.pygamescreen.blit(
        self.labels,
        (self.width / 2 - label_rect.center[0], self.height / 2 - label_rect.center[1]),
    )
    old_hsi_hdg = hsi_hdg

    # Draw Ticks
    gnd_trk_tick(self, gnd_trk)

    # Draw Turn Rate
    turn_rate_disp(self, turn_rate)
