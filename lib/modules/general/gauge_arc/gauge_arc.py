#!/usr/bin/env python

#################################################
# Module: gauge_arc
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
from lib.common.dataship import dataship
from lib.common import shared
import pygame
import math


class gauge_arc(Module):
    # called only when object is first created.
    def __init__(self):
        Module.__init__(self)
        self.name = "Gauge Arc"  # set name
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
        self.text_offset = 7
        self.pointer_distance = 15
    

        # Add new attributes for gauge drawing
        self.startAngle = 225  # Start angle in degrees (bottom left)
        self.sweepAngle = 270  # Total sweep angle in degrees
        self.arcRadius = 0  # Will be calculated in initMod
        self.pointer_width = 0  # Will be calculated in initMod
        self.arcCenter = None  # Will be set in initMod

        # Add smoothing variables
        self.current_smooth_value = 0  # Current interpolated value
        self.smooth_factor = 0.15  # How quickly to move to target (0.1 = slow, 0.9 = fast)

        # Cache for expensive calculations
        self._cached_tick_positions = []
        self._cached_text_positions = []
        self._cached_surfaces = {}

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

        # Pre-calculate tick and text positions
        self._precalculate_positions()

    def _precalculate_positions(self):
        """Pre-calculate tick and text positions for better performance"""
        self._cached_tick_positions = []
        self._cached_text_positions = []
        
        for i in range(self.minValue, self.maxValue + 1, self.step):
            angle = math.radians(self.startAngle - 
                               (i - self.minValue) * self.sweepAngle / 
                               (self.maxValue - self.minValue))
            
            inner_x = self.arcCenter[0] + (self.arcRadius - 15) * math.cos(angle)
            inner_y = self.arcCenter[1] - (self.arcRadius - 15) * math.sin(angle)
            outer_x = self.arcCenter[0] + (self.arcRadius - 5) * math.cos(angle)
            outer_y = self.arcCenter[1] - (self.arcRadius - 5) * math.sin(angle)
            
            text_x = self.arcCenter[0] + (self.arcRadius - 35) * math.cos(angle)
            text_y = self.arcCenter[1] - (self.arcRadius - 35) * math.sin(angle)
            
            self._cached_tick_positions.append(((inner_x, inner_y), (outer_x, outer_y)))
            self._cached_text_positions.append((text_x, text_y, str(i)))

    def _get_cached_text_surface(self, text, color):
        """Cache and return text surfaces"""
        # Convert color tuple to string for hashing
        key = (text, str(color))
        if key not in self._cached_surfaces:
            text_surface = self.font.render(text, True, color)
            self._cached_surfaces[key] = text_surface
        return self._cached_surfaces[key]

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
        x = pos[0] if pos[0] is not None else smartdisplay.x_center
        y = pos[1] if pos[1] is not None else smartdisplay.y_center

        # Clear the surface
        self.surface2.fill((0,0,0,0))
        
        # Get and smooth value
        target_value = self.get_data_field(aircraft, self.data_field)
        actual_value = target_value
        
        if target_value is not None:
            self.current_smooth_value += (target_value - self.current_smooth_value) * self.smooth_factor
            value = max(self.minValue, min(self.maxValue, self.current_smooth_value))
        else:
            value = None

        # Draw bezel (3D effect)
        for i in range(4):
            color = tuple(max(0, c - 40 + i * 10) for c in self.outline_color)
            pygame.draw.circle(self.surface2, color, self.arcCenter, 
                             self.arcRadius - i, max(1, self.outline_weight))

        # Draw dial face
        for i in range(3):
            pygame.draw.circle(self.surface2, (20, 20, 20, 255 - i * 20), 
                             self.arcCenter, self.arcRadius - 4 - i)

        # Draw tick marks and values using cached positions
        shadow_color = (50, 50, 50)
        for (inner_pos, outer_pos), (text_x, text_y, text) in zip(
            self._cached_tick_positions, self._cached_text_positions):
            
            # Draw tick shadow and main tick
            pygame.draw.line(self.surface2, shadow_color,
                           (inner_pos[0] + 2, inner_pos[1] + 2),
                           (outer_pos[0] + 2, outer_pos[1] + 2), 2)
            pygame.draw.line(self.surface2, self.outline_color,
                           inner_pos, outer_pos, 2)
            
            # Draw text with shadow
            text_surface = self._get_cached_text_surface(text, self.text_color)
            shadow_surface = self._get_cached_text_surface(text, shadow_color)
            text_rect = text_surface.get_rect()
            
            self.surface2.blit(shadow_surface, 
                             (text_x - text_rect.width/2 + 1, 
                              text_y - text_rect.height/2 + 1))
            self.surface2.blit(text_surface, 
                             (text_x - text_rect.width/2, 
                              text_y - text_rect.height/2))

        # Draw pointer (optimized calculation)
        if value is not None:
            value_angle = math.radians(self.startAngle - 
                                     (value - self.minValue) * self.sweepAngle / 
                                     (self.maxValue - self.minValue))
            
            center_offset = (self.arcRadius * 0.3) * (self.pointer_distance/10)
            base_x = self.arcCenter[0] + center_offset * math.cos(value_angle)
            base_y = self.arcCenter[1] - center_offset * math.sin(value_angle)
            
            # Calculate pointer points once
            cos_val = math.cos(value_angle)
            sin_val = math.sin(value_angle)
            pointer_length = self.arcRadius * 0.15
            pointer_base_width = self.pointer_width * 1.5
            
            pointer_points = [
                (base_x + pointer_length * cos_val,
                 base_y - pointer_length * sin_val),
                (base_x + pointer_base_width * math.cos(value_angle + math.pi/2),
                 base_y - pointer_base_width * math.sin(value_angle + math.pi/2)),
                (base_x + pointer_base_width * math.cos(value_angle - math.pi/2),
                 base_y - pointer_base_width * math.sin(value_angle - math.pi/2))
            ]
            
            # Draw pointer with shadow and highlight
            pygame.draw.polygon(self.surface2, (50, 50, 50), 
                              [(x + 2, y + 2) for x, y in pointer_points])
            pygame.draw.polygon(self.surface2, self.value_color, pointer_points)
            
            # # Highlight calculation
            # highlight_points = [
            #     pointer_points[0],
            #     (pointer_points[1][0] * 0.8 + self.arcCenter[0] * 0.2,
            #      pointer_points[1][1] * 0.8 + self.arcCenter[1] * 0.2),
            #     (pointer_points[2][0] * 0.8 + self.arcCenter[0] * 0.2,
            #      pointer_points[2][1] * 0.8 + self.arcCenter[1] * 0.2)
            # ]
            # highlight_color = tuple(min(255, c + 50) for c in self.value_color)
            # pygame.draw.polygon(self.surface2, highlight_color, highlight_points)

        # Draw value text if enabled
        if self.show_text and actual_value is not None:
            value_str = f"{actual_value:.1f}"
            # Convert color to string for the key
            text_key = (value_str, str(self.text_color))
            
            if text_key not in self._cached_surfaces:
                value_font = pygame.font.SysFont(self.font_name, 
                                               int(self.font_size * 1.2), 
                                               self.font_bold)
                self._cached_surfaces[text_key] = value_font.render(
                    value_str, True, self.text_color)
            
            value_surface = self._cached_surfaces[text_key]
            text_rect = value_surface.get_rect()
            text_x = self.arcCenter[0] - text_rect.width / 2
            text_y = self.arcCenter[1] + self.arcRadius * (self.text_offset/10)
            
            # Use string conversion for shadow color key as well
            shadow_text_key = (value_str, str((30, 30, 30)))
            self.surface2.blit(self._get_cached_text_surface(value_str, (30, 30, 30)), 
                             (text_x + 1, text_y + 1))
            self.surface2.blit(value_surface, (text_x, text_y))

        # Final blit to screen
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

        data_fields = shared.Dataship._get_all_fields()
        #print(f"templates: {data_fields}")

        return {
            "data_field": {
                "type": "dropdown",
                "default": self.data_field,
                "options": data_fields,
                "label": "Data Field",
                "description": "Select a data field to display",
            },
            "minValue": {
                "type": "int",
                "default": self.minValue,
                "label": "Min Value",
                "min": 0,
                "max": 1000,
                "description": "Minimum value to display",
                "post_change_function": "update_cached_positions"
            },
            "maxValue": {
                "type": "float",
                "default": self.maxValue,
                "label": "Max Value",
                "description": "Maximum value to display",
                "post_change_function": "update_cached_positions"
            },

            "step": {
                "type": "int",
                "default": self.step,
                "min": 1,
                "max": 1000,
                "label": "Step Size",
                "description": "Step size to use",
                "post_change_function": "update_cached_positions"
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
                "description": "Offset of the text from the center",
                "post_change_function": "update_cached_positions"
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
            "smooth_factor": {
                "type": "float",
                "default": self.smooth_factor,
                "min": 0.01,
                "max": 1.0,
                "label": "Smooth Factor",
                "description": "How quickly the pointer moves to new values (0.01=slow, 1.0=instant)"
            },
        }
    
    def update_cached_positions(self):
        self._precalculate_positions()


    # handle events
    def processEvent(self,event,aircraft,smartdisplay):

        pass



# vi: modeline tabstop=8 expandtab shiftwidth=4 softtabstop=4 syntax=python
