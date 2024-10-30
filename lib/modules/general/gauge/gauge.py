#!/usr/bin/env python

#################################################
# Module: gauge
# A gauge is a module that displays a value on a gauge.
# It is a circular display of a value within a range.
# The gauge can be filled with a color that represents the value.
# The gauge can also have a border and a label.
# The gauge can be used to display a variety of values such as fuel level, oil pressure, temperature, etc.
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


class gauge(Module):
    # called only when object is first created.
    def __init__(self):
        Module.__init__(self)
        self.name = "Gauge"  # set name
        self.font_name = "monospace"
        self.font_size = 20
        self.font_bold = False
        self.text = "text"
        self.text_color = (200,255,255)
        self.text_bg_color = (0,0,0)
        self.outline_color = (255,255,255)
        self.outline_weight = 0
        self.outline_radius = 0
        self.value_color = (255,255,255)

        self.data_field = ""
        self.minValue = 0
        self.maxValue = 100
        self.step = 10
    # called once for setup
    def initMod(self, pygamescreen, width=None, height=None):
        if width is None:
            width = 200 # default width
        if height is None:
            height = 50 # default height
        Module.initMod(
            self, pygamescreen, width, height
        )  # call parent init screen.
        if shared.aircraft.debug_mode > 0:
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

    def get_data_field(self, aircraft, data_field):
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
        if data_field == "":
            return 0
        try:
            return get_nested_attr(aircraft, data_field)
        except Exception as e:
            print(f"Error getting data field {data_field}: {e}")
            return 0

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
        #text = self.parse_text(aircraft)
        #label = self.font.render(text, True, self.text_color)

        value = self.get_data_field(aircraft, self.data_field)

        # draw the gauge
        pygame.draw.arc(self.surface2, self.outline_color, (0, 0, self.width, self.height), 0, 2 * math.pi, self.outline_weight)

        # draw the value which is a needle pointing to the value
        value_angle = (value - self.minValue) / (self.maxValue - self.minValue) * 2 * math.pi
        pygame.draw.arc(self.surface2, self.value_color, (0, 0, self.width, self.height), 0, value_angle, self.outline_weight)

        # draw the values around the gauge
        for i in range(0, 100, self.step):
            value_angle = (i - self.minValue) / (self.maxValue - self.minValue) * 2 * math.pi
            pygame.draw.arc(self.surface2, self.value_color, (0, 0, self.width, self.height), 0, value_angle, self.outline_weight)


        # draw the label
        #self.pygamescreen.blit(label, (0, 0))

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

        aircraft_fields = shared.aircraft._get_all_fields()
        #print(f"templates: {aircraft_fields}")

        return {
            "data_field": {
                "type": "dropdown",
                "default": self.data_field,
                "options": aircraft_fields,
                "label": "Data Field",
                "description": "Select a data field to display",
            },
            "minValue": {
                "type": "int",
                "default": self.minValue,
                "label": "Min Value",
                "min": 0,
                "max": 1000,
                "description": "Minimum value to display"
            },
            "maxValue": {
                "type": "int",
                "default": self.maxValue,
                "label": "Max Value",
                "min": 1,
                "max": 1000,
                "description": "Maximum value to display"
            },
            "value_color": {
                "type": "color",
                "default": self.value_color,
                "label": "Value Color",
                "description": "Color of the value to use"
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
            "outline_color": {
                "type": "color",
                "default": self.outline_color,
                "label": "Outline Color",
                "description": "Color of the outline to use"
            },
            "outline_weight": {
                "type": "int",
                "default": self.outline_weight,
                "min": 0,
                "max": 10,
                "label": "Outline Weight",
                "description": "Weight of the outline to use"
            }, 
            "outline_radius": {
                "type": "int",
                "default": self.outline_radius,
                "min": 0,
                "max": 10,
                "label": "Outline Radius",
                "description": "Radius of the outline to use"
            },
            "step": {
                "type": "int",
                "default": self.step,
                "min": 1,
                "max": 100,
                "label": "Step",
                "description": "Step size to use"
            }
        }


    # handle events
    def processEvent(self,event,aircraft,smartdisplay):

        pass



# vi: modeline tabstop=8 expandtab shiftwidth=4 softtabstop=4 syntax=python
