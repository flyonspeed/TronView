#!/usr/bin/env python

#################################################
# Module: text
# Topher 2024.
# 

from lib.modules._module import Module
from lib import hud_graphics
from lib import hud_utils
from lib import smartdisplay
from lib import aircraft
import pygame
import math

class text(Module):
    # called only when object is first created.
    def __init__(self):
        Module.__init__(self)
        self.name = "Text"  # set name
        self.font_name = "monospace"
        self.font_size = 12
        self.font_bold = False
        self.text = "Hello World"
        self.text_color = (200,255,255)
        self.text_bg_color = (0,0,0)

    # called once for setup
    def initMod(self, pygamescreen, width, height):
        Module.initMod(
            self, pygamescreen, width, height
        )  # call parent init screen.
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
        label = self.font.render(self.text, True, self.text_color)
        self.surface2.blit(label, (0, 0))

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
        return {
            "text": {
                "type": "text",
                "default": self.text,
                "label": "Text",
                "description": "Text to display"
            },
            "font_name": {
                "type": "string",
                "default": self.font_name,
                "label": "Font Name",
                "description": "Name of the font to use",
                "post_change_function": "buildFont"
            },
            "font_size": {
                "type": "int",
                "default": self.font_size,
                "min": 7,
                "max": 40,
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
            "text_bg_color": {
                "type": "color",
                "default": self.text_bg_color,
                "label": "Text Background Color",
                "description": "Color of the text background to use"
            },
        }

    # handle events
    def processEvent(self,event,aircraft,smartdisplay):

        pass



# vi: modeline tabstop=8 expandtab shiftwidth=4 softtabstop=4 syntax=python
