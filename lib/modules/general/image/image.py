#!/usr/bin/env python

#################################################
# Module: image
# Topher 2025
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
from lib.common.graphic.objects.TronViewImageObject import TronViewImageObject
import base64
import io

class image(Module):
    def __init__(self):
        Module.__init__(self)
        self.name = "Image"
        self.image: TronViewImageObject = None
        self.image_surface = None
        self.draw_mode = "fit"
        self.alpha = 255
        
    def initMod(self, pygamescreen, width=None, height=None):
        if width is None:
            width = 200
        if height is None:
            height = 50
        Module.initMod(self, pygamescreen, width, height)        
        self.surface2 = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        self.preload_image()

    def preload_image(self):
        # check if image is a dict
        if isinstance(self.image, dict):
            self.image = TronViewImageObject.from_dict(self.image)
        elif not isinstance(self.image, TronViewImageObject):
            # if it's not a TronViewImageObject, then make sure its None
            self.image = None
            return

        if self.image and self.image.base64:
            try:
                # Decode base64 to bytes
                decoded_data = base64.b64decode(self.image.base64)
                
                # Create a file-like object from the decoded data
                image_stream = io.BytesIO(decoded_data)
                
                # Load the PNG using pygame
                temp_surface = pygame.image.load(image_stream)
                
                # Convert to RGBA format
                self.image_surface = temp_surface.convert_alpha()
                
                # Update the stored dimensions to match actual image
                self.image.width = self.image_surface.get_width()
                self.image.height = self.image_surface.get_height()
                
                print(f"Successfully loaded image: {self.image.file_name} ({self.image.width}x{self.image.height})")
                
            except Exception as e:
                print(f"Error loading image {self.image.file_name}: {str(e)}")
                self.image_surface = None
        else:
            self.image_surface = None

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

        # Draw image if it exists
        if self.image and self.image_surface:
            # Create a copy of the image surface to modify alpha
            working_surface = self.image_surface.copy()
            if self.alpha < 255:
                working_surface.set_alpha(self.alpha)

            if self.draw_mode == "stretch":
                # Stretch to fill entire bounds
                scaled_img = pygame.transform.scale(working_surface, (self.width, self.height))
                self.surface2.blit(scaled_img, (0, 0))
                
            elif self.draw_mode == "center":
                # Center image at original size
                x_pos = (self.width - self.image.width) // 2
                y_pos = (self.height - self.image.height) // 2
                self.surface2.blit(working_surface, (x_pos, y_pos))
                
            else: # "fit" mode (default)
                # Maintain aspect ratio while fitting within bounds
                img_ratio = self.image.width / self.image.height
                surface_ratio = self.width / self.height
                
                if img_ratio > surface_ratio:
                    # Image is wider relative to height
                    new_width = self.width
                    new_height = int(self.width / img_ratio)
                else:
                    # Image is taller relative to width
                    new_height = self.height
                    new_width = int(self.height * img_ratio)
                
                scaled_img = pygame.transform.scale(working_surface, (new_width, new_height))
                x_pos = (self.width - new_width) // 2
                y_pos = (self.height - new_height) // 2
                self.surface2.blit(scaled_img, (x_pos, y_pos))
        
        # Blit to screen
        self.pygamescreen.blit(self.surface2, (x, y))

    def get_module_options(self):
        data_fields = shared.Dataship._get_all_fields()
        
        return {
            "draw_mode": {
                "type": "dropdown",
                "default": self.draw_mode,
                "label": "Draw Mode",
                "description": "Select the draw mode for the image",
                "options": ["fit", "stretch", "center"],
                "post_change_function": "preload_image"
            },
            "image": {
                "type": "filedrop",
                "default": self.image,
                "label": "Image (Drag and Drop)",
                "description": "Select an image file to display",
                "post_change_function": "preload_image"
            },
            "alpha": {
                "type": "int",
                "default": self.alpha,
                "label": "Alpha",
                "min": 0,
                "max": 255,
                "description": "Enable alpha channel for the image"
            }
        }

    # def set_image(self, image_file):
    #     self.image = image_file