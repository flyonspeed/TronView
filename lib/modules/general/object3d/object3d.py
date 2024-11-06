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
from lib.common import shared
from lib.common.dataship.dataship import Dataship

class object3d(Module):
    # called only when object is first created.
    def __init__(self):
        Module.__init__(self)
        self.name = "object 3D"  # set name
        self.MainColor = (255,255,255)
        self.font_size = 30

        self.source_imu_index_name = ""
        self.source_imu_index = 0

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
        self.imu_ids = []

        self.draw_arrows = True
        self.zero_position = None

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

        # if imu is available and the self.source_imu_index is not larger than the number of imus.
        if aircraft.imus and self.source_imu_index < len(aircraft.imus):
            source_imu = aircraft.imus[self.source_imu_index]
            new_position = self.getUpdatedPostion(source_imu.pitch, source_imu.roll, source_imu.yaw)
            pitch = new_position[0]
            roll = new_position[1]
            yaw = new_position[2]
        else:
            roll = None
            pitch = None
            yaw = None

        # error with IMU data..
        if roll is None or pitch is None:
            # draw a red X on the screen.
            pygame.draw.line(self.surface, (255,0,0), (0,0), (self.width,self.height), 4)
            pygame.draw.line(self.surface, (255,0,0), (self.width,0), (0,self.height), 4)
            text = self.font.render("IMU-"+str(self.source_imu_index+1) +" ERROR", True, (255,0,0))
            text_rect = text.get_rect(center=(self.width//2, self.height//2-20))
            self.surface.blit(text, text_rect)
            next_line = 30
            # check if index is bigger then size
            if self.source_imu_index >= len(aircraft.imus):
                if len(self.source_imu_index_name) > 0:
                    text = self.font.render("NotFound\n"+self.source_imu_index_name, True, (255,0,0))
                    text_rect = text.get_rect(center=(self.width//2, self.height//2+next_line))
                    self.surface.blit(text, text_rect)
                    next_line += 20
                else:
                    text = self.font.render("NotFound", True, (255,0,0))
                    text_rect = text.get_rect(center=(self.width//2, self.height//2+next_line))
                    self.surface.blit(text, text_rect)
                    next_line += 20
            smartdisplay.pygamescreen.blit(self.surface, pos)
            # if self.source_imu_index_name is not empty then print the name in pygame font to self.surface.
            return

        # Convert degrees to radians
        pitch = math.radians(pitch)
        roll = math.radians(roll)
        if yaw is not None:
            yaw = math.radians(yaw)
        else:
            #draw NO YAW text on the screen.
            text = self.font.render("NO YAW", True, (255,0,0))
            text_rect = text.get_rect(center=(self.width//2, self.height-15))
            self.surface.blit(text, text_rect)
            yaw = 0

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
        # get the imu list of imu objects
        imu_list = shared.Dataship.imus
        # go through imu list and get the id and name.
        self.imu_ids = []
        if isinstance(imu_list, dict):
            # If it's a dictionary, iterate through values
            for imu_id, imu in imu_list.items():
                #print(f"IMU {imu_id}:", imu.id)
                self.imu_ids.append(str(imu.id))
        if len(self.source_imu_index_name) == 0: # if no name.
            self.source_imu_index_name = self.imu_ids[self.source_imu_index]  # select first one.

        return {
            "source_imu_index_name": {
                "type": "dropdown",
                "label": "Source IMU",
                "description": "IMU to use for the 3D object.",
                "options": self.imu_ids,
                "post_change_function": "changeSourceIMU"
            },
            "source_imu_index": {
                "type": "int",
                "hidden": True,  # hide from the UI, but save to json screen file.
                "default": 0
            },
            "MainColor": {
                "type": "color",
                "default": (255,255,255),
                "label": "Main Color",
                "description": "Color of the main line.",
            }
        }
    
    def changeSourceIMU(self):
        # source_imu_index_name got changed. find the index of the imu id in the imu list.
        self.source_imu_index = self.imu_ids.index(self.source_imu_index_name)
        #print("source_imu_index==", self.source_imu_index)

    def processClick(self, aircraft: Dataship, mx, my):
        # When clicked, set the current position as the new zero reference point
        if aircraft.imus and self.source_imu_index < len(aircraft.imus):
            source_imu = aircraft.imus[self.source_imu_index]
            self.zero_position = [
                source_imu.pitch,
                source_imu.roll,
                source_imu.yaw
            ]
            print("New zero position set:", self.zero_position)

    def getUpdatedPostion(self, pitch, roll, yaw):
        # If we have a zero position set, return values relative to that position
        if self.zero_position is not None:
            # Calculate the relative angles
            rel_pitch = pitch - self.zero_position[0]
            rel_roll = roll - self.zero_position[1]
            if yaw is not None: 
                rel_yaw = yaw - self.zero_position[2]
            else:
                rel_yaw = None  
            
            # Normalize angles to -180 to +180 range
            rel_pitch = (rel_pitch + 180) % 360 - 180
            rel_roll = (rel_roll + 180) % 360 - 180
            if rel_yaw is not None:
                rel_yaw = (rel_yaw + 180) % 360 - 180
            
            return [rel_pitch, rel_roll, rel_yaw]
        else:
            return [pitch, roll, yaw]

# vi: modeline tabstop=8 expandtab shiftwidth=4 softtabstop=4 syntax=python
