#!/usr/bin/env python

#################################################
# Module: text
# Topher 2024.
# 

import inspect
from lib.modules._module import Module
from lib import hud_graphics
from lib import hud_utils
from lib import smartdisplay
from lib import aircraft
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
        print(("Init Mod: %s %dx%d"%(self.name,self.width,self.height)))
        # does the self.font_name variable exist?
            
        self.font = pygame.font.SysFont(self.font_name, self.font_size, self.font_bold)
        # does the self.text variable exist?
        self.surface2 = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        self.surface2.fill((0,0,0,0))
        # Remove the self.surface creation and fill

    def parse_text(self, aircraft):
        def get_nested_attr(obj, attr):
            parts = attr.split('.')
            for part in parts:
                if part.endswith('()'):
                    # It's a function call
                    func_name = part[:-2]
                    obj = getattr(obj, func_name)()
                else:
                    obj = getattr(obj, part)
            return obj

        words = self.text.split()
        result = self.text
        for word in words:
            if "{" in word and "}" in word:
                variable_name = word[1:-1]
                if "%" in variable_name:
                    variable_name, format_specifier = variable_name.split("%")
                else:
                    format_specifier = None

                try:
                    variable_value = get_nested_attr(aircraft, variable_name)
                    
                    if format_specifier:
                        variable_value = f"{variable_value:{format_specifier}}"
                    else:
                        variable_value = str(variable_value)
                except Exception as e:
                    variable_value = f"Error: {str(e)}"

                result = result.replace(word, variable_value)
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

        aircraft_fields = self.get_aircraft_fields(shared.aircraft)
        # # get a list of all fields in the aircraft object
        # for field in shared.aircraft.__dict__:
        #     # check if it's not a special method or object
        #     #if not callable(getattr(shared.aircraft, field)) and not isinstance(getattr(shared.aircraft, field), object):
        #         # convert to string
        #         description = str(field)
        #         # is field a string?
        #         if isinstance(getattr(shared.aircraft, field), str):
        #             description += " (string)"
        #         # is field a function?
        #         elif callable(getattr(shared.aircraft, field)):
        #             description += " (function)"
        #         # is field an object?
        #         elif isinstance(getattr(shared.aircraft, field), object):
        #             description += " (object)"
        #         templates.append(description)
        #         print(f"template: {description}")
        #         # is field a function?
        print(f"templates: {aircraft_fields}")

        return {
            "template": {
                "type": "dropdown",
                "default": "template",
                "options": aircraft_fields,
                "label": "Value",
                "description": "Select a predefined value",
                "post_change_function": "update_text"
            },
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

    def get_aircraft_fields(self,obj, prefix=''):
        fields = []
        
        for name, value in inspect.getmembers(obj):
            # Skip private and special methods
            if name.startswith('__'):
                continue
            
            full_name = f"{prefix}{name}" if prefix else name
            
            if isinstance(value, (str, int, float, list, tuple, dict)):
                fields.append(full_name)
            elif inspect.isfunction(value) or inspect.ismethod(value):
                fields.append(f"{full_name}()")
            elif inspect.isclass(value):
                # Skip classes
                continue
            elif hasattr(value, '__dict__'):
                # It's an object, recurse into it
                fields.extend(self.get_aircraft_fields(value, f"{full_name}."))
    
        return fields

    def update_text(self):
        self.text = "{"+self.template+"}"
        #self.buildFont()

    # handle events
    def processEvent(self,event,aircraft,smartdisplay):

        pass



# vi: modeline tabstop=8 expandtab shiftwidth=4 softtabstop=4 syntax=python
