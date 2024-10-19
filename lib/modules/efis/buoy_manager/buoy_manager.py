#!/usr/bin/env python

#################################################
# Module: Buoy Manager
# Topher 2024

from lib.modules._module import Module
from lib import hud_graphics
from lib import hud_utils
from lib import smartdisplay
from lib import aircraft
import pygame
import math


class buoy_manager(Module):
    # called only when object is first created.
    def __init__(self):
        Module.__init__(self)
        self.name = "Buoy Manager"  # set name
        self.target_font_size = hud_utils.readConfigInt("HUD", "target_font_size", 20)
        self.buttons = []


    # called once for setup, or when module is being resized in editor
    def initMod(self, pygamescreen, width=None, height=None):
        if width is None:
            width = 120 # default width
        if height is None:
            height = 100 # default height
        Module.initMod(
            self, pygamescreen, width, height
        )  # call parent init screen.
        print(("Init Mod: %s %dx%d"%(self.name,self.width,self.height)))

        self.buttons = []

        # fonts
        self.font_target = pygame.font.SysFont(None, self.target_font_size)
        # Create a surface with per-pixel alpha
        self.surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)

        # create buttons
        self.addButton("Add Buoy", self.addBuoy)

    # called every redraw for the module
    def draw(self, aircraft, smartdisplay, pos=(0, 0)):
        x, y = pos
        
        # Clear the surface with full transparency
        self.surface.fill((0, 0, 0, 0))

        # draw buttons
        for button in self.buttons:
            pygame.draw.rect(self.surface, (255,255,255), (button["x"], button["y"], button["width"], button["height"]), 0, 2)
            text = self.font_target.render(button["text"], True, (0,0,0))
            self.surface.blit(text, (button["x"] + (button["width"]/2 - text.get_width()/2), button["y"] + (button["height"]/2 - text.get_height()/2)))
        
        # Use alpha blending when blitting to the screen
        smartdisplay.pygamescreen.blit(self.surface, pos, special_flags=pygame.BLEND_ALPHA_SDL2)

    def addButton(self, text, function, x=-1, y=-1, width=100, height=30):
        # if x,y are -1, then append the button just below the last one (if any)
        if x == -1 and y == -1:
            if len(self.buttons) > 0:
                x = self.buttons[-1]["x"] + self.buttons[-1]["width"] + 10
                y = self.buttons[-1]["y"]
            else:
                x = 10
                y = 10
        self.buttons.append({"x": x, "y": y, "width": width, "height": height, "text": text, "function": function})

    def clear(self):
        #self.ahrs_bg.fill((0, 0, 0))  # clear screen
        print("clear")

    # handle key events
    def processClick(self, aircraft, mx, my):
        #print("processClick")
        for button in self.buttons:
            if button["x"] <= mx <= button["x"] + button["width"] and button["y"] <= my <= button["y"] + button["height"]:
                button["function"]()


    def addBuoy(self):
        print("addBuoy clicked")

    # return a dict of objects that are used to configure the module.
    def get_module_options(self):
        # each item in the dict represents a configuration option.  These are variable in this class that are exposed to the user to edit.
        return {
            "target_font_size": {
                "type": "int",
                "default": self.target_font_size,
                "min": 10,
                "max": 100,
                "label": "Target Font Size",
                "description": "Font size for target labels"
            }
        }

    def changeHappened(self):
        self.initMod(self.pygamescreen, self.width, self.height)

# vi: modeline tabstop=8 expandtab shiftwidth=4 softtabstop=4 syntax=python
