#!/usr/bin/env python

#################################################
## HSI Module by Brian Chesteen. 02/08/2019

from __future__ import print_function
import pygame
import math

def hsi_init(self, hsi_size, color):
    self.myfont1 = pygame.font.SysFont(
        "Comic Sans MS", 30
    )  # hsi

    # HSI Setup
    self.hsi_size = hsi_size
    self.color = color
    self.rose = pygame.Surface((self.hsi_size, self.hsi_size), pygame.SRCALPHA)
    self.labels = pygame.Surface((self.hsi_size, self.hsi_size), pygame.SRCALPHA)


    # Setup Labels
    self.N = self.myfont1.render("N", False, (self.color))
    self.N_rect = self.N.get_rect()
    self.R3 = self.myfont1.render("3", False, (self.color))
    self.R3_rect = self.R3.get_rect()
    self.R6 = self.myfont1.render("6", False, (self.color))
    self.R6_rect = self.R6.get_rect()
    self.E = self.myfont1.render("E", False, (self.color))
    self.E_rect = self.E.get_rect()
    self.R12 = self.myfont1.render("12", False, (self.color))
    self.R12_rect = self.R12.get_rect()
    self.R15 = self.myfont1.render("15", False, (self.color))
    self.R15_rect = self.R15.get_rect()
    self.S = self.myfont1.render("S", False, (self.color))
    self.S_rect = self.S.get_rect()
    self.R21 = self.myfont1.render("21", False, (self.color))
    self.R21_rect = self.R21.get_rect()
    self.R24 = self.myfont1.render("24", False, (self.color))
    self.R24_rect = self.R24.get_rect()
    self.W = self.myfont1.render("W", False, (self.color))
    self.W_rect = self.W.get_rect()
    self.R30 = self.myfont1.render("30", False, (self.color))
    self.R30_rect = self.R30.get_rect()
    self.R33 = self.myfont1.render("33", False, (self.color))
    self.R33_rect = self.R33.get_rect()


def roint(num):
    return int(round(num))

# Create HSI label coordinates
def labeler(self, hsi_hdg):
    self.labels.fill((pygame.SRCALPHA))
    for label in range(360):
        cos = math.cos(math.radians(label))
        sin = math.sin(math.radians(label))
        y = roint(self.hsi_size / 2 + self.hsi_size / 2.5 * cos)
        x = roint(self.hsi_size / 2 + self.hsi_size / 2.5 * sin)

        if label == hsi_hdg:
            self.labels.blit(self.E, (x - self.E_rect.center[0], y - self.E_rect.center[1]))
        if label == (hsi_hdg + 330) % 360:
            self.labels.blit(self.R12, (x - self.R12_rect.center[0], y - self.R12_rect.center[1]))
        if label == (hsi_hdg + 300) % 360:
            self.labels.blit(self.R15, (x - self.R15_rect.center[0], y - self.R15_rect.center[1]))
        if label == (hsi_hdg + 270) % 360:
            self.labels.blit(self.S, (x - self.S_rect.center[0], y - self.S_rect.center[1]))
        if label == (hsi_hdg + 240) % 360:
            self.labels.blit(self.R21, (x - self.R21_rect.center[0], y - self.R21_rect.center[1]))
        if label == (hsi_hdg + 210) % 360:
            self.labels.blit(self.R24, (x - self.R24_rect.center[0], y - self.R24_rect.center[1]))
        if label == (hsi_hdg + 180) % 360:
            self.labels.blit(self.W, (x - self.W_rect.center[0], y - self.W_rect.center[1]))
        if label == (hsi_hdg + 150) % 360:
            self.labels.blit(self.R30, (x - self.R30_rect.center[0], y - self.R30_rect.center[1]))
        if label == (hsi_hdg + 120) % 360:
            self.labels.blit(self.R33, (x - self.R33_rect.center[0], y - self.R33_rect.center[1]))
        if label == (hsi_hdg + 90) % 360:
            self.labels.blit(self.N, (x - self.N_rect.center[0], y - self.N_rect.center[1]))
        if label == (hsi_hdg + 60) % 360:
            self.labels.blit(self.R3, (x - self.R3_rect.center[0], y - self.R3_rect.center[1]))
        if label == (hsi_hdg + 30) % 360:
            self.labels.blit(self.R6, (x - self.R6_rect.center[0], y - self.R6_rect.center[1]))

        
def hsi_main(self, hsi_hdg):
    # Draw Major Tick marks
    hsi_hdg = (hsi_hdg + 90) % 360
    for big_tick in range(36):
        cos = math.cos(math.radians(360.0 / 36 * big_tick))
        sin = math.sin(math.radians(360.0 / 36 * big_tick))
        x0 = roint(self.hsi_size / 2 + self.hsi_size / 15 * cos * 4)
        y0 = roint(self.hsi_size / 2 + self.hsi_size / 15 * sin * 4)
        x1 = roint(self.hsi_size / 2 + self.hsi_size / 2.8 * cos)
        y1 = roint(self.hsi_size / 2 + self.hsi_size / 2.8 * sin)
        pygame.draw.line(self.rose, self.color, [x0, y0], [x1, y1], 3)
    tick_rotated = pygame.transform.rotate(self.rose, hsi_hdg)
    tick_rect = tick_rotated.get_rect()
    self.pygamescreen.blit(tick_rotated, (self.width / 2 - tick_rect.center[0], self.height / 2 - tick_rect.center[1]))

    # Draw Minor Tick Marks
    for little_tick in range(72):
        cos = math.cos(math.radians(360.0 / 72 * little_tick))
        sin = math.sin(math.radians(360.0 / 72 * little_tick))
        x0 = roint(self.hsi_size / 2 + self.hsi_size / 13 * cos * 4)
        y0 = roint(self.hsi_size / 2 + self.hsi_size / 13 * sin * 4)
        x1 = roint(self.hsi_size / 2 + self.hsi_size / 3 * cos)
        y1 = roint(self.hsi_size / 2 + self.hsi_size / 3 * sin)
        pygame.draw.line(self.rose, self.color, [x0, y0], [x1, y1], 2)
    tock_rotated = pygame.transform.rotate(self.rose, hsi_hdg)
    tock_rect = tock_rotated.get_rect()
    self.pygamescreen.blit(tock_rotated, (self.width / 2 - tock_rect.center[0], self.height / 2 - tock_rect.center[1]))

    # Draw Labels
    labeler(self, hsi_hdg)   
    label_rect = self.labels.get_rect()
    self.pygamescreen.blit(self.labels, (self.width / 2 - label_rect.center[0], self.height / 2 - label_rect.center[1]))
