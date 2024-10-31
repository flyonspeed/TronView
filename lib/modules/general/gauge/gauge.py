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
        self.show_text = True
        self.text_offset = 1
        self.pointer_distance = 1
    

        # Add new attributes for gauge drawing
        self.startAngle = 225  # Start angle in degrees (bottom left)
        self.sweepAngle = 270  # Total sweep angle in degrees
        self.arcRadius = 0  # Will be calculated in initMod
        self.pointer_width = 0  # Will be calculated in initMod
        self.arcCenter = None  # Will be set in initMod

    # called once for setup
    def initMod(self, pygamescreen, width=None, height=None):
        if width is None:
            width = 200
        if height is None:
            height = 200  # Make it square by default
            
        Module.initMod(self, pygamescreen, width, height)
        
        # Calculate gauge dimensions
        self.arcRadius = min(self.width, self.height) * 0.4
        self.pointer_width = self.arcRadius * 0.1
        self.arcCenter = (self.width // 2, self.height // 2)
        
        self.font = pygame.font.SysFont(self.font_name, self.font_size, self.font_bold)
        self.surface2 = pygame.Surface((self.width, self.height), pygame.SRCALPHA)

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

        # Clear the surface
        self.surface2.fill((0,0,0,0))
        
        # Get current value 
        value = self.get_data_field(aircraft, self.data_field)
        
        # Store actual value for display
        actual_value = value
        
        # Limit value for pointer position only
        if value is not None:
            value = max(self.minValue, min(self.maxValue, value))  # Clamp value for pointer

        # Draw 3D effect for the outer circle (bezel)
        for i in range(4):
            # Create gradient effect from dark to light
            alpha = 150 - (i * 30)
            color = (
                max(0, self.outline_color[0] - 40 + i * 10),
                max(0, self.outline_color[1] - 40 + i * 10),
                max(0, self.outline_color[2] - 40 + i * 10)
            )
            pygame.draw.circle(self.surface2, color, self.arcCenter, 
                             self.arcRadius - i, max(1, self.outline_weight))

        # Draw main dial face with slight gradient
        for i in range(3):
            alpha = 255 - (i * 20)
            face_color = (20, 20, 20, alpha)
            pygame.draw.circle(self.surface2, face_color, self.arcCenter, 
                             self.arcRadius - 4 - i)

        # Draw tick marks and values with 3D effect
        for i in range(self.minValue, self.maxValue + 1, self.step):
            angle = math.radians(self.startAngle - 
                               (i - self.minValue) * self.sweepAngle / 
                               (self.maxValue - self.minValue))
            
            # Draw main tick mark
            inner_x = self.arcCenter[0] + (self.arcRadius - 15) * math.cos(angle)
            inner_y = self.arcCenter[1] - (self.arcRadius - 15) * math.sin(angle)
            outer_x = self.arcCenter[0] + (self.arcRadius - 5) * math.cos(angle)
            outer_y = self.arcCenter[1] - (self.arcRadius - 5) * math.sin(angle)
            
            # Draw tick shadow
            shadow_color = (30, 30, 30)
            pygame.draw.line(self.surface2, shadow_color,
                           (inner_x + 1, inner_y + 1), 
                           (outer_x + 1, outer_y + 1), 2)
            
            # Draw main tick
            pygame.draw.line(self.surface2, self.outline_color,
                           (inner_x, inner_y), (outer_x, outer_y), 2)
            
            # Draw value text with shadow
            text = str(i)
            # Draw text shadow
            shadow_surface = self.font.render(text, True, (30, 30, 30))
            text_surface = self.font.render(text, True, self.text_color)
            text_rect = text_surface.get_rect()
            text_x = self.arcCenter[0] + (self.arcRadius - 35) * math.cos(angle) - text_rect.width/2
            text_y = self.arcCenter[1] - (self.arcRadius - 35) * math.sin(angle) - text_rect.height/2
            
            # Blit shadow then text
            self.surface2.blit(shadow_surface, (text_x + 1, text_y + 1))
            self.surface2.blit(text_surface, (text_x, text_y))

        # Draw the pointer with 3D effect
        if value is not None:
            value_angle = math.radians(self.startAngle - 
                                 (value - self.minValue) * self.sweepAngle / 
                                 (self.maxValue - self.minValue))
        
            # Create shorter, stubbier pointer triangle
            pointer_length = self.arcRadius * 0.15  # Reduced from 0.35 to 0.15 to make it shorter
            pointer_base_width = self.pointer_width * 1.5  # Made base wider
            
            # Calculate center offset based on pointer_distance
            center_offset = (self.arcRadius * 0.3) * (self.pointer_distance/10)  # How far from center to start
            
            # Adjust the base position of the pointer
            base_x = self.arcCenter[0] + center_offset * math.cos(value_angle)
            base_y = self.arcCenter[1] - center_offset * math.sin(value_angle)
            
            # Calculate points for stubby triangle
            pointer_points = [
                # Tip of pointer - closer to numbers
                (base_x + pointer_length * math.cos(value_angle),
                 base_y - pointer_length * math.sin(value_angle)),
                # Wider base points
                (base_x + pointer_base_width * math.cos(value_angle + math.pi/2),
                 base_y - pointer_base_width * math.sin(value_angle + math.pi/2)),
                (base_x + pointer_base_width * math.cos(value_angle - math.pi/2),
                 base_y - pointer_base_width * math.sin(value_angle - math.pi/2))
            ]
            
            # Draw pointer shadow
            shadow_points = [(x + 1, y + 1) for x, y in pointer_points]  # Reduced shadow offset
            pygame.draw.polygon(self.surface2, (30, 30, 30), shadow_points)
            
            # Draw pointer with highlight
            pygame.draw.polygon(self.surface2, self.value_color, pointer_points)
            
            # Add highlight to pointer - adjusted for stubby shape
            highlight_points = [
                pointer_points[0],
                (pointer_points[1][0] * 0.8 + self.arcCenter[0] * 0.2,
                 pointer_points[1][1] * 0.8 + self.arcCenter[1] * 0.2),
                (pointer_points[2][0] * 0.8 + self.arcCenter[0] * 0.2,
                 pointer_points[2][1] * 0.8 + self.arcCenter[1] * 0.2)
            ]
            highlight_color = (
                min(255, self.value_color[0] + 50),
                min(255, self.value_color[1] + 50),
                min(255, self.value_color[2] + 50)
            )
            pygame.draw.polygon(self.surface2, highlight_color, highlight_points)
            
        # Draw center hub with 3D effect
        # Draw hub shadow
        pygame.draw.circle(self.surface2, (30, 30, 30), 
                         (self.arcCenter[0] + 2, self.arcCenter[1] + 2), 
                         self.pointer_width + 2)
        
        # Draw main hub
        # pygame.draw.circle(self.surface2, self.value_color, self.arcCenter, 
        #                  self.pointer_width)
        
        # Add highlight to hub
        # highlight_color = (
        #     min(255, self.value_color[0] + 50),
        #     min(255, self.value_color[1] + 50),
        #     min(255, self.value_color[2] + 50)
        # )
        # pygame.draw.circle(self.surface2, highlight_color,
        #                  (self.arcCenter[0] - 1, self.arcCenter[1] - 1),
        #                  self.pointer_width - 2)

        # Draw the current value text if enabled
        if self.show_text and actual_value is not None:
            # Format the actual value text (not the limited value)
            value_str = f"{actual_value:.1f}"  # Show one decimal place
            
            # Create larger font for value display
            value_font = pygame.font.SysFont(self.font_name, int(self.font_size * 1.2), self.font_bold)
            
            # Render value text with shadow
            shadow_surface = value_font.render(value_str, True, (30, 30, 30))
            value_surface = value_font.render(value_str, True, self.text_color)
            
            # Position text at bottom center of gauge
            text_rect = value_surface.get_rect()
            text_x = self.arcCenter[0] - text_rect.width / 2  # Center horizontally
            text_y = self.arcCenter[1] + self.arcRadius * (self.text_offset/10) # Position below center
            
            # Draw shadow then text
            self.surface2.blit(shadow_surface, (text_x + 1, text_y + 1))
            self.surface2.blit(value_surface, (text_x, text_y))

        # Blit the surface to the screen
        self.pygamescreen.blit(self.surface2, (x, y))

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

            "step": {
                "type": "int",
                "default": self.step,
                "min": 1,
                "max": 100,
                "label": "Step",
                "description": "Step size to use"
            },
            "show_text": {
                "type": "bool",
                "default": self.show_text,
                "label": "Show Value",
                "description": "Show the current value next to the gauge"
            },
            "text_offset": {
                "type": "int",
                "default": self.text_offset,
                "min": 1,
                "max": 10,
                "label": "Text Offset",
                "description": "Offset of the text from the center"
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
            "pointer_distance": {
                "type": "int",
                "default": self.pointer_distance,
                "min": 1,
                "max": 15,
                "label": "Pointer Distance",
                "description": "Distance of the pointer from the center"
            },
        }


    # handle events
    def processEvent(self,event,aircraft,smartdisplay):

        pass



# vi: modeline tabstop=8 expandtab shiftwidth=4 softtabstop=4 syntax=python
