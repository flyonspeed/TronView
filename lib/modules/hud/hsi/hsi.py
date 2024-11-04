#!/usr/bin/env python

#################################################
# Module: HSI
# Topher 2024 re-write.
# Adapted from hsi code by Brian Chesteen.

from lib.modules._module import Module
from lib import hud_graphics
from lib import hud_utils
from lib import smartdisplay
from lib.common.dataship import dataship
import pygame
import math
from lib.common import shared
import pygame.gfxdraw



class hsi(Module):
    # called only when object is first created.
    def __init__(self):
        Module.__init__(self)
        self.name = "HSI"  # set name
        self.x_offset = 0
        self.label_positions = {}
        self.old_hsi_hdg = None
        self.current_heading = None  # Initialize as None for first update
        self.smoothing_factor = 0.15  # Default smoothing (0 = no smoothing, 1 = no movement)

    # called once for setup
    def initMod(self, pygamescreen, width=None, height=None):
        if width is None:
            width = 500 # default width
        if height is None:
            height = 500 # default height
        Module.initMod(
            self, pygamescreen, width, height
        )  # call parent init screen.
        if shared.Dataship.debug_mode > 0:
            print(("Init Mod: %s %dx%d"%(self.name,self.width,self.height)))

        self.myfont1 = pygame.font.SysFont("arial", 30, bold=False)  # hsi font
        self.MainColor = (0, 255, 0)  # main color 

    # setup must have default values for all parameters
    def setup(self, hsi_size = -1 , gnd_trk_tick_size = -1, rose_color = (70,130,40), label_color = (255, 255, 0), smoothing_factor = 0.15):
        #print("HSI setup() %d %d %s %s" % (hsi_size, gnd_trk_tick_size, rose_color, label_color))
        if(hsi_size == -1):
            hsi_size = self.width
        if(gnd_trk_tick_size == -1):
            gnd_trk_tick_size = self.width / 10

        self.smoothing_factor = max(0.0, min(1.0, smoothing_factor))  # Clamp between 0 and 1

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
        self.gnd_trk_tick = pygame.image.load("lib/modules/hud/hsi/tick_m.jpg").convert()
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

        self.label_data = [
            ("N", 0), ("3", 30), ("6", 60), ("E", 90),
            ("12", 120), ("15", 150), ("S", 180), ("21", 210),
            ("24", 240), ("W", 270), ("30", 300), ("33", 330)
        ]
        
        for label, angle in self.label_data:
            rendered_label = self.myfont1.render(label, False, self.label_color)
            setattr(self, f"{label}_label", rendered_label)
            setattr(self, f"{label}_rect", rendered_label.get_rect())

        self.heading_indicator = pygame.Surface((self.hsi_size, self.hsi_size), pygame.SRCALPHA)
        self.draw_heading_indicator()

    def roint(self,num):
        return int(round(num))

    def calculate_label_position(self, angle, hsi_hdg):
        label_angle = (angle - hsi_hdg + 360) % 360
        radius = self.hsi_size / 2.5
        x = self.roint(self.hsi_size / 2 + radius * math.sin(math.radians(label_angle)))
        y = self.roint(self.hsi_size / 2 - radius * math.cos(math.radians(label_angle)))
        return x, y

    def labeler(self, hsi_hdg):
        if self.old_hsi_hdg == hsi_hdg:
            #print(f"Skipping label update, heading unchanged: {hsi_hdg}")
            return  # No need to update if heading hasn't changed

        #print(f"Updating labels for heading: {hsi_hdg}")
        self.labels.fill((0,0,0,0))
        for label, angle in self.label_data:
            x, y = self.calculate_label_position(angle, hsi_hdg)
            rendered_label = getattr(self, f"{label}_label")
            label_rect = getattr(self, f"{label}_rect")
            self.labels.blit(
                rendered_label,
                (x - label_rect.center[0], y - label_rect.center[1])
            )

        self.old_hsi_hdg = hsi_hdg

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

    def draw_heading_indicator(self):
        triangle_height = self.hsi_size / 20
        triangle_width = triangle_height * 0.8
        
        points = [
            (self.hsi_size / 2, self.hsi_size / 2 - self.hsi_size / 3),
            (self.hsi_size / 2 - triangle_width / 2, self.hsi_size / 2 - self.hsi_size / 3 + triangle_height),
            (self.hsi_size / 2 + triangle_width / 2, self.hsi_size / 2 - self.hsi_size / 3 + triangle_height)
        ]
        
        pygame.gfxdraw.filled_trigon(self.heading_indicator, 
                                     int(points[0][0]), int(points[0][1]),
                                     int(points[1][0]), int(points[1][1]),
                                     int(points[2][0]), int(points[2][1]),
                                     self.label_color)
        pygame.gfxdraw.aatrigon(self.heading_indicator,
                                int(points[0][0]), int(points[0][1]),
                                int(points[1][0]), int(points[1][1]),
                                int(points[2][0]), int(points[2][1]),
                                self.label_color)

    def smooth_value(self, current, target, smoothing):
        if current is None:
            return target
        # Calculate the shortest angular distance
        diff = ((target - current + 180) % 360) - 180
        # Apply smoothing
        return current + diff * smoothing

    # called every redraw for the mod
    def draw(self, aircraft, smartdisplay, pos=(None, None)):
        x_pos = smartdisplay.x_center
        y_pos = smartdisplay.y_center
        if pos[0] is not None:
            x_pos = pos[0] + self.width / 2  # center the hsi in the middle of this module
        if pos[1] is not None:
            y_pos = pos[1] + self.height / 2

        target_heading = aircraft.mag_head
        
        # Initialize current_heading if None
        if self.current_heading is None:
            self.current_heading = target_heading

        # Smooth the heading transition
        self.current_heading = self.smooth_value(
            self.current_heading, 
            target_heading, 
            self.smoothing_factor
        )

        gnd_trk = aircraft.gndtrack
        turn_rate = aircraft.turn_rate

        # Draw Compass Rose Tick Marks using smoothed heading
        tick_rotated = pygame.transform.rotate(self.rose, self.current_heading)
        tick_rect = tick_rotated.get_rect()
        self.pygamescreen.blit(
            tick_rotated,
            (x_pos - tick_rect.center[0], y_pos - tick_rect.center[1]),
        )

        # Draw Labels using smoothed heading
        self.labeler(self.current_heading)
        label_rect = self.labels.get_rect()
        self.pygamescreen.blit(
            self.labels,
            (x_pos - label_rect.center[0], y_pos - label_rect.center[1]),
        )

        # Draw Heading Indicator Triangle (stationary)
        self.pygamescreen.blit(self.heading_indicator, 
                             (x_pos - self.hsi_size / 2, y_pos + 40 - self.hsi_size / 2))

        # Draw ground track and heading labels using target values
        gnd_trk_label = self.myfont1.render(f"trk:{gnd_trk:03d}", False, self.label_color)
        hdg_label = self.myfont1.render(f"hdg:{target_heading:03.0f}", False, self.label_color)
        
        self.pygamescreen.blit(
            gnd_trk_label,
            (x_pos - label_rect.center[0], y_pos - label_rect.center[1]),
        )
        self.pygamescreen.blit(
            hdg_label,
            (x_pos + self.width / 2 - (label_rect.center[0] / 2), 
             y_pos - label_rect.center[1]),
        )

        # Draw Turn Rate
        self.turn_rate_disp(smartdisplay, turn_rate, pos)


    # called before screen draw.  To clear the screen to your favorite color.
    def clear(self):
        #self.ahrs_bg.fill((0, 0, 0))  # clear screen
        print("clear")

    # handle key events
    def processEvent(self, event):
        print("processEvent")
    
    def get_module_options(self):
        return {
            "hsi_size": {
                "type": "int",
                "default": self.hsi_size,
                "min": -1,
                "max": 300,
                "label": "HSI Size",
                "description": "Size of the HSI.",
            },
            "smoothing_factor": {
                "type": "float",
                "default": 0.15,
                "min": 0.0,
                "max": 0.95,
                "label": "Smoothing Factor",
                "description": "Heading rotation smoothing (0=none, 0.95=max)",
            }
        }


# vi: modeline tabstop=8 expandtab shiftwidth=4 softtabstop=4 syntax=python






