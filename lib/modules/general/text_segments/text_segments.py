#!/usr/bin/env python

#################################################
# Module: text_digits
# Topher 2024.
# Digital segment display style numbers
# 2/10/2025 - new dataship refactor

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
        #    d1   p  d2
        
class text_segments(Module):
    # Define segment patterns at class level
    SEGMENTS = {
        '0': (1,1,1,1,1,1,1,1,0,0,0,0,0,0,0,0,0),
        '1': (0,0,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0),
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
        ' ': (0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0),
        ':': (0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1), 
        '.': (0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1)  # Only period segment
    }

    def __init__(self):
        Module.__init__(self)
        self.name = "Text Segments"
        self.total_decimals = 3  # Total number of digits to display
        self.scroll_decimal = 1  # Number of scrolling digits
        self.text = "0"  # Default text
        self.text_color = (242,242,24)  # Default color
        self.not_active_color = (31,31,31)  # Not active color
        self.box_color = (45,45,45)  # Border color
        self.box_weight = 0  # Border thickness
        self.digit_spacing = 5  # Spacing between digits
        self.width_ratio = 71  # Width to height ratio (71 = 0.71)
        self.value = 0  # Current value to display
        self.fail = False
        self.bad = False
        self.old = False
        self.template = ""  # Add template support
        self.justify = 'left'  # Add default justification
        self.padding = 5  # Padding between segments and border
        
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
        
        # Calculate digit dimensions using ratio (convert from int to decimal)
        self.digit_width = int((self.height - 2*self.padding) * (self.width_ratio / 100))
        self.digit_height = self.height - 2*self.padding
        self.segment_thickness = max(2, self.digit_height // 10)
        
        # Adjust surface based on calculated width
        self.digit_surface = pygame.Surface((self.digit_width, self.digit_height), pygame.SRCALPHA)
        
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
            [(right, t), (right+t, t), (right+t, middle-t/2), (right, middle-t/2)],          # b1
            [(right, middle+t/2), (right+t, middle+t/2), (right+t, bottom-t), (right, bottom-t)],  # b2
            
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
            
            # Modified diagonal segments - from corners to center
            # j - top left diagonal
            [(left, t),                     # top left
             (left+t, t),                   # top right
             (center, middle),              # bottom right
             (center-t, middle)],           # bottom left
            
            # k - top right diagonal
            [(right-t, t),                  # top left
             (right, t),                    # top right
             (center+t, middle),            # bottom left
             (center, middle)],             # bottom right
            
            # l - bottom left diagonal
            [(center-t, middle),            # top left
             (center, middle),              # top right
             (left+t, bottom),              # bottom right
             (left, bottom)],               # bottom left
            
            # m - bottom right diagonal
            [(center, middle),              # top left
             (center+t, middle),            # top right
             (right, bottom),               # bottom right
             (right-t, bottom)],            # bottom left
             
            # Period segment (p)
            [(center-t/2, bottom-t), (center+t/2, bottom-t),
             (center+t/2, bottom), (center-t/2, bottom)]  # small square at bottom center
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
            parsed_text = self.parse_text(self.text, aircraft)
            text = str(parsed_text).upper()
            
            # Format text length
            if len(text) < self.total_decimals:
                if self.justify == 'right':
                    text = text.rjust(self.total_decimals)
                else:  # left justify
                    text = text.ljust(self.total_decimals)
            elif len(text) > self.total_decimals:
                text = text[:self.total_decimals]
            
            # Only redraw if text changed
            if text != self._last_text:
                # Clear surface
                self.surface.fill((0,0,0,0))

                # Draw each character with padding offset
                for i, char in enumerate(text):
                    digit_surface = self.draw_digit(char)
                    digit_x = self.padding + i * (self.digit_width + self.digit_spacing)
                    self.surface.blit(digit_surface, (digit_x, self.padding))
                
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
            # "template": {
            #     "type": "dropdown",
            #     "default": "template",
            #     "options": data_fields,
            #     "label": "Value",
            #     "description": "Select a predefined value",
            #     "post_change_function": "update_text"
            # },
            "text": {
                "type": "text",
                "default": self.text,
                "label": "Custom",
                "description": "Text to display",
                "post_change_function": "valueChanged"
            },
            "digit_spacing": {
                "type": "int",
                "default": self.digit_spacing,
                "min": 0,
                "max": 20,
                "label": "Character Spacing",
                "description": "Space between characters",
                "post_change_function": "valueChanged"
            },
            "width_ratio": {
                "type": "int",
                "default": self.width_ratio,
                "min": 1,
                "max": 100,
                "label": "Width Ratio",
                "description": "Width to height ratio of digits (in percent)",
                "post_change_function": "valueChanged"
            },
            "total_decimals": {
                "type": "int",
                "default": self.total_decimals,
                "min": 1,
                "max": 50,
                "label": "Total Slots",
                "description": "Total number of digits to display",
                "post_change_function": "valueChanged"
            },
            "justify": {
                "type": "dropdown",
                "default": self.justify,
                "options": ["left", "right"],
                "label": "Justify",
                "description": "Text justification",
                "post_change_function": "valueChanged"
            },

            "text_color": {
                "type": "color",
                "default": self.text_color,
                "label": "Segment Color",
                "description": "Color of the digit segments",
                "post_change_function": "valueChanged"
            },
            "not_active_color": {
                "type": "color",
                "default": self.not_active_color,
                "label": "Not Active Color",
                "description": "Color of the digit segments when not active",
                "post_change_function": "valueChanged"
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
            },
            "padding": {
                "type": "int",
                "default": self.padding,
                "min": 0,
                "max": 20,
                "label": "Border Padding",
                "description": "Space between segments and border",
                "post_change_function": "valueChanged"
            }
        }

    def update_text(self, update_type=None):
        if update_type == "on_load":
            return
        if self.template == "":
            return
        self.text = "{"+self.template+"}"

    def processEvent(self, event, aircraft, smartdisplay):
        pass

    def valueChanged(self):
        self.initMod(self.pygamescreen, self.width, self.height)
        self._needs_reset = True





# vi: modeline tabstop=8 expandtab shiftwidth=4 softtabstop=4 syntax=python
