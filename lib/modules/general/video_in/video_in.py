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
        self.video_source = -1  # Default to no video source
        self.rotation = 0  # Rotation angle in degrees
        self.resolution = "medium"  # Default resolution setting
        self.resolution_presets = {
            "low": (320, 240),
            "medium": (640, 480),
            "high": (1280, 720)
        }
        self.convert_bgr_to_rgb = True  # Default to converting BGR to RGB
        self.threshold_enabled = False  # Threshold control
        self.threshold_value = 128      # Default threshold value
        self.threshold_max = 255        # Maximum value for threshold
        # New threshold properties
        self.threshold_type = "binary"  # binary, binary_inv, trunc, tozero, tozero_inv
        self.adaptive_method = "none"   # none, mean, gaussian
        self.adaptive_block_size = 11   # Must be odd number
        self.adaptive_c = 2             # Constant subtracted from mean/gaussian
        self.use_otsu = False          # Whether to use Otsu's method
        self.skip_frames = 0           # Number of frames to skip between reads
        self.frame_counter = 0         # Counter to track skipped frames
        self.last_frame = None         # Store the last captured frame
        
    def initMod(self, pygamescreen, width=None, height=None):
        if width is None:
            width = 400
        if height is None:
            height = 400
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
                return
                
            # Set resolution based on the selected preset
            width, height = self.resolution_presets[self.resolution]
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
            print(f"VideoIn: Resolution set to {width}x{height}")
            
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

        # Return early if no video source is selected
        if self.video_source == -1:
            return

        # Clear surface
        #self.surface2.fill((0,0,0,0))

        # Capture and process webcam frame
        if self.cap is not None:
            frame = None
            ret = False
            
            # Skip frames if configured
            if self.frame_counter < self.skip_frames:
                self.frame_counter += 1
                #self.cap.read()  # Read and discard the frame
                if self.last_frame is not None:
                    frame = self.last_frame.copy()  # Use the last frame
            else:
                # Reset counter and read frame
                self.frame_counter = 0
                ret, new_frame = self.cap.read()
                if ret:
                    frame = new_frame
                    self.last_frame = frame.copy()  # Store the new frame
                elif self.last_frame is not None:
                    frame = self.last_frame.copy()  # Use last frame if read failed

            if frame is not None:
                # Apply threshold if enabled
                if self.threshold_enabled:
                    # Convert to grayscale first
                    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                    
                    # Handle different threshold types
                    if self.adaptive_method != "none":
                        # Ensure block size is odd and valid
                        block_size = max(3, self.adaptive_block_size)  # Ensure minimum size of 3
                        block_size = block_size + (1 if block_size % 2 == 0 else 0)  # Make odd if even
                        
                        # Adaptive thresholding
                        adapt_method = cv2.ADAPTIVE_THRESH_MEAN_C if self.adaptive_method == "mean" else cv2.ADAPTIVE_THRESH_GAUSSIAN_C
                        binary = cv2.adaptiveThreshold(
                            gray,
                            self.threshold_max,
                            adapt_method,
                            cv2.THRESH_BINARY,
                            block_size,
                            self.adaptive_c
                        )
                    else:
                        # Regular thresholding
                        threshold_types = {
                            "binary": cv2.THRESH_BINARY,
                            "binary_inv": cv2.THRESH_BINARY_INV,
                            "trunc": cv2.THRESH_TRUNC,
                            "tozero": cv2.THRESH_TOZERO,
                            "tozero_inv": cv2.THRESH_TOZERO_INV
                        }
                        
                        thresh_type = threshold_types[self.threshold_type]
                        if self.use_otsu:
                            thresh_type |= cv2.THRESH_OTSU
                            _, binary = cv2.threshold(gray, 0, self.threshold_max, thresh_type)
                        else:
                            _, binary = cv2.threshold(gray, self.threshold_value, self.threshold_max, thresh_type)
                    
                    # Convert back to BGR for consistency
                    frame = cv2.cvtColor(binary, cv2.COLOR_GRAY2BGR)

                # Convert BGR to RGB if enabled
                if self.convert_bgr_to_rgb:
                    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                
                # Rotate frame to correct orientation
                #frame = cv2.rotate(frame, cv2.ROTATE_180)
                # Convert to pygame surface
                frame_surface = pygame.surfarray.make_surface(frame)
                
                # Apply rotation if needed
                if self.rotation == 1:
                    frame_surface = pygame.transform.rotate(frame_surface, 90)
                elif self.rotation == 2:
                    frame_surface = pygame.transform.rotate(frame_surface, 180)
                elif self.rotation == 3:
                    frame_surface = pygame.transform.rotate(frame_surface, 270)
                
                # Apply alpha if not fully opaque
                if self.alpha != 255:
                    frame_surface.set_alpha(self.alpha)
                
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
        
        options = {
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
                "label": "Video Source (-1:None)",
                "description": "Select the video source (0 for first camera)",
                "min": -1,
                "max": 10,
                "post_change_function": "initialize_webcam"
            },
            "resolution": {
                "type": "dropdown",
                "default": self.resolution,
                "label": "Resolution",
                "description": "Select the video resolution (lower resolution = better performance)",
                "options": ["low", "medium", "high"],
                "post_change_function": "initialize_webcam"
            },
            "skip_frames": {
                "type": "int",
                "default": self.skip_frames,
                "label": "Skip Frames",
                "description": "Number of frames to skip between reads (0-100)",
                "min": 0,
                "max": 100
            },
            "convert_bgr_to_rgb": {
                "type": "bool",
                "default": self.convert_bgr_to_rgb,
                "label": "Convert BGR to RGB",
                "description": "Convert from OpenCV BGR to RGB format (recommended for correct colors)",
            },
            "alpha": {
                "type": "int",
                "default": self.alpha,
                "label": "Alpha",
                "min": 0,
                "max": 255,
                "description": "Enable alpha channel for the video"
            },
            "rotation": {
                "type": "int",
                "default": self.rotation,
                "label": "Rotation",
                "min": 0,
                "max": 3,
                "description": "Rotate the video"
            },
            "threshold_enabled": {
                "type": "bool",
                "default": self.threshold_enabled,
                "label": "Threshold Enabled",
                "description": "Enable threshold processing for the video"
            },
            "threshold_type": {
                "type": "dropdown",
                "default": self.threshold_type,
                "label": "Threshold Type",
                "description": "Select the type of thresholding to apply",
                "options": ["binary", "binary_inv", "trunc", "tozero", "tozero_inv"]
            },
            "adaptive_method": {
                "type": "dropdown",
                "default": self.adaptive_method,
                "label": "Adaptive Method",
                "description": "Select adaptive thresholding method",
                "options": ["none", "mean", "gaussian"]
            },
            "adaptive_block_size": {
                "type": "int",
                "default": self.adaptive_block_size,
                "label": "Adaptive Block Size",
                "min": 3,
                "max": 99,
                "step": 2,  # Must be odd number
                "description": "Block size for adaptive threshold"
            },
            "adaptive_c": {
                "type": "int",
                "default": self.adaptive_c,
                "label": "Adaptive C",
                "min": -255,
                "max": 255,
                "description": "Constant subtracted from mean/gaussian"
            },
            "use_otsu": {
                "type": "bool",
                "default": self.use_otsu,
                "label": "Use Otsu's Method",
                "description": "Automatically determine optimal threshold value"
            },
            "threshold_value": {
                "type": "int",
                "default": self.threshold_value,
                "label": "Threshold Value",
                "min": 0,
                "max": 255,
                "description": "Value for thresholding"
            },
            "threshold_max": {
                "type": "int",
                "default": self.threshold_max,
                "label": "Threshold Max",
                "min": 0,
                "max": 255,
                "description": "Maximum value for thresholding"
            }
        }
        # Merge with existing options
        existing_options = super().get_module_options()
        existing_options.update(options)
        return existing_options

    def __del__(self):
        if self.cap is not None:
            self.cap.release()