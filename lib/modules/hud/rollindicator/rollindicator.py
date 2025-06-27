#!/usr/bin/env python

#################################################
# Module: Roll indicator
# Topher 2021.

from lib.modules._module import Module
from lib import hud_graphics
from lib import hud_utils
from lib import smartdisplay
import pygame
import math
from lib.common import shared
from lib.common.dataship.dataship import Dataship
from lib.common.dataship.dataship_imu import IMUData

class rollindicator(Module):
    # called only when object is first created.
    def __init__(self):
        Module.__init__(self)
        self.name = "RollIndicator"  # set name
        self.hsi_size = 360
        self.roll_point_size = 20
        self.x_offset = 0
        self.IMUData = IMUData()

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

        # fonts
        self.font = pygame.font.SysFont(
            None, int(self.height / 20)
        )

        # Robust roll point tick image loading and scaling
        self.roll_point_size = 20  # Set a reasonable default size
        try:
            self.roll_point_img = pygame.image.load("lib/modules/hud/rollindicator/tick_w.bmp").convert()
            self.roll_point_img.set_colorkey((0, 0, 0))
        except Exception as e:
            print("Failed to load roll point image:", e)
            self.roll_point_img = pygame.Surface((self.roll_point_size, self.roll_point_size), pygame.SRCALPHA)
            pygame.draw.polygon(
                self.roll_point_img,
                (255, 255, 255),
                [
                    (self.roll_point_size // 2, 0),
                    (0, self.roll_point_size),
                    (self.roll_point_size, self.roll_point_size)
                ]
            )  # fallback: white triangle pointer

        self.roll_point_scaled = pygame.transform.scale(
            self.roll_point_img, (self.roll_point_size, self.roll_point_size)
        )
        self.roll_point_scaled_rect = self.roll_point_scaled.get_rect()

        self.roll_tick = pygame.Surface((self.hsi_size, self.hsi_size), pygame.SRCALPHA)
        self.roll_point = pygame.Surface(
            (self.hsi_size, self.hsi_size), pygame.SRCALPHA
        )
        self.roll_point.blit(
            self.roll_point_scaled,
            (
                (self.hsi_size / 2) - self.roll_point_scaled_rect.center[0],
                (self.hsi_size / 2) + 120 - self.roll_point_scaled_rect[1],
            ),
        )
        def roint(num):
            return int(round(num))
        # render big tick onto surface.
        for big_tick in range(6, 13):
            cos = math.cos(math.radians(360.0 / 36 * big_tick))
            sin = math.sin(math.radians(360.0 / 36 * big_tick))
            x0 = roint(self.hsi_size / 2 + self.hsi_size / 15 * cos * 6)
            y0 = roint(self.hsi_size / 2 + self.hsi_size / 15 * sin * 6)
            x1 = roint(self.hsi_size / 2 + self.hsi_size / 2.1 * cos)
            y1 = roint(self.hsi_size / 2 + self.hsi_size / 2.1 * sin)
            pygame.draw.line(self.roll_tick, (255, 255, 255), [x0, y0], [x1, y1], 4)
        for big_tick in range(12, 25):
            cos = math.cos(math.radians(360.0 / 72 * big_tick))
            sin = math.sin(math.radians(360.0 / 72 * big_tick))
            x0 = roint(self.hsi_size / 2 + self.hsi_size / 15 * cos * 6)
            y0 = roint(self.hsi_size / 2 + self.hsi_size / 15 * sin * 6)
            x1 = roint(self.hsi_size / 2 + self.hsi_size / 2.3 * cos)
            y1 = roint(self.hsi_size / 2 + self.hsi_size / 2.3 * sin)
            pygame.draw.line(self.roll_tick, (255, 255, 255), [x0, y0], [x1, y1], 2)
        for big_tick in range(1, 4):
            cos = math.cos(math.radians(360.0 / 8 * big_tick))
            sin = math.sin(math.radians(360.0 / 8 * big_tick))
            x0 = roint(self.hsi_size / 2 + self.hsi_size / 15 * cos * 6)
            y0 = roint(self.hsi_size / 2 + self.hsi_size / 15 * sin * 6)
            x1 = roint(self.hsi_size / 2 + self.hsi_size / 2.3 * cos)
            y1 = roint(self.hsi_size / 2 + self.hsi_size / 2.3 * sin)
            pygame.draw.line(self.roll_tick, (255, 255, 255), [x0, y0], [x1, y1], 4)
        for big_tick in range(3, 4):
            cos = math.cos(math.radians(360.0 / 36 * big_tick))
            sin = math.sin(math.radians(360.0 / 36 * big_tick))
            x0 = roint(self.hsi_size / 2 + self.hsi_size / 15 * cos * 6)
            y0 = roint(self.hsi_size / 2 + self.hsi_size / 15 * sin * 6)
            x1 = roint(self.hsi_size / 2 + self.hsi_size / 2.1 * cos)
            y1 = roint(self.hsi_size / 2 + self.hsi_size / 2.1 * sin)
            pygame.draw.line(self.roll_tick, (255, 255, 255), [x0, y0], [x1, y1], 4)
        for big_tick in range(15, 16):
            cos = math.cos(math.radians(360.0 / 36 * big_tick))
            sin = math.sin(math.radians(360.0 / 36 * big_tick))
            x0 = roint(self.hsi_size / 2 + self.hsi_size / 15 * cos * 6)
            y0 = roint(self.hsi_size / 2 + self.hsi_size / 15 * sin * 6)
            x1 = roint(self.hsi_size / 2 + self.hsi_size / 2.1 * cos)
            y1 = roint(self.hsi_size / 2 + self.hsi_size / 2.1 * sin)
            pygame.draw.line(self.roll_tick, (255, 255, 255), [x0, y0], [x1, y1], 4)
        for big_tick in range(1, 2):
            cos = math.cos(math.radians(360.0 / 4 * big_tick))
            sin = math.sin(math.radians(360.0 / 4 * big_tick))
            x0 = roint(self.hsi_size / 2 + self.hsi_size / 15 * cos * 5.5)
            y0 = roint(self.hsi_size / 2 + self.hsi_size / 15 * sin * 5.5)
            x1 = roint(self.hsi_size / 2 + self.hsi_size / 2.1 * cos)
            y1 = roint(self.hsi_size / 2 + self.hsi_size / 2.1 * sin)
            pygame.draw.line(self.roll_tick, (255, 255, 255), [x0, y0], [x1, y1], 4)

        if len(shared.Dataship.imuData) > 0:
            self.IMUData = shared.Dataship.imuData[0]
        else:
            self.IMUData = IMUData()

    # called every redraw for the mod
    def draw(self, dataship: Dataship, smartdisplay, pos=(None, None)):

        x_pos = 0
        y_pos = 0

        # Calculate center positions
        x_center = self.width // 2
        y_center = self.height // 2

        # Determine draw position
        if pos[0] is not None and pos[1] is not None:
            draw_pos = (pos[0], pos[1])
            x_center = pos[0]
            y_center = pos[1]
        else:
            draw_pos = (x_center - 180, y_center - 180)

        # Draw the roll ticks (arc) rotated by the roll angle
        roll_angle = getattr(self.IMUData, 'roll', 0)
        rotated_ticks = pygame.transform.rotate(self.roll_tick, -roll_angle)
        rotated_ticks_rect = rotated_ticks.get_rect(center=(x_center, y_center))
        smartdisplay.pygamescreen.blit(rotated_ticks, rotated_ticks_rect.topleft)

        # Place the roll point tick at 70% of the arc radius used for the largest rotating arc ticks, at the -270° angle (bottommost point)
        arc_radius = (self.hsi_size / 2.1) * 0.70
        pointer_angle_rad = -3 * math.pi / 2  # -270 degrees, bottommost point of the arc
        pointer_x = int(x_center + arc_radius * math.cos(pointer_angle_rad) - self.roll_point_size // 2)
        pointer_y = int(y_center + arc_radius * math.sin(pointer_angle_rad) - self.roll_point_size // 2)
        smartdisplay.pygamescreen.blit(self.roll_point_scaled, (pointer_x, pointer_y))

    # called before screen draw.  To clear the screen to your favorite color.
    def clear(self):
        #self.ahrs_bg.fill((0, 0, 0))  # clear screen
        print("clear")

    # handle key events
    def processEvent(self, event):
        print("processEvent")
    
    def get_module_options(self):
        return {
            "roll_point_size": {
                "type": "int",
                "default": self.roll_point_size,
                "min": 10,
                "max": 50,
                "label": "Roll Point Size",
                "description": "Size of the roll point.",
                "post_change_function": "update_roll_point_size"
            }
        }
    
    def update_roll_point_size(self):
        self.roll_point_scaled = pygame.transform.scale(
            self.roll_point_img, (self.roll_point_size, self.roll_point_size)
        )
        self.roll_point_scaled_rect = self.roll_point_scaled.get_rect()
    


# vi: modeline tabstop=8 expandtab shiftwidth=4 softtabstop=4 syntax=python
