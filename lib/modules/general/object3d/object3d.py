#!/usr/bin/env python

#################################################
# Module: object3d
# Topher 2024

from lib.modules._module import Module
from lib import hud_graphics
from lib import hud_utils
from lib import smartdisplay
import pygame
import math


class object3d(Module):
    # called only when object is first created.
    def __init__(self):
        Module.__init__(self)
        self.name = "object 3D"  # set name
        self.MainColor = (255,255,255)
        self.font_size = 16

    # called once for setup
    def initMod(self, pygamescreen, width=None, height=None):
        if width is None:
            width = 500 # default width
        if height is None:
            height = 500 # default height
        Module.initMod(
            self, pygamescreen, width, height
        )  # call parent init screen.
        print(("Init Mod: %s %dx%d"%(self.name,self.width,self.height)))

        # fonts
        self.font = pygame.font.SysFont(
            None, self.font_size
        )
        # Create a surface with per-pixel alpha
        self.surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)

    # called every redraw for the mod
    def draw(self, aircraft, smartdisplay, pos=(None, None)):
        # Clear the surface
        self.surface.fill((0, 0, 0, 0))

        # Calculate the cube size based on the smaller dimension of the surface
        cube_size = min(self.width, self.height) * 1  # Use % of the smaller dimension

        # Set the center of the cube to the center of the surface
        x = self.width // 2
        y = self.height // 2

        # Define cube vertices
        vertices = [
            [-1, -1, -1], # front left bottom
            [1, -1, -1], # front right bottom
            [1, 1, -1], # front right top
            [-1, 1, -1], # front left top
            [-1, -1, 1], # back left bottom
            [1, -1, 1], # back right bottom
            [1, 1, 1], # back right top
            [-1, 1, 1] # back left top
        ]

        # Convert degrees to radians
        pitch = math.radians(aircraft.pitch)
        roll = math.radians(aircraft.roll)
        yaw = math.radians(aircraft.mag_head)

        # Define rotation matrices
        def rotate_x(v, angle):
            return [v[0], v[1] * math.cos(angle) - v[2] * math.sin(angle), v[1] * math.sin(angle) + v[2] * math.cos(angle)]

        def rotate_y(v, angle):
            return [v[0] * math.cos(angle) + v[2] * math.sin(angle), v[1], -v[0] * math.sin(angle) + v[2] * math.cos(angle)]

        def rotate_z(v, angle):
            return [v[0] * math.cos(angle) - v[1] * math.sin(angle), v[0] * math.sin(angle) + v[1] * math.cos(angle), v[2]]

        # Apply rotations to vertices
        rotated_vertices = []
        for v in vertices:
            rotated = rotate_z(rotate_y(rotate_x(v, pitch), yaw), roll)
            # Project 3D point to 2D surface
            scale = cube_size / (4 + rotated[2])
            x2d = int(rotated[0] * scale + x)
            y2d = int(rotated[1] * scale + y)
            rotated_vertices.append((x2d, y2d))

        # Draw edges
        edges = [
            (0, 1), (1, 2), (2, 3), (3, 0),  # Front face
            (4, 5), (5, 6), (6, 7), (7, 4),  # Back face
            (0, 4), (1, 5), (2, 6), (3, 7)   # Connecting edges
        ]

        for edge in edges:
            pygame.draw.line(self.surface, self.MainColor, rotated_vertices[edge[0]], rotated_vertices[edge[1]], 2)

        # Draw face features on the front face
        front_face = rotated_vertices[:4]  # First four vertices are the front face

        # Calculate center and size of the front face
        center_x = sum(v[0] for v in front_face) // 4
        center_y = sum(v[1] for v in front_face) // 4
        face_width = max(v[0] for v in front_face) - min(v[0] for v in front_face)
        face_height = max(v[1] for v in front_face) - min(v[1] for v in front_face)

        # Draw eyes
        eye_size = max(face_width, face_height) // 16
        left_eye_pos = (center_x - face_width // 4, center_y - face_height // 4)
        right_eye_pos = (center_x + face_width // 4, center_y - face_height // 4)
        pygame.draw.circle(self.surface, self.MainColor, left_eye_pos, eye_size)
        pygame.draw.circle(self.surface, self.MainColor, right_eye_pos, eye_size)

        # Draw nose
        nose_size = max(face_width, face_height) // 20
        nose_pos = (center_x, center_y)
        pygame.draw.circle(self.surface, self.MainColor, nose_pos, nose_size)

        # Draw mouth
        mouth_width = face_width // 2
        mouth_height = face_height // 8
        mouth_rect = pygame.Rect(center_x - mouth_width // 2, center_y + face_height // 4 - mouth_height // 2, mouth_width, mouth_height)
        pygame.draw.arc(self.surface, self.MainColor, mouth_rect, math.pi, 2 * math.pi, 2)

        # Draw the surface onto the main screen
        smartdisplay.pygamescreen.blit(self.surface, pos if pos != (None, None) else (0, 0))

    # called before screen draw.  To clear the screen to your favorite color.
    def clear(self):
        #self.ahrs_bg.fill((0, 0, 0))  # clear screen
        print("clear")

    # handle key events
    def processEvent(self, event):
        print("processEvent")
    
    def get_module_options(self):
        return {
            "MainColor": {
                "type": "color",
                "default": (255,255,255),
                "label": "Main Color",
                "description": "Color of the main line.",
            }
        }


# vi: modeline tabstop=8 expandtab shiftwidth=4 softtabstop=4 syntax=python
