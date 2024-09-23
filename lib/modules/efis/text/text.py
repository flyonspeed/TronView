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
        self.font_size = 20
        self.font_bold = False
        self.text = "text"
        self.text_color = (200,255,255)
        self.text_bg_color = (0,0,0)
        self.box_color = (255,255,255)
        self.box_weight = 0
        self.box_radius = 0

    # called once for setup
    def initMod(self, pygamescreen, width=None, height=None):
        if width is None:
            width = 200 # default width
        if height is None:
            height = 50 # default height
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

    def parse_text(self, aircraft):
        # text can contain variables in the form of {variable_name}
        # allow %f to format the variable as a float example {variable_name%2f}

        # split the text into words
        words = self.text.split()
        result = self.text
        for word in words:
            if "{" in word and "}" in word:
                # this is a variable
                variable_name = word[1:-1]
                # check if it has a format specifier
                if "%" in variable_name:
                    # split the variable name and the format specifier
                    variable_name, format_specifier = variable_name.split("%")
                    # get the value of the variable from the aircraft object
                    variable_value = getattr(aircraft, variable_name, "N/A")
                    # apply the format specifier example %0.2f = float with 2 decimal places. %d = integer
                    try:
                        # Use f-string formatting for float values
                        variable_value = f"{variable_value:{format_specifier}}"
                    except Exception as e:
                        # get error message
                        variable_value = str(e)
                    
                    # replace the variable with the value
                    result = result.replace(word, str(variable_value))
                else:
                    # get the value of the variable from the aircraft object
                    variable_value = getattr(aircraft, variable_name, "N/A")
                # replace the variable with the value
                result = result.replace(word, str(variable_value))
            else:
                # this is a normal word
                result = result.replace(word, word)
        return result

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
        text = self.parse_text(aircraft)
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
        return {
            "text": {
                "type": "text",
                "default": self.text,
                "label": "Text",
                "description": "Text to display"
            },
            "font_name": {
                "type": "text",
                "default": self.font_name,
                "label": "Font Name",
                "description": "Name of the font to use",
                "post_change_function": "buildFont"
            },
            "font_size": {
                "type": "int",
                "default": self.font_size,
                "min": 10,
                "max": 70,
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

    # handle events
    def processEvent(self,event,aircraft,smartdisplay):

        pass



# vi: modeline tabstop=8 expandtab shiftwidth=4 softtabstop=4 syntax=python
