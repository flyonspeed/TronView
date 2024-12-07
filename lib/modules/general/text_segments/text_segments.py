#!/usr/bin/env python

#################################################
# Module: text_digits
# Topher 2024.
# Digital segment display style numbers

import inspect
from lib.modules._module import Module
from lib import hud_graphics
from lib import hud_utils
from lib import smartdisplay
from lib.common.dataship import dataship
from lib.common import shared
import pygame
import math

        # 16-segment display layout:
        #
        #     a1     a2
        #   ------ ------
        #   |\    h    /|
        # f1| \j     k/ |b1
        #   |  \    /   |
        #   |   \  /    |
        #   |g1  \/  g2 |
        #    ----   -----
        #   |    /\     |
        #   |   /  \    |
        # f2|  /    \   |b2
        #   | /l   m \  |
        #   |/    i   \ |
        #   ------ ------
        #    d1      d2
        
class text_segments(Module):
    # Define segment patterns as class variable
    segments = {
        '0': (1,1,1,1,1,1,1,1,0,0,0,0,0,0,0,0),
        '1': (0,0,1,1,0,0,0,0,0,0,0,0,0,0,0,0),
        '2': (1,1,1,0,1,1,0,1,1,1,0,0,0,0,0,0),
        '3': (1,1,1,1,1,1,0,0,1,1,0,0,0,0,0,0),
        '4': (0,0,1,1,0,0,1,0,1,1,0,0,0,0,0,0),
        '5': (1,1,0,1,1,1,1,0,1,1,0,0,0,0,0,0),
        '6': (1,1,0,1,1,1,1,1,1,1,0,0,0,0,0,0),
        '7': (1,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0),
        '8': (1,1,1,1,1,1,1,1,1,1,0,0,0,0,0,0),
        '9': (1,1,1,1,1,1,1,0,1,1,0,0,0,0,0,0),
        'A': (1,1,1,1,0,0,1,1,1,1,0,0,0,0,0,0),
        'B': (1,1,1,1,1,1,0,0,0,1,1,1,0,0,0,0),
        'C': (1,1,0,0,1,1,1,1,0,0,0,0,0,0,0,0),
        'D': (1,1,1,1,1,1,0,0,0,0,1,1,0,0,0,0),
        'E': (1,1,0,0,1,1,1,1,1,0,0,0,0,0,0,0),
        'F': (1,1,0,0,0,0,1,1,1,0,0,0,0,0,0,0),
        'G': (1,1,0,1,1,1,1,1,0,1,0,0,0,0,0,0),
        'H': (0,0,1,1,0,0,1,1,1,1,0,0,0,0,0,0),
        'I': (1,1,0,0,1,1,0,0,0,0,1,1,0,0,0,0),
        'J': (0,1,1,1,1,1,0,0,0,0,0,0,0,0,0,0),
        'K': (0,0,0,0,0,0,1,1,1,0,0,0,0,1,0,1),
        'L': (0,0,0,0,1,1,1,1,0,0,0,0,0,0,0,0),
        'M': (0,0,1,1,0,0,1,1,0,0,0,0,1,1,0,0),
        'N': (0,0,1,1,0,0,1,1,0,0,0,0,1,0,0,1),
        'O': (1,1,1,1,1,1,1,1,0,0,0,0,0,0,0,0),
        'P': (1,1,1,0,0,0,1,1,1,1,0,0,0,0,0,0),
        'Q': (1,1,1,1,1,1,1,1,0,0,0,0,0,0,0,1),
        'R': (1,1,1,0,0,0,1,1,1,1,0,0,0,0,0,1),
        'S': (1,1,0,1,1,1,1,0,1,1,0,0,0,0,0,0),
        'T': (1,1,0,0,0,0,0,0,0,0,1,1,0,0,0,0),
        'U': (0,0,1,1,1,1,1,1,0,0,0,0,0,0,0,0),
        'V': (0,0,0,0,0,0,1,1,0,0,0,0,0,1,1,0),
        'W': (0,0,1,1,0,0,1,1,0,0,0,0,0,0,1,1),
        'X': (0,0,0,0,0,0,0,0,0,0,0,0,1,1,1,1),
        'Y': (0,0,0,0,0,0,0,0,0,0,0,1,1,1,0,0),
        'Z': (1,1,0,0,1,1,0,0,0,0,0,0,0,1,1,0),
        '-': (0,0,0,0,0,0,0,0,1,1,0,0,0,0,0,0),
        ' ': (0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0)
    }

    def __init__(self):
        Module.__init__(self)
        self.name = "Text Segments"
        self.total_decimals = 3  # Total number of digits to display
        self.scroll_decimal = 1  # Number of scrolling digits
        self.text = "0"  # Default text
        self.text_color = (242,242,24)  # Default color
        self.not_active_color = (45,45,45)  # Not active color
        self.box_color = (45,45,45)  # Border color
        self.box_weight = 0  # Border thickness
        self.digit_spacing = 2  # Spacing between digits
        self.value = 0  # Current value to display
        self.fail = False
        self.bad = False
        self.old = False
        self.template = ""  # Add template support
        
        # Add cache for pre-rendered digits
        self.digit_cache = {}
        self.inactive_digit_surface = None

    def initMod(self, pygamescreen, width=None, height=None):
        if width is None:
            width = 200
        if height is None:
            height = 50
        Module.initMod(self, pygamescreen, width, height)
        
        # Create surfaces
        self.surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        self.digit_surface = pygame.Surface((self.width//self.total_decimals - self.digit_spacing, 
                                           self.height), pygame.SRCALPHA)
        
        # Calculate digit dimensions
        self.digit_width = self.width // self.total_decimals - self.digit_spacing
        self.digit_height = self.height
        self.segment_thickness = max(2, self.digit_height // 10)
        
        # Pre-render inactive segments
        self._create_inactive_segments()

    def _create_inactive_segments(self):
        """Pre-render the inactive segments surface"""
        w = self.digit_width
        h = self.digit_height
        t = self.segment_thickness
        
        # Calculate key points
        left = t
        right = w - t
        center = w/2
        top = t
        bottom = h - t
        middle = h/2
        
        self.inactive_digit_surface = pygame.Surface((w, h), pygame.SRCALPHA)
        
        # Define all segments
        segs = [
            # Top segments (a1, a2)
            [(left, 0), (center-t/2, 0), (center-t/2, t), (left, t)],      # a1
            [(center+t/2, 0), (right, 0), (right, t), (center+t/2, t)],    # a2
            
            # Right segments (b1, b2)
            [(right-t, t), (right, t), (right, middle-t/2), (right-t, middle-t/2)],          # b1
            [(right-t, middle+t/2), (right, middle+t/2), (right, bottom-t), (right-t, bottom-t)],  # b2
            
            # Bottom segments (d1, d2)
            [(left, bottom-t), (center-t/2, bottom-t), (center-t/2, bottom), (left, bottom)],   # d1
            [(center+t/2, bottom-t), (right, bottom-t), (right, bottom), (center+t/2, bottom)], # d2
            
            # Left segments (f1, f2)
            [(0, t), (t, t), (t, middle-t/2), (0, middle-t/2)],           # f1
            [(0, middle+t/2), (t, middle+t/2), (t, bottom-t), (0, bottom-t)],  # f2
            
            # Middle segments (g1, g2)
            [(left+t, middle-t/2), (center-t/2, middle-t/2), (center-t/2, middle+t/2), (left+t, middle+t/2)],    # g1
            [(center+t/2, middle-t/2), (right-t, middle-t/2), (right-t, middle+t/2), (center+t/2, middle+t/2)],  # g2
            
            # Center vertical segments (h, i)
            [(center-t/2, t), (center+t/2, t), (center+t/2, middle-t/2), (center-t/2, middle-t/2)],          # h
            [(center-t/2, middle+t/2), (center+t/2, middle+t/2), (center+t/2, bottom-t), (center-t/2, bottom-t)], # i
            
            # Diagonal segments (j, k, l, m)
            [(left+t, t), (center-t, middle-t/2), (center-t-t/2, middle), (left, t+t)],                    # j
            [(center+t, middle-t/2), (right-t, t), (right, t+t), (center+t+t/2, middle)],               # k
            [(left+t, bottom-t), (center-t, middle+t/2), (center-t-t/2, middle), (left, bottom-2*t)],        # l
            [(center+t, middle+t/2), (right-t, bottom-t), (right, bottom-2*t), (center+t+t/2, middle)]   # m
        ]
        
        # Draw all segments in inactive color
        for seg in segs:
            self.draw_segment(self.inactive_digit_surface, seg, self.not_active_color)

        # Store segs as instance variable
        self.segs = segs

    def draw_segment(self, surface, points, color):
        """Draw a segment using polygon"""
        pygame.draw.polygon(surface, color, points)

    def draw_digit(self, digit):
        """Draw a single digit/letter on digit_surface with caching"""
        # Check cache first - use only immutable types for cache key
        cache_key = (str(digit).upper(), 
                    tuple(self.text_color), 
                    tuple(self.not_active_color))
        
        if cache_key in self.digit_cache:
            self.digit_surface.blit(self.digit_cache[cache_key], (0, 0))
            return
            
        # Clear surface and draw inactive segments
        self.digit_surface.fill((0,0,0,0))
        self.digit_surface.blit(self.inactive_digit_surface, (0, 0))
        
        # If digit not recognized, return early
        if str(digit).upper() not in self.segments:
            return
            
        pattern = self.segments[str(digit).upper()]
        
        # Draw only active segments
        for i, (seg, on) in enumerate(zip(self.segs, pattern)):
            if on:
                self.draw_segment(self.digit_surface, seg, self.text_color)
        
        # Cache the result
        self.digit_cache[cache_key] = self.digit_surface.copy()

    def parse_text(self, aircraft):
        def get_nested_attr(obj, attr):
            parts = attr.split('.')
            for part in parts:
                if part.endswith('()'):
                    # It's a function call
                    func_name = part[:-2]
                    obj = getattr(obj, func_name)()
                elif part.endswith('<obj>'):
                    # It's an object
                    obj = getattr(obj, part[:-5])
                else:
                    obj = getattr(obj, part)
            return obj
    
        def format_object(obj):
            # check if None
            if obj is None:
                obj = "None"
            else:
                sub_vars = obj.__dict__
                final_value = ""
                for sub_var in sub_vars:
                    # check if it starts with _ then skip it.
                    if sub_var.startswith('_'):
                        continue
                    # check if it has a __dict__.. if so skip it cause it's probably a child object.
                    if hasattr(sub_vars[sub_var], '__dict__'):
                        continue
                    final_value += f"{sub_var}: {sub_vars[sub_var]}\n"
                obj = final_value
            return obj

        words = self.text.split()
        result = self.text
        for word in words:
            if "{" in word and "}" in word:
                variable_name = word[1:-1]
                if "%" in variable_name:
                    variable_name, format_specifier = variable_name.split("%")
                elif ":" in variable_name:
                    variable_name, format_specifier = variable_name.split(":")
                else:
                    format_specifier = None

                try:
                    if variable_name == "self":
                        variable_value = format_object(aircraft)
                    else:
                        variable_value = get_nested_attr(aircraft, variable_name)

                    if format_specifier:
                        variable_value = f"{variable_value:{format_specifier}}"
                    elif isinstance(variable_value, (str, int, float, tuple, dict)):
                        variable_value = f"{variable_value}"
                    elif isinstance(variable_value, list):
                        final_value = ""
                        for item in variable_value:
                            final_value += f"\n{format_object(item)}\n======================="
                        variable_value = final_value
                    elif isinstance(variable_value, object):
                        variable_value = format_object(variable_value)
                    else:
                        variable_value = str(variable_value)
                except Exception as e:
                    variable_value = f"Error: {str(e)}"

                result = result.replace(word, variable_value)
            else:
                result = result.replace(word, word)
        return result

    def draw(self, aircraft, smartdisplay, pos=(None,None)):
        if pos[0] is None:
            x = smartdisplay.x_center
        else:
            x = pos[0]
        if pos[1] is None:
            y = smartdisplay.y_center
        else:
            y = pos[1]

        # Clear main surface
        self.surface.fill((0,0,0,0))

        if self.fail:
            # Draw fail indication
            pygame.draw.rect(self.surface, (50,50,50), (0,0,self.width,self.height))
            font = pygame.font.SysFont('Arial', min(self.width//3, self.height//2))
            fail_text = font.render('XXX', True, (255,0,0))
            text_rect = fail_text.get_rect(center=(self.width//2, self.height//2))
            self.surface.blit(fail_text, text_rect)
            return

        # Parse template/text first
        parsed_text = self.parse_text(aircraft)
        # Format input - handle both numbers and text
        text = str(parsed_text).upper()[:self.total_decimals].ljust(self.total_decimals)

        # Draw each character
        for i, char in enumerate(text):
            self.draw_digit(char)
            digit_x = i * (self.digit_width + self.digit_spacing)
            self.surface.blit(self.digit_surface, (digit_x, 0))

        # Draw border if needed
        if self.box_weight > 0:
            pygame.draw.rect(self.surface, self.box_color, 
                           (0,0,self.width,self.height), self.box_weight)

        # Draw to screen
        self.pygamescreen.blit(self.surface, (x,y))

    def clear(self):
        """Clear the cache when module is cleared"""
        self.digit_cache.clear()
        super().clear()

    def get_module_options(self):
        data_fields = shared.Dataship._get_all_fields()

        return {
            "template": {
                "type": "dropdown",
                "default": "template",
                "options": data_fields,
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
            "total_decimals": {
                "type": "int",
                "default": self.total_decimals,
                "min": 1,
                "max": 50,
                "label": "Total Slots",
                "description": "Total number of digits to display"
            },
            "text_color": {
                "type": "color",
                "default": self.text_color,
                "label": "Segment Color",
                "description": "Color of the digit segments"
            },
            "not_active_color": {
                "type": "color",
                "default": self.not_active_color,
                "label": "Not Active Color",
                "description": "Color of the digit segments when not active"
            },
            "box_color": {
                "type": "color",
                "default": self.box_color,
                "label": "Border Color",
                "description": "Color of the border"
            },
            "box_weight": {
                "type": "int",
                "default": self.box_weight,
                "min": 0,
                "max": 10,
                "label": "Border Weight",
                "description": "Thickness of the border"
            }
        }

    def update_text(self):
        self.text = "{"+self.template+"}"

    def processEvent(self, event, aircraft, smartdisplay):
        pass



# vi: modeline tabstop=8 expandtab shiftwidth=4 softtabstop=4 syntax=python
