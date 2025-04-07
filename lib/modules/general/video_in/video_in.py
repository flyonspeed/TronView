#!/usr/bin/env python

#################################################
# Module: video_in
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
import base64
import io
import cv2
import numpy as np

class video_in(Module):
    def __init__(self):
        Module.__init__(self)
        self.name = "VideoIn"
        self.image_surface = None
        self.draw_mode = "fit"
        self.alpha = 255
        self.cap = None
        self.video_source = 0  # Default to first video source
        
    def initMod(self, pygamescreen, width=None, height=None):
        if width is None:
            width = 200
        if height is None:
            height = 50
        Module.initMod(self, pygamescreen, width, height)        
        self.surface2 = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        self.initialize_webcam()

    def initialize_webcam(self):
        if self.cap is not None:
            self.cap.release()
        try:
            self.cap = cv2.VideoCapture(self.video_source)
            if not self.cap.isOpened():
                print(f"Error: Could not open video source {self.video_source}")
                self.cap = None
        except Exception as e:
            print(f"Error initializing webcam: {str(e)}")
            self.cap = None

    def preload_image(self):
        # This method is kept for backward compatibility
        pass

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

        # Capture and process webcam frame
        if self.cap is not None:
            ret, frame = self.cap.read()
            if ret:
                # Convert BGR to RGB
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                # Rotate frame to correct orientation
                frame = cv2.rotate(frame, cv2.ROTATE_180)
                # Convert to pygame surface
                frame_surface = pygame.surfarray.make_surface(frame)
                
                if self.draw_mode == "stretch":
                    scaled_img = pygame.transform.scale(frame_surface, (self.width, self.height))
                    self.surface2.blit(scaled_img, (0, 0))
                elif self.draw_mode == "center":
                    x_pos = (self.width - frame.shape[1]) // 2
                    y_pos = (self.height - frame.shape[0]) // 2
                    self.surface2.blit(frame_surface, (x_pos, y_pos))
                else:  # "fit" mode (default)
                    img_ratio = frame.shape[1] / frame.shape[0]
                    surface_ratio = self.width / self.height
                    
                    if img_ratio > surface_ratio:
                        new_width = self.width
                        new_height = int(self.width / img_ratio)
                    else:
                        new_height = self.height
                        new_width = int(self.height * img_ratio)
                    
                    scaled_img = pygame.transform.scale(frame_surface, (new_width, new_height))
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
                "description": "Select the draw mode for the video",
                "options": ["fit", "stretch", "center"],
                "post_change_function": "preload_image"
            },
            "video_source": {
                "type": "int",
                "default": self.video_source,
                "label": "Video Source",
                "description": "Select the video source (0 for first camera)",
                "min": 0,
                "max": 10,
                "post_change_function": "initialize_webcam"
            },
            "alpha": {
                "type": "int",
                "default": self.alpha,
                "label": "Alpha",
                "min": 0,
                "max": 255,
                "description": "Enable alpha channel for the video"
            }
        }

    def __del__(self):
        if self.cap is not None:
            self.cap.release()