#!/usr/bin/env python

#################################################
# Module: Artificial horizon
# Topher 2021.

from lib.modules._module import Module
from lib import hud_graphics
from lib import hud_utils
from lib import smartdisplay
import pygame
import math
import numpy as np

class artificalhorz(Module):
    def __init__(self):
        Module.__init__(self)
        self.name = "ArtificalHorz"
        self.MainColor = (255, 255, 255)
        self.SkyColor = (0, 153, 204)
        self.SkyColorTop = (0, 102, 204)  # Darker blue for top of sky
        self.GroundColor = (153, 102, 51)
        self.GroundColorBottom = (102, 51, 0)  # Darker brown for bottom of ground
        self.LineColor = (255, 255, 255)
        self.pitch_range = 30  # Degrees of pitch to show above and below horizon
        self.width = 500
        self.height = 500
        self.sky_gradient = None
        self.ground_gradient = None

    def initMod(self, pygamescreen, width=None, height=None):
        if width is not None:
            self.width = width
        if height is not None:
            self.height = height
        Module.initMod(self, pygamescreen, self.width, self.height)
        print(f"Init Mod: {self.name} {self.width}x{self.height}")

        self.font = pygame.font.SysFont(None, int(self.height / 20))
        self.surface = pygame.Surface((self.width, self.height))

        # Pre-render sky gradient
        self.sky_gradient = self.create_gradient(self.SkyColorTop, self.SkyColor, self.height // 2)

        # Pre-render ground gradient
        self.ground_gradient = self.create_gradient(self.GroundColor, self.GroundColorBottom, self.height // 2)

    def create_gradient(self, color1, color2, height):
        gradient = pygame.Surface((1, height))
        for i in range(height):
            r = int(color1[0] + (color2[0] - color1[0]) * i / height)
            g = int(color1[1] + (color2[1] - color1[1]) * i / height)
            b = int(color1[2] + (color2[2] - color1[2]) * i / height)
            gradient.set_at((0, i), (r, g, b))
        return gradient

    def draw(self, aircraft, smartdisplay, pos=(None, None)):
        if pos[0] is None or pos[1] is None:
            x, y = 0, 0
        else:
            x, y = pos

        # Create a temporary surface for drawing
        temp_surface = pygame.Surface((self.width, self.height))

        # Calculate horizon line position
        horizon_y = self.height / 2 - (aircraft.pitch / self.pitch_range) * (self.height / 2)

        # Draw sky gradient
        sky_rect = pygame.Rect(0, 0, self.width, horizon_y)
        pygame.transform.scale(self.sky_gradient, (self.width, int(horizon_y)), temp_surface.subsurface(sky_rect))

        # Draw ground gradient
        ground_rect = pygame.Rect(0, horizon_y, self.width, self.height - horizon_y)
        pygame.transform.scale(self.ground_gradient, (self.width, int(self.height - horizon_y)), temp_surface.subsurface(ground_rect))

        # Draw horizon line
        pygame.draw.line(temp_surface, self.LineColor, (0, horizon_y), (self.width, horizon_y), 2)

        # Draw pitch lines
        for pitch in range(-self.pitch_range, self.pitch_range + 1, 5):
            if pitch == 0:
                continue
            y_pitch = horizon_y - (pitch / self.pitch_range) * (self.height / 2)
            length = 50 if pitch % 10 == 0 else 25
            pygame.draw.line(temp_surface, self.LineColor, (self.width/2 - length, y_pitch), (self.width/2 + length, y_pitch), 2)
            
            if pitch % 10 == 0:
                text = self.font.render(str(abs(pitch)), True, self.LineColor)
                temp_surface.blit(text, (self.width/2 + length + 5, y_pitch - text.get_height()/2))
                temp_surface.blit(text, (self.width/2 - length - text.get_width() - 5, y_pitch - text.get_height()/2))

        # Draw roll indicator
        roll_indicator_radius = self.height / 3
        center = (self.width / 2, self.height / 2)
        for angle in [-60, -45, -30, -20, -10, 0, 10, 20, 30, 45, 60]:
            rad = math.radians(angle - aircraft.roll)
            x_roll = center[0] + roll_indicator_radius * math.sin(rad)
            y_roll = center[1] - roll_indicator_radius * math.cos(rad)
            length = 20 if angle % 30 == 0 else 10
            end_x = center[0] + (roll_indicator_radius - length) * math.sin(rad)
            end_y = center[1] - (roll_indicator_radius - length) * math.cos(rad)
            pygame.draw.line(temp_surface, self.LineColor, (x_roll, y_roll), (end_x, end_y), 2)

        # Draw roll indicator triangle
        triangle_points = [
            (center[0], center[1] - roll_indicator_radius),
            (center[0] - 10, center[1] - roll_indicator_radius + 20),
            (center[0] + 10, center[1] - roll_indicator_radius + 20),
        ]
        pygame.draw.polygon(temp_surface, self.LineColor, triangle_points)

        # Rotate the surface
        rotated_surface = pygame.transform.rotate(temp_surface, aircraft.roll)
        rotated_rect = rotated_surface.get_rect(center=(self.width/2, self.height/2))

        # Create a surface for the final output, considering the rotation
        final_surface = pygame.Surface((self.width, self.height))
        final_surface.fill((0, 0, 0, 0))  # Fill with transparent color

        # Blit the rotated surface onto the final surface
        final_surface.blit(rotated_surface, (rotated_rect.x, rotated_rect.y))

        # Draw the final surface on the screen at the specified position, trimming off excess
        self.pygamescreen.blit(final_surface, (x, y), (0, 0, self.width, self.height))

        # Draw center fixed aircraft reference
        center_x, center_y = x + self.width/2, y + self.height/2
        pygame.draw.circle(self.pygamescreen, self.LineColor, (int(center_x), int(center_y)), 5, 2)
        pygame.draw.line(self.pygamescreen, self.LineColor, (int(center_x) - 40, int(center_y)), (int(center_x) - 15, int(center_y)), 2)
        pygame.draw.line(self.pygamescreen, self.LineColor, (int(center_x) + 15, int(center_y)), (int(center_x) + 40, int(center_y)), 2)

    def clear(self):
        pass

    def processEvent(self, event):
        pass
    
    def get_module_options(self):
        return {
            "MainColor": {
                "type": "color",
                "default": (255, 255, 255),
                "label": "Main Color",
                "description": "Color of the main lines and text.",
            },
            "SkyColor": {
                "type": "color",
                "default": (0, 153, 204),
                "label": "Sky Color (Bottom)",
                "description": "Color of the sky at the horizon.",
            },
            "SkyColorTop": {
                "type": "color",
                "default": (0, 102, 204),
                "label": "Sky Color (Top)",
                "description": "Color of the sky at the top.",
            },
            "GroundColor": {
                "type": "color",
                "default": (153, 102, 51),
                "label": "Ground Color (Top)",
                "description": "Color of the ground at the horizon.",
            },
            "GroundColorBottom": {
                "type": "color",
                "default": (102, 51, 0),
                "label": "Ground Color (Bottom)",
                "description": "Color of the ground at the bottom.",
            },
        }

# vi: modeline tabstop=8 expandtab shiftwidth=4 softtabstop=4 syntax=python
