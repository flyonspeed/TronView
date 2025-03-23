#!/usr/bin/env python

#################################################
# Module: text
# Topher 2024.
# 2/9/2025 - added dataship refactor.

import inspect
from lib.modules._module import Module
from lib import hud_graphics
from lib import hud_utils
from lib import smartdisplay
from lib.common.dataship import dataship
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
        self.text_min_size = 0
        self.show_text_bg = False
        self.text_bg_color = (0,0,0)
        self.text_bg_alpha = 100
        self.box_color = (255,255,255)
        self.box_weight = 0
        self.box_radius = 0
        self.box_padding = 1
        self.template = ""
        self.shrink_right_chars = 0
        self.shrink_size = 30
        # Cache variables
        self._cached_text = None
        self._cached_font_props = None
        self._cached_dimensions = None
        self._cached_surfaces = None
    # called once for setup
    def initMod(self, pygamescreen, width=None, height=None):
        if width is None:
            width = 200 # default width
        if height is None:
            height = 50 # default height
        Module.initMod(
            self, pygamescreen, width, height
        )  # call parent init screen.
        if shared.Dataship.debug_mode > 0:
            print(("Init Mod: %s %dx%d"%(self.name,self.width,self.height)))
        # does the self.font_name variable exist?
            
        self.font = pygame.font.SysFont(self.font_name, self.font_size, self.font_bold)
        # does the self.text variable exist?
        self.surface2 = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        self.surface2.fill((0,0,0,0))
        # Remove the self.surface creation and fill

    def _get_font_props(self):
        return (self.font_name, self.font_size, self.font_bold, self.shrink_right_chars, self.shrink_size)

    def _calculate_text_dimensions(self, text):

        # check if self.text_min_size is greater than 0
        if self.text_min_size > 0:
            # check if the text is less than the text_min_size
            if len(text) < self.text_min_size:
                # add spaces to the text (pad on left side)
                text =  " " * (self.text_min_size - len(text)) + text

        if (self._cached_text == text and 
            self._cached_font_props == self._get_font_props() and 
            self._cached_dimensions is not None and
            self._cached_surfaces is not None):
            return self._cached_dimensions, self._cached_surfaces

        surfaces = {}
        if self.shrink_right_chars > 0 and len(text) > self.shrink_right_chars:
            main_text = text[:-self.shrink_right_chars]
            shrunk_text = text[-self.shrink_right_chars:]
            
            main_label = self.font.render(main_text, True, self.text_color)
            shrunk_font_size = max(10, self.font_size - self.shrink_size)
            shrunk_font = pygame.font.SysFont(self.font_name, shrunk_font_size, self.font_bold)
            shrunk_label = shrunk_font.render(shrunk_text, True, self.text_color)
            
            total_width = main_label.get_width() + shrunk_label.get_width()
            total_height = max(main_label.get_height(), shrunk_label.get_height())
            
            # If total width is less than text_min_size, add spaces to main text
            if self.text_min_size > 0 and total_width < self.text_min_size:
                # Calculate space width using a single space
                space_width = self.font.render("W", True, self.text_color).get_width()
                if space_width > 0:  # Prevent division by zero
                    # Calculate how many spaces we need
                    extra_spaces_needed = math.ceil((self.text_min_size - total_width) / space_width)
                    main_text = main_text + "W" * extra_spaces_needed
                    # Re-render main text with added spaces
                    main_label = self.font.render(main_text, True, self.text_color)
                    total_width = main_label.get_width() + shrunk_label.get_width()
            
            surfaces['main'] = main_label
            surfaces['shrunk'] = shrunk_label
            surfaces['shrunk_font'] = shrunk_font
        else:
            # First render to get initial width
            label = self.font.render(text, True, self.text_color)
            total_width = label.get_width()
            total_height = label.get_height()
            
            # If width is less than text_min_size, add spaces
            if self.text_min_size > 0 and total_width < self.text_min_size:
                # Calculate space width using a single space
                space_width = self.font.render("W", True, self.text_color).get_width()
                if space_width > 0:  # Prevent division by zero
                    # Calculate how many spaces we need
                    extra_spaces_needed = math.ceil((self.text_min_size - total_width) / space_width)
                    text = text + "W" * extra_spaces_needed
                    # Re-render with added spaces
                    label = self.font.render(text, True, self.text_color)
                    total_width = label.get_width()
            
            surfaces['label'] = label

        # Cache the results
        self._cached_text = text
        self._cached_font_props = self._get_font_props()
        self._cached_dimensions = (total_width, total_height)
        self._cached_surfaces = surfaces
        
        return (total_width, total_height), surfaces

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

        # Get the text content
        text = self.parse_text(self.text, aircraft)
        
        # Get dimensions and surfaces from cache or calculate them
        (total_width, total_height), surfaces = self._calculate_text_dimensions(text)

        # Add padding to dimensions if needed
        padding = self.box_padding if self.box_padding > 0 else 0
        padded_width = total_width + (padding * 2)
        padded_height = total_height + (padding * 2)

        # Create a new surface with padding if needed
        if padding > 0 or self.show_text_bg:
            new_surface = pygame.Surface((padded_width, padded_height), pygame.SRCALPHA)
            new_surface.fill((0,0,0,0))
            self.surface2 = new_surface

        # Draw background if enabled
        if self.show_text_bg:
            bg_surface = pygame.Surface((padded_width, padded_height), pygame.SRCALPHA)
            r = int(max(0, min(255, self.text_bg_color[0])))
            g = int(max(0, min(255, self.text_bg_color[1])))
            b = int(max(0, min(255, self.text_bg_color[2])))
            a = int(max(0, min(255, self.text_bg_alpha)))
            bg_surface.fill((r, g, b, a))
            self.surface2.blit(bg_surface, (0, 0))

        # Now render the text with padding offset
        if self.shrink_right_chars > 0 and len(text) > self.shrink_right_chars:
            # Render main text
            self.surface2.blit(surfaces['main'], (padding, padding))
            
            # Position shrunk text right after main text
            main_width = surfaces['main'].get_width()
            shrunk_y = padding + (surfaces['main'].get_height() - surfaces['shrunk'].get_height()) // 2
            self.surface2.blit(surfaces['shrunk'], (main_width + padding, shrunk_y))
        else:
            # Regular rendering without shrinking
            self.surface2.blit(surfaces['label'], (padding, padding))

        if self.box_weight > 0:
            # If we have padding, draw box around entire surface
            if padding > 0:
                surface_rect = pygame.Rect(0, 0, padded_width, padded_height)
            else:
                surface_rect = self.surface2.get_bounding_rect()
                # add a little padding to the box
                surface_rect.x -= 2
                surface_rect.y -= 2
                surface_rect.width += 4
                surface_rect.height += 4
            # draw a box around the text
            pygame.draw.rect(self.surface2, self.box_color, surface_rect, self.box_weight, self.box_radius)

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

        #data_fields = shared.Dataship._get_all_fields()
        #print(f"templates: {data_fields}")

        return {
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
            "text_min_size": {
                "type": "int",
                "default": self.text_min_size,
                "min": 0,
                "max": 30,
                "label": "Text Min Size",
                "description": "Minimum size of the text to use"
            },
            "text_color": {
                "type": "color",
                "default": self.text_color,
                "label": "Text Color",
                "description": "Color of the text to use"
            },
            "shrink_right_chars": {
                "type": "int",
                "min": 0,
                "max": 100,
                "default": self.shrink_right_chars,
                "label": "Shrink Right Chars",
                "description": "Number of characters to shrink the text to the right"
            },
            "shrink_size": {
                "type": "int",
                "min": 0,
                "max": 100,
                "default": self.shrink_size,
                "label": "Shrink Size",
                "description": "Size of the shrink to use"
            },
            "show_text_bg": {
                "type": "bool",
                "default": self.show_text_bg,
                "label": "Show Text Background",
                "description": "Show the text background"
            },
            "text_bg_color": {
                "type": "color",
                "default": self.text_bg_color,
                "label": "Text Background Color",
                "description": "Color of the text background to use"
            },
            "text_bg_alpha": {
                "type": "int",
                "default": self.text_bg_alpha,
                "min": 0,
                "max": 255,
                "label": "Text Background Alpha",
                "description": "Alpha of the text background to use"
            },
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
            },
            "box_padding": {
                "type": "int",
                "default": self.box_padding,
                "min": 0,
                "max": 20,
                "label": "Box Padding",
                "description": "Padding between text and box"
            }
        }

    def update_text(self, update_type=None):
        #print(f"update_text: {update_type}")
        if update_type == "on_load": # in "on_load" then we are loading the module from a json file
            return
        if self.template == "":
            return
        # else set the text to the the value.
        self.text = "{"+self.template+"}"
        #self.buildFont()

    # handle events
    def processEvent(self,event,aircraft,smartdisplay):

        pass



# vi: modeline tabstop=8 expandtab shiftwidth=4 softtabstop=4 syntax=python
