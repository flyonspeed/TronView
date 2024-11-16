#!/usr/bin/env python

#################################################
# Module: object3d
# Topher 2024

from lib.modules._module import Module
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
        self.font_size = 20  # Reduced font size for better fit

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

        self.buttonsInit()
        self.buttonAdd(id="zero_position", 
                       text="Zero", 
                       function=self.zeroPosition, 
                       pos="BotR")

    # called every redraw for the mod
    def draw(self, aircraft, smartdisplay, pos=(None, None)):
        # Clear the surface
        self.surface.fill((0, 0, 0, 0))

        # Calculate the cube size based on the smaller dimension of the surface
        cube_size = min(self.width, self.height) * 1  # Use % of the smaller dimension

        # Set the center of the cube to the center of the surface
        x = self.width // 2
        y = self.height // 2

        # Define cube vertices with the same order as before
        vertices = [
            [-1, -1, -1], # front left bottom (0)
            [1, -1, -1],  # front right bottom (1)
            [1, 1, -1],   # front right top (2)
            [-1, 1, -1],  # front left top (3)
            [-1, -1, 1],  # back left bottom (4)
            [1, -1, 1],   # back right bottom (5)
            [1, 1, 1],    # back right top (6)
            [-1, 1, 1]    # back left top (7)
        ]

        # Define faces (vertices that make up each face)
        faces = [
            ([0, 1, 2, 3], "FRONT", (255, 0, 0, 64)),    # Front face (red)
            ([5, 4, 7, 6], "BACK", (0, 255, 0, 64)),     # Back face (green)
            ([4, 0, 3, 7], "LEFT", (0, 0, 255, 64)),     # Left face (blue)
            ([1, 5, 6, 2], "RIGHT", (255, 255, 0, 64)),  # Right face (yellow)
            ([3, 2, 6, 7], "TOP", (255, 0, 255, 64)),    # Top face (magenta)
            ([0, 1, 5, 4], "BOTTOM", (0, 255, 255, 64))  # Bottom face (cyan)
        ]

        # if imu is available and the self.source_imu_index is not larger than the number of imus.
        if aircraft.imus and self.source_imu_index < len(aircraft.imus):
            source_imu = aircraft.imus[self.source_imu_index]
            #new_position = self.getUpdatedPostion(source_imu.pitch, source_imu.roll, source_imu.yaw)
            pitch = source_imu.pitch
            roll = source_imu.roll
            yaw = source_imu.yaw
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

        # Calculate center points and draw faces
        def get_face_center(face_vertices):
            x = sum(rotated_vertices[v][0] for v in face_vertices) / 4
            y = sum(rotated_vertices[v][1] for v in face_vertices) / 4
            # Calculate average z-coordinate for depth sorting
            z = sum(rotate_z(rotate_y(rotate_x(vertices[v], pitch), yaw), roll)[2] for v in face_vertices) / 4
            return (x, y, z)

        # Sort faces by z-coordinate (painter's algorithm)
        faces_with_depth = []
        for face_vertices, label, color in faces:
            center = get_face_center(face_vertices)
            faces_with_depth.append((face_vertices, label, color, center[2]))
        
        # Sort faces from back to front
        faces_with_depth.sort(key=lambda x: x[3], reverse=True)

        # Create text surfaces once
        text_surfaces = {}
        for _, label, color in faces:
            # Create a surface for the text with a transparent background
            text_surface = pygame.Surface((100, 30), pygame.SRCALPHA)
            rendered_text = self.font.render(label, True, self.MainColor)
            # Center the text on its surface
            text_rect = rendered_text.get_rect(center=(50, 15))
            text_surface.blit(rendered_text, text_rect)
            text_surfaces[label] = text_surface

        # Draw the sorted faces
        for face_vertices, label, color, _ in faces_with_depth:
            points = [rotated_vertices[v] for v in face_vertices]
            
            # Draw the face surface
            pygame.draw.polygon(self.surface, color, points)
            pygame.draw.polygon(self.surface, self.MainColor, points, 2)  # Draw edges

            # Calculate face center and normal vector
            center_x = sum(p[0] for p in points) / 4
            center_y = sum(p[1] for p in points) / 4

            # Get the text surface for this face
            text_surface = text_surfaces[label]
            text_rect = text_surface.get_rect()
            
            # Calculate text position
            text_rect.center = (int(center_x), int(center_y))

            # Calculate scale factor based on face size
            face_width = max(p[0] for p in points) - min(p[0] for p in points)
            scale_factor = face_width / text_rect.width * 0.5  # Use 50% of face width
            
            if scale_factor > 0:
                # Scale text surface
                scaled_size = (int(text_rect.width * scale_factor), 
                             int(text_rect.height * scale_factor))
                if scaled_size[0] > 0 and scaled_size[1] > 0:  # Ensure valid size
                    scaled_text = pygame.transform.scale(text_surface, scaled_size)
                    scaled_rect = scaled_text.get_rect(center=(center_x, center_y))
                    
                    # Rotate text to match face orientation
                    # Calculate rotation angle based on face normal
                    dx = points[1][0] - points[0][0]
                    dy = points[1][1] - points[0][1]
                    angle = math.degrees(math.atan2(dy, dx))
                    
                    # Rotate text surface
                    rotated_text = pygame.transform.rotate(scaled_text, -angle)
                    rotated_rect = rotated_text.get_rect(center=(center_x, center_y))
                    
                    # Draw the rotated and scaled text
                    self.surface.blit(rotated_text, rotated_rect)

        # draw buttons
        self.buttonsDraw(aircraft, smartdisplay, pos)

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
        shared.Dataship.imus[self.source_imu_index].home(delete=True) 

    def processClick(self, aircraft: Dataship, mx, my):
        if self.buttonsCheckClick(aircraft, mx, my):
            return
    
    def zeroPosition(self, aircraft: Dataship, button):
        aircraft.imus[self.source_imu_index].home()
        
        # # When clicked, set the current position as the new zero reference point
        # if aircraft.imus and self.source_imu_index < len(aircraft.imus):
        #     source_imu = aircraft.imus[self.source_imu_index]
        #     self.zero_position = [
        #         source_imu.pitch,
        #         source_imu.roll,
        #         source_imu.yaw
        #     ]
        #     print("New zero position set:", self.zero_position)

    # def getUpdatedPostion(self, pitch, roll, yaw):
    #     if pitch is None or roll is None:
    #         return [None, None, None]

    #     # If we have a zero position set, return values relative to that position
    #     if self.zero_position is not None:
    #         # Calculate the relative angles
    #         rel_pitch = pitch - self.zero_position[0]
    #         rel_roll = roll - self.zero_position[1]
    #         if yaw is not None: 
    #             rel_yaw = yaw - self.zero_position[2]
    #         else:
    #             rel_yaw = None  
            
    #         # Normalize angles to -180 to +180 range
    #         rel_pitch = (rel_pitch + 180) % 360 - 180
    #         rel_roll = (rel_roll + 180) % 360 - 180
    #         if rel_yaw is not None:
    #             rel_yaw = (rel_yaw + 180) % 360 - 180

            
    #         return [rel_pitch, rel_roll, rel_yaw]
    #     else:
    #         return [pitch, roll, yaw]

# vi: modeline tabstop=8 expandtab shiftwidth=4 softtabstop=4 syntax=python
