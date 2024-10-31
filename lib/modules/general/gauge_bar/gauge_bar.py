#!/usr/bin/env python

#################################################
# Module: gauge_bar
# A bar gauge displays a value as a horizontal or vertical bar.
# The bar has a 3D appearance with gradients and shadows.
# The bar can show min/max values and current value text.
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

class gauge_bar(Module):
    def __init__(self):
        Module.__init__(self)
        self.name = "Gauge Bar"
        self.font_name = "monospace"
        self.font_size = 20
        self.font_bold = False
        self.text_color = (200,255,255)
        self.bar_color = (0,255,0)  # Main bar color
        self.background_color = (40,40,40)  # Bar background
        self.border_color = (100,100,100)  # Border color
        
        # Gauge parameters
        self.data_field = ""
        self.minValue = 0
        self.maxValue = 100
        self.vertical = False  # False = horizontal, True = vertical
        self.show_text = True
        self.show_borders = True
        self.border_width = 2
        self.direction = 1  # 1 = facing right, 2 = facing left, 3 = facing up.
        
        # 3D effect parameters
        self.gradient_steps = 5  # Number of gradient steps for 3D effect
        self.shadow_offset = 2  # Shadow offset in pixels
        
        # Smoothing
        self.current_smooth_value = 0
        self.smooth_factor = 0.15

    def initMod(self, pygamescreen, width=None, height=None):
        if width is None:
            width = 200
        if height is None:
            height = 50
        Module.initMod(self, pygamescreen, width, height)
        
        self.font = pygame.font.SysFont(self.font_name, self.font_size, self.font_bold)
        self.surface2 = pygame.Surface((self.width, self.height), pygame.SRCALPHA)

    def get_data_field(self, aircraft, data_field):
        def get_nested_attr(obj, attr):
            parts = attr.split('.')
            for part in parts:
                if part.endswith('()'):
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

    def draw(self, aircraft, smartdisplay, pos=(None,None)):
        if pos[0] is None:
            x = smartdisplay.x_center
        else:
            x = pos[0]
        if pos[1] is None:
            y = smartdisplay.y_center
        else:
            y = pos[1]

        # Clear surface
        self.surface2.fill((0,0,0,0))
        
        # Get and smooth value
        target_value = self.get_data_field(aircraft, self.data_field)
        actual_value = target_value
        
        if target_value is not None:
            diff = target_value - self.current_smooth_value
            self.current_smooth_value += diff * self.smooth_factor
            value = max(self.minValue, min(self.maxValue, self.current_smooth_value))
        else:
            value = None

        if value is not None:
            # Calculate bar dimensions
            padding = 10
            bar_height = self.height - (padding * 2)
            bar_width = self.width - (padding * 2)
            
            if self.vertical:
                # Draw background with 3D effect
                for i in range(self.gradient_steps):
                    shade = max(0, self.background_color[0] - (i * 5))
                    bg_color = (shade, shade, shade)
                    bar_rect = pygame.Rect(padding, padding + i, 
                                         bar_width, bar_height - i)
                    pygame.draw.rect(self.surface2, bg_color, bar_rect)

                # Calculate value height
                value_percent = (value - self.minValue) / (self.maxValue - self.minValue)
                value_height = int(bar_height * value_percent)
                
                # Draw value bar with 3D effect
                for i in range(self.gradient_steps):
                    # Create gradient colors
                    bar_shade = (
                        max(0, self.bar_color[0] - (i * 15)),
                        max(0, self.bar_color[1] - (i * 15)),
                        max(0, self.bar_color[2] - (i * 15))
                    )
                    
                    bar_rect = pygame.Rect(padding,
                                         padding + (bar_height - value_height) + i,
                                         bar_width - i,
                                         value_height - i)
                    pygame.draw.rect(self.surface2, bar_shade, bar_rect)
                
            else:  # Horizontal
                # Draw background with 3D effect
                for i in range(self.gradient_steps):
                    shade = max(0, self.background_color[0] - (i * 5))
                    bg_color = (shade, shade, shade)
                    bar_rect = pygame.Rect(padding + i, padding + i, 
                                         bar_width - i, bar_height - i)
                    pygame.draw.rect(self.surface2, bg_color, bar_rect)

                # Calculate value width
                value_percent = (value - self.minValue) / (self.maxValue - self.minValue)
                value_width = int(bar_width * value_percent)
                
                # Draw value bar with 3D effect
                for i in range(self.gradient_steps):
                    # Create gradient colors
                    bar_shade = (
                        max(0, self.bar_color[0] - (i * 15)),
                        max(0, self.bar_color[1] - (i * 15)),
                        max(0, self.bar_color[2] - (i * 15))
                    )
                    
                    bar_rect = pygame.Rect(padding + i, padding + i,
                                         value_width - i, bar_height - i)
                    pygame.draw.rect(self.surface2, bar_shade, bar_rect)

            # Draw borders
            if self.show_borders:
                border_rect = pygame.Rect(padding, padding, bar_width, bar_height)
                pygame.draw.rect(self.surface2, self.border_color, border_rect, self.border_width)

            # Draw value text
            if self.show_text:
                text = f"{actual_value:.1f}"
                text_surface = self.font.render(text, True, self.text_color)
                text_rect = text_surface.get_rect()
                
                # Position text in center of bar
                text_x = padding + (bar_width - text_rect.width) // 2
                text_y = padding + (bar_height - text_rect.height) // 2
                
                # Draw text shadow
                shadow_surface = self.font.render(text, True, (30, 30, 30))
                self.surface2.blit(shadow_surface, (text_x + 1, text_y + 1))
                self.surface2.blit(text_surface, (text_x, text_y))

        # Blit to screen
        self.pygamescreen.blit(self.surface2, (x, y))

    def get_module_options(self):
        aircraft_fields = shared.aircraft._get_all_fields()
        
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
                "description": "Minimum value"
            },
            "maxValue": {
                "type": "int",
                "default": self.maxValue,
                "label": "Max Value",
                "min": 1,
                "max": 1000,
                "description": "Maximum value"
            },
            "vertical": {
                "type": "bool",
                "default": self.vertical,
                "label": "Vertical",
                "description": "Display bar vertically"
            },
            "show_text": {
                "type": "bool",
                "default": self.show_text,
                "label": "Show Value",
                "description": "Show the current value"
            },
            "show_borders": {
                "type": "bool",
                "default": self.show_borders,
                "label": "Show Borders",
                "description": "Show border around bar"
            },
            "border_width": {
                "type": "int",
                "default": self.border_width,
                "min": 1,
                "max": 5,
                "label": "Border Width",
                "description": "Width of the border"
            },
            "bar_color": {
                "type": "color",
                "default": self.bar_color,
                "label": "Bar Color",
                "description": "Color of the bar"
            },
            "background_color": {
                "type": "color",
                "default": self.background_color,
                "label": "Background Color",
                "description": "Color of the background"
            },
            "border_color": {
                "type": "color",
                "default": self.border_color,
                "label": "Border Color",
                "description": "Color of the border"
            },
            "smooth_factor": {
                "type": "float",
                "default": self.smooth_factor,
                "min": 0.01,
                "max": 1.0,
                "label": "Smooth Factor",
                "description": "How quickly the bar moves (0.01=slow, 1.0=instant)"
            },
            "font_name": {
                "type": "dropdown",
                "default": self.font_name,
                "options": ["monospace", "sans-serif", "serif","arial","courier","times","helvetica"],
                "label": "Font Name",
                "description": "Font for value display",
                "post_change_function": "buildFont"
            },
            "font_size": {
                "type": "int",
                "default": self.font_size,
                "min": 10,
                "max": 100,
                "label": "Font Size",
                "description": "Size of the font",
                "post_change_function": "buildFont"
            },
            "text_color": {
                "type": "color",
                "default": self.text_color,
                "label": "Text Color",
                "description": "Color of the value text"
            }
        }

    def buildFont(self):
        self.font = pygame.font.SysFont(self.font_name, self.font_size, self.font_bold) 