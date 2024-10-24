#!/usr/bin/env python

#################################################
# Module: Artificial horizon
# Topher 2021.

from lib.modules._module import Module
import pygame
import math

class artificalhorz(Module):
    def __init__(self):
        Module.__init__(self)
        self.name = "ArtificalHorz"
        self.MainColor = (255, 255, 255)
        self.SkyColorTop = (0, 102, 204)
        self.SkyColorBottom = (0, 153, 204)
        self.GroundColorTop = (153, 102, 51)
        self.GroundColorBottom = (102, 51, 0)
        self.LineColor = (255, 255, 255)
        self.pitch_range = 30
        self.width = 500
        self.height = 500
        self.font_size = 20
        self.bank_angle_radius = None

    def initMod(self, pygamescreen, width=None, height=None):
        if width is not None:
            self.width = width
        if height is not None:
            self.height = height
        Module.initMod(self, pygamescreen, self.width, self.height)
        print(f"Init Mod: {self.name} {self.width}x{self.height}")

        self.font = pygame.font.SysFont(None, self.font_size)
        self.surface = pygame.Surface((self.width, self.height))
        self.pixels_per_deg = self.height / (self.pitch_range * 2)
        
        if self.bank_angle_radius is None:
            self.bank_angle_radius = self.height / 3

        self.sky_gradient = self.create_gradient(self.SkyColorTop, self.SkyColorBottom, self.height // 2)
        self.ground_gradient = self.create_gradient(self.GroundColorTop, self.GroundColorBottom, self.height // 2)

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
        temp_surface.fill((0, 0, 0))

        # Calculate horizon line position
        horizon_y = int(self.height / 2 + (aircraft.pitch * self.pixels_per_deg))

        # Draw sky
        sky_height = max(0, min(horizon_y, self.height))
        if sky_height > 0:
            sky_surface = pygame.transform.scale(self.sky_gradient, (self.width, sky_height))
            temp_surface.blit(sky_surface, (0, 0))

        # Draw ground
        ground_start = max(0, min(horizon_y, self.height))
        ground_height = max(0, self.height - ground_start)
        if ground_height > 0:
            ground_surface = pygame.transform.scale(self.ground_gradient, (self.width, ground_height))
            temp_surface.blit(ground_surface, (0, ground_start))

        # Draw pitch lines
        self.draw_pitch_lines(temp_surface, horizon_y)

        # Rotate the surface
        rotated_surface = pygame.transform.rotate(temp_surface, aircraft.roll)
        rotated_rect = rotated_surface.get_rect(center=(self.width/2, self.height/2))

        # Create a surface for the final output, considering the rotation
        final_surface = pygame.Surface((self.width, self.height))
        final_surface.fill((0, 0, 0, 0))  # Fill with transparent color

        # Blit the rotated surface onto the final surface
        final_surface.blit(rotated_surface, (rotated_rect.x, rotated_rect.y))

        # Draw the final surface on the pygamescreen at the specified position, trimming off excess
        self.pygamescreen.blit(final_surface, (x, y), (0, 0, self.width, self.height))

        # Draw fixed elements
        self.draw_fixed_elements(x, y)

    def draw_pitch_lines(self, surface, horizon_y):
        for pitch in range(-self.pitch_range, self.pitch_range + 1, 5):
            if pitch == 0:
                continue
            y_pitch = horizon_y + (pitch * self.pixels_per_deg)
            length = 50 if pitch % 10 == 0 else 25
            pygame.draw.line(surface, self.LineColor, (self.width/2 - length, y_pitch), (self.width/2 + length, y_pitch), 2)
            
            if pitch % 10 == 0:
                text = self.font.render(str(abs(pitch)), True, self.LineColor)
                surface.blit(text, (self.width/2 + length + 5, y_pitch - text.get_height()/2))
                surface.blit(text, (self.width/2 - length - text.get_width() - 5, y_pitch - text.get_height()/2))

    def draw_fixed_elements(self, x, y):
        center_x, center_y = x + self.width/2, y + self.height/2
        
        # Draw center fixed aircraft reference
        pygame.draw.circle(self.pygamescreen, self.LineColor, (int(center_x), int(center_y)), 5, 2)
        pygame.draw.line(self.pygamescreen, self.LineColor, (int(center_x) - 40, int(center_y)), (int(center_x) - 15, int(center_y)), 2)
        pygame.draw.line(self.pygamescreen, self.LineColor, (int(center_x) + 15, int(center_y)), (int(center_x) + 40, int(center_y)), 2)

        # Draw roll indicator
        self.draw_roll_indicator(center_x, center_y)

    def draw_roll_indicator(self, center_x, center_y):
        r = self.bank_angle_radius
        for angle in [-60, -45, -30, -20, -10, 0, 10, 20, 30, 45, 60]:
            rad = math.radians(angle)
            x_roll = center_x + r * math.sin(rad)
            y_roll = center_y - r * math.cos(rad)
            length = 20 if angle % 30 == 0 else 10
            end_x = center_x + (r - length) * math.sin(rad)
            end_y = center_y - (r - length) * math.cos(rad)
            pygame.draw.line(self.pygamescreen, self.LineColor, (int(x_roll), int(y_roll)), (int(end_x), int(end_y)), 2)

        # Draw roll indicator triangle
        triangle_points = [
            (center_x, center_y - r),
            (center_x - 10, center_y - r + 20),
            (center_x + 10, center_y - r + 20),
        ]
        pygame.draw.polygon(self.pygamescreen, self.LineColor, triangle_points)

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
            "SkyColorBottom": {
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
            "GroundColorTop": {
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
