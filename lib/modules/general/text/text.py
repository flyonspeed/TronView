#!/usr/bin/env python

#################################################
# Module: text
# Topher 2024.
# 2/9/2025 - added dataship refactor.

import inspect
from lib.modules._module import Module
from lib import hud_graphics
from lib import hud_utils
from lib import smartdisplay
from lib.common.dataship import dataship
from lib.common import shared
import pygame
import math


class text(Module):
    # called only when object is first created.
    def __init__(self):
        Module.__init__(self)
        self.name = "Text"  # set name
        self.font_name = "monospace"
        self.font_size = 20
        self.font_bold = False
        self.text = "text"
        self.text_color = (200,255,255)
        self.text_bg_color = (0,0,0)
        self.box_color = (255,255,255)
        self.box_weight = 0
        self.box_radius = 0
        self.template = ""
    # called once for setup
    def initMod(self, pygamescreen, width=None, height=None):
        if width is None:
            width = 200 # default width
        if height is None:
            height = 50 # default height
        Module.initMod(
            self, pygamescreen, width, height
        )  # call parent init screen.
        if shared.Dataship.debug_mode > 0:
            print(("Init Mod: %s %dx%d"%(self.name,self.width,self.height)))
        # does the self.font_name variable exist?
            
        self.font = pygame.font.SysFont(self.font_name, self.font_size, self.font_bold)
        # does the self.text variable exist?
        self.surface2 = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        self.surface2.fill((0,0,0,0))
        # Remove the self.surface creation and fill


    # called every redraw for the mod
    def draw(self, aircraft, smartdisplay, pos=(None,None)):
        if pos[0] is None:
            x = smartdisplay.x_center
        else:
            x = pos[0] 
        if pos[1] is None:
            y = smartdisplay.y_center
        else:
            y = pos[1] 

        # Clear the surface with a transparent background
        self.surface2.fill((0,0,0,0))

        # Render the text with a transparent background
        text = self.parse_text(self.text, aircraft)
        label = self.font.render(text, True, self.text_color)
        self.surface2.blit(label, (0, 0))

        if self.box_weight > 0:
            # calculate the width and height of the text
            text_width, text_height = self.font.size(text)
            # draw a box around the text
            pygame.draw.rect(self.surface2, self.box_color, (0, 0, text_width, text_height), self.box_weight, self.box_radius)

        self.pygamescreen.blit(self.surface2, (x,y))

    # called before screen draw.  To clear the screen to your favorite color.
    def clear(self):
        #self.ahrs_bg.fill((0, 0, 0))  # clear screen
        #print("clear")
        pass

    def buildFont(self):
        self.font = pygame.font.SysFont(self.font_name, self.font_size, self.font_bold)
    
    # return a dict of objects that are used to configure the module.
    def get_module_options(self):

        #data_fields = shared.Dataship._get_all_fields()
        #print(f"templates: {data_fields}")

        return {
            # "template": {
            #     "type": "dropdown",
            #     "default": self.template,
            #     "options": data_fields,
            #     "label": "Predefined",
            #     "description": "Select a predefined value",
            #     "post_change_function": "update_text"
            # },
            "text": {
                "type": "text",
                "default": self.text,
                "label": "Custom",
                "description": "Text to display"
            },
            "font_name": {
                "type": "dropdown",
                "default": self.font_name,
                "options": ["monospace", "sans-serif", "serif","arial","courier","times","helvetica"],
                "label": "Font Name",
                "description": "Name of the font to use",
                "post_change_function": "buildFont"
            },
            "font_size": {
                "type": "int",
                "default": self.font_size,
                "min": 10,
                "max": 300,
                "label": "Font Size",
                "description": "Size of the font to use",
                "post_change_function": "buildFont"
            },
            "font_bold": {
                "type": "bool",
                "default": False,
                "label": "Font Bold",
                "description": "Use bold font",
                "post_change_function": "buildFont"
            },
            "text_color": {
                "type": "color",
                "default": self.text_color,
                "label": "Text Color",
                "description": "Color of the text to use"
            },  
            # "text_bg_color": {
            #     "type": "color",
            #     "default": self.text_bg_color,
            #     "label": "Text Background Color",
            #     "description": "Color of the text background to use"
            # },
            "box_color": {
                "type": "color",
                "default": self.box_color,
                "label": "Box Color",
                "description": "Color of the box to use"
            },
            "box_weight": {
                "type": "int",
                "default": self.box_weight,
                "min": 0,
                "max": 10,
                "label": "Box Weight",
                "description": "Weight of the box to use"
            }, 
            "box_radius": {
                "type": "int",
                "default": self.box_radius,
                "min": 0,
                "max": 10,
                "label": "Box Radius",
                "description": "Radius of the box to use"
            }
        }

    def update_text(self, update_type=None):
        #print(f"update_text: {update_type}")
        if update_type == "on_load": # in "on_load" then we are loading the module from a json file
            return
        if self.template == "":
            return
        # else set the text to the the value.
        self.text = "{"+self.template+"}"
        #self.buildFont()

    # handle events
    def processEvent(self,event,aircraft,smartdisplay):

        pass



# vi: modeline tabstop=8 expandtab shiftwidth=4 softtabstop=4 syntax=python
