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
    # Define segment patterns at class level
    SEGMENTS = {
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
        
        # Add cache-related variables
        self._char_cache = {}  # Cache for rendered characters
        self._last_text = ""   # Track last rendered text
        self._background = None # Pre-rendered background with inactive segments
        self._needs_reset = True # Flag to track if cache needs reset

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
        
        # Reset caches since dimensions changed
        self._reset_caches()

    def _reset_caches(self):
        """Reset all caches when dimensions or colors change"""
        self._char_cache = {}
        self._last_text = ""
        self._create_background()
        self._needs_reset = False

    def _create_background(self):
        """Pre-render background with all inactive segments"""
        self._background = pygame.Surface((self.digit_width, self.digit_height), pygame.SRCALPHA)
        
        w, h, t = self.digit_width, self.digit_height, self.segment_thickness
        
        # Calculate key points
        left = t
        right = w - t
        center = w/2
        top = t
        bottom = h - t
        middle = h/2
        
        # Define segment coordinates
        self.segs = [
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
        for seg in self.segs:
            self.draw_segment(self._background, seg, self.not_active_color)

    def draw_segment(self, surface, points, color):
        """Draw a segment using polygon"""
        pygame.draw.polygon(surface, color, points)

    def draw_digit(self, digit):
        """Draw a single digit/letter, using cache if available"""
        digit = str(digit).upper()
        
        # Return cached version if available
        if digit in self._char_cache:
            return self._char_cache[digit]
            
        # Create new surface starting from background
        new_surface = self._background.copy()
        
        # Only draw active segments
        if digit in self.SEGMENTS:
            pattern = self.SEGMENTS[digit]
            for i, (seg, on) in enumerate(zip(self.segs, pattern)):
                if on:
                    self.draw_segment(new_surface, seg, self.text_color)
        
        # Cache and return
        self._char_cache[digit] = new_surface
        return new_surface

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
        # Reset caches if needed
        if self._needs_reset:
            self._reset_caches()
            
        if pos[0] is None:
            x = smartdisplay.x_center
        else:
            x = pos[0]
        if pos[1] is None:
            y = smartdisplay.y_center
        else:
            y = pos[1]

        # Clear main surface
        

        if self.fail:
            # Draw fail indication
            pygame.draw.rect(self.surface, (50,50,50), (0,0,self.width,self.height))
            font = pygame.font.SysFont('Arial', min(self.width//3, self.height//2))
            fail_text = font.render('XXX', True, (255,0,0))
            text_rect = fail_text.get_rect(center=(self.width//2, self.height//2))
            self.surface.blit(fail_text, text_rect)
        else:
            # Parse template/text
            parsed_text = self.parse_text(aircraft)
            text = str(parsed_text).upper()
            
            # Format text length
            if len(text) < self.total_decimals:
                text = text.ljust(self.total_decimals)
            elif len(text) > self.total_decimals:
                text = text[:self.total_decimals]
            
            # Only redraw if text changed
            if text != self._last_text:
                # Clear surface
                self.surface.fill((0,0,0,0))

                # Draw each character
                for i, char in enumerate(text):
                    digit_surface = self.draw_digit(char)
                    digit_x = i * (self.digit_width + self.digit_spacing)
                    self.surface.blit(digit_surface, (digit_x, 0))
                
                # Draw border if needed
                if self.box_weight > 0:
                    pygame.draw.rect(self.surface, self.box_color, 
                                   (0,0,self.width,self.height), self.box_weight)
                                   
                self._last_text = text

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

    # Add cache reset to option setters
    def set_text_color(self, color):
        self.text_color = color
        self._needs_reset = True
        
    def set_not_active_color(self, color):
        self.not_active_color = color
        self._needs_reset = True
        
    def set_box_color(self, color):
        self.box_color = color
        self._needs_reset = True
        
    def set_box_weight(self, weight):
        self.box_weight = weight
        self._needs_reset = True
        
    def set_total_decimals(self, decimals):
        self.total_decimals = decimals
        self._needs_reset = True



# vi: modeline tabstop=8 expandtab shiftwidth=4 softtabstop=4 syntax=python
