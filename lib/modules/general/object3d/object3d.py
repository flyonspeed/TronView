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

        # Add smoothing variables
        self.smoothing_factor = 0.1  # Default smoothing (0 = no smoothing, 1 = max smoothing)
        self.current_pitch = 0
        self.current_roll = 0 
        self.current_yaw = 0

        self.source_imu_index_name = ""  # name of the primary imu.
        self.source_imu_index = 0  # index of the primary imu.

        self.source_imu_index2_name = ""  # name of the secondary imu. (optional)
        self.source_imu_index2 = None  # index of the secondary imu. (optional)

        self.show_xyz = False

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
        self.imu_ids2 = []

        # update self.source_imu_index_name with the correct name using the index.
        # this can happen because we load a screen that used a imu id that is not in the list or moved
        # we only care about the index.
        for imu_index, imu in shared.Dataship.imus.items():
            if self.source_imu_index == imu_index:
                self.source_imu_index_name = imu.id

        self.draw_arrows = True
        self.zero_position = None

        self.buttonsInit()
        self.buttonAdd(id="zero_position", 
                       text="Zero", 
                       function=self.zeroPosition, 
                       pos="BotR")
        
        # Define cube vertices with the same order as before
        self.vertices = [
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
        self.faces = [
            ([0, 1, 2, 3], "FRONT", (255, 0, 0, 64)),    # Front face (red)
            ([5, 4, 7, 6], "BACK", (0, 255, 0, 64)),     # Back face (green)
            ([4, 0, 3, 7], "LEFT", (0, 0, 255, 64)),     # Left face (blue)
            ([1, 5, 6, 2], "RIGHT", (255, 255, 0, 64)),  # Right face (yellow)
            ([3, 2, 6, 7], "BOTTOM", (255, 0, 255, 64)),    # Bottom face (magenta)
            ([0, 1, 5, 4], "TOP", (0, 255, 255, 64))  # Top face (cyan)
        ]


    # called every redraw for the mod
    def draw(self, aircraft, smartdisplay, pos=(None, None)):
        # Clear the surface
        self.surface.fill((0, 0, 0, 0))

        # Calculate the cube size based on the smaller dimension of the surface
        cube_size = min(self.width, self.height) * 1  # Use % of the smaller dimension

        # Set the center of the cube to the center of the surface
        x = self.width // 2
        y = self.height // 2

        # if imu is available and the self.source_imu_index is not larger than the number of imus.
        if aircraft.imus and self.source_imu_index < len(aircraft.imus):
            if self.source_imu_index2 is not None:
                source_imu = self.calculateCameraPosition()
            else:
                source_imu = aircraft.imus[self.source_imu_index]

            # Apply smoothing to the orientation values
            if source_imu.pitch is not None:
                target_pitch = source_imu.pitch
                self.current_pitch += (target_pitch - self.current_pitch) * (1 - self.smoothing_factor)
                pitch = self.current_pitch
            else:
                pitch = None

            if source_imu.roll is not None:
                target_roll = source_imu.roll
                self.current_roll += (target_roll - self.current_roll) * (1 - self.smoothing_factor)
                roll = self.current_roll
            else:
                roll = None

            if source_imu.yaw is not None:
                target_yaw = source_imu.yaw
                # Handle yaw wraparound at 360/0 degrees
                if abs(target_yaw - self.current_yaw) > 180:
                    if target_yaw > self.current_yaw:
                        target_yaw -= 360
                    else:
                        target_yaw += 360
                self.current_yaw += (target_yaw - self.current_yaw) * (1 - self.smoothing_factor)
                # Normalize yaw back to -180 to 180 range
                yaw = self.current_yaw
                if yaw > 180:
                    yaw -= 360
                elif yaw < -180:
                    yaw += 360
            else:
                yaw = None
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
        for v in self.vertices:
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
            z = sum(rotate_z(rotate_y(rotate_x(self.vertices[v], pitch), yaw), roll)[2] for v in face_vertices) / 4
            return (x, y, z)

        # Sort faces by z-coordinate (painter's algorithm)
        faces_with_depth = []
        for face_vertices, label, color in self.faces:
            center = get_face_center(face_vertices)
            faces_with_depth.append((face_vertices, label, color, center[2]))
        
        # Sort faces from back to front
        faces_with_depth.sort(key=lambda x: x[3], reverse=True)

        # Create text surfaces once
        text_surfaces = {}
        for _, label, color in self.faces:
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
        if self.source_imu_index2 is None:
            self.buttonsDraw(aircraft, smartdisplay, pos)
        
        if self.show_xyz:
            # create text for x, y, z.
            if source_imu.pitch is not None:
                x = round(source_imu.pitch,1)
            else:
                x = "---"
            if source_imu.roll is not None:
                y = round(source_imu.roll,1)
            else:
                    y = "---"
            if source_imu.yaw is not None:
                z = round(source_imu.yaw,1)
            else:
                z = "---"
            text = self.font.render("Pitch: "+str(x)+"\nRoll: "+str(y)+"\nYaw: "+str(z), True, self.MainColor)
            text_rect = text.get_rect(topleft=(10, 10)) # draw in top left corner.
            self.surface.blit(text, text_rect)

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
            for imu_index, imu in imu_list.items():
                #print(f"IMU {imu_id}:", imu.id)
                self.imu_ids.append(str(imu.id))
        if len(self.source_imu_index_name) == 0: # if no name.
            self.source_imu_index_name = self.imu_ids[self.source_imu_index]  # select first one.

        # duplicate the list for the secondary imu.
        self.imu_ids2 = self.imu_ids.copy()
        self.imu_ids2.append("NONE")

        options = {
            "source_imu_index_name": {
                "type": "dropdown",
                "label": "Primary IMU",
                "description": "IMU to use for the 3D object.",
                "options": self.imu_ids,
                "post_change_function": "changeSource1IMU"
            },
            "source_imu_index": {
                "type": "int",
                "hidden": True,  # hide from the UI, but save to json screen file.
                "default": 0
            },
            "source_imu_index2_name": {
                "type": "dropdown",
                "label": "Secondary IMU (Camera)",
                "description": "If selected then 2nd IMU will be position camera. As if it was mounted on the Primary IMU.",
                "options": self.imu_ids2,
                "post_change_function": "changeSource2IMU"
            },
            "source_imu_index2": {
                "type": "int",
                "hidden": True,  # hide from the UI, but save to json screen file.
                "default": 0
            },
            "MainColor": {
                "type": "color",
                "default": (255,255,255),
                "label": "Main Color",
                "description": "Color of the main line.",
            },
            "show_xyz": {
                "type": "bool",
                "default": False,
                "label": "Show Coordinates",
                "description": "Show the XYZ axes.",
            },
            "smoothing_factor": {
                "type": "float",
                "default": 0.1,
                "min": 0.0,
                "max": 0.99,
                "label": "Smoothing Factor",
                "description": "Amount of smoothing to apply to orientation changes (0 = none, 0.99 = max)",
            }
        }

        # check if self.imu_ids[self.source_imu_index].input has a method setPostion.
        if self.source_imu_index < len(shared.Dataship.imus) and shared.Dataship.imus[self.source_imu_index].input is not None:
            if shared.Dataship.imus[self.source_imu_index].input is not None:
                if hasattr(shared.Dataship.imus[self.source_imu_index].input, "setPostion"):
                    # check if self.test_pitch exists.
                    if not hasattr(self, "test_pitch"):
                        self.test_pitch = 0
                    if not hasattr(self, "test_roll"):
                        self.test_roll = 0
                    if not hasattr(self, "test_yaw"):
                        self.test_yaw = 0
                    if not hasattr(self, "auto_rotate_pitch"):
                        self.auto_rotate_pitch = 0
                    if not hasattr(self, "auto_rotate_roll"):
                        self.auto_rotate_roll = 0
                    if not hasattr(self, "auto_rotate_yaw"):
                        self.auto_rotate_yaw = 0

                    options["test_pitch"] = {
                        "type": "int",
                        "default": 0,
                        "min": -180,
                        "max": 180,
                        "label": "Test Pitch",
                        "description": "Test pitch value.",
                        "post_change_function": "setTestPostion"
                    }
                    options["test_roll"] = {
                        "type": "int",
                        "default": 0,
                        "min": -180,
                        "max": 180,
                        "label": "Test Roll",
                        "description": "Test roll value.",
                        "post_change_function": "setTestPostion"
                    }
                    options["test_yaw"] = {
                        "type": "int",
                        "default": 0,
                        "min": -180,
                        "max": 180,
                        "label": "Test Yaw",
                        "description": "Test yaw value.",
                        "post_change_function": "setTestPostion"
                    }
                    options["auto_rotate_pitch"] = {
                        "type": "int",
                        "default": 0,
                        "min": -5,
                        "max": 5,
                        "label": "Auto Rotate Pitch",
                        "description": "Auto rotate pitch value.",
                        "post_change_function": "setTestAutoRotate"
                    }
                    options["auto_rotate_roll"] = {
                        "type": "int",
                        "default": 0,
                        "min": -5,
                        "max": 5,
                        "label": "Auto Rotate Roll",
                        "description": "Auto rotate roll value.",
                        "post_change_function": "setTestAutoRotate"
                    }
                    options["auto_rotate_yaw"] = {
                        "type": "int",
                        "default": 0,
                        "min": -5,
                        "max": 5,
                        "label": "Auto Rotate Yaw",
                        "description": "Auto rotate yaw value.",
                        "post_change_function": "setTestAutoRotate"
                    }
        
        # Add existing options
        options.update(super().get_module_options())
        return options

    def setTestPostion(self):
        shared.Dataship.imus[self.source_imu_index].input.setPostion(self.test_pitch, self.test_roll, self.test_yaw)
    
    def setTestAutoRotate(self):
        shared.Dataship.imus[self.source_imu_index].input.setAutoRotate(self.auto_rotate_pitch, self.auto_rotate_roll, self.auto_rotate_yaw)

    def changeSource1IMU(self):
        '''
        Change the primary IMU.
        '''
        # source_imu_index_name got changed. find the index of the imu id in the imu list.
        self.source_imu_index = self.imu_ids.index(self.source_imu_index_name)
        #print("source_imu_index==", self.source_imu_index)
        shared.Dataship.imus[self.source_imu_index].home(delete=True) 

    def changeSource2IMU(self):
        if self.source_imu_index2_name == "NONE":
            self.source_imu_index2 = None
        else:
            self.source_imu_index2 = self.imu_ids2.index(self.source_imu_index2_name)
            shared.Dataship.imus[self.source_imu_index2].home(delete=True) 

    def processClick(self, aircraft: Dataship, mx, my):
        if self.buttonsCheckClick(aircraft, mx, my):
            return
    
    def zeroPosition(self, aircraft: Dataship, button):
        '''
        Set the zero position of the primary IMU.
        '''
        aircraft.imus[self.source_imu_index].home()


    def calculateCameraPosition(self):
        '''
        Calculate the camera position based on the primary and secondary IMU.
        The virtual IMU represents where the camera IMU is looking relative to the base IMU's orientation.
        For example:
        - If base IMU is at 100° yaw and camera IMU is at 110° yaw, virtual IMU will be at 10° yaw
        - If base IMU is at 15° pitch and camera IMU is at -15° pitch, virtual IMU will be at 0° pitch
        Returns a virtual IMU object with the relative orientation between the two IMUs.
        '''
        if self.source_imu_index2 >= shared.Dataship.imus.__len__():  # secondary imu not found.
            # create a virtual imu with all None values.
            virtual_imu = type('VirtualIMU', (), {})()
            virtual_imu.pitch = None
            virtual_imu.roll = None
            virtual_imu.yaw = None
            return virtual_imu

        # Get references to both IMUs from shared dataship
        imu_base = shared.Dataship.imus[self.source_imu_index]
        imu_camera = shared.Dataship.imus[self.source_imu_index2]

        # Create a virtual IMU that represents the relative orientation
        virtual_imu = type('VirtualIMU', (), {})()

        # If either IMU has None values, return None for all orientations
        if imu_camera.pitch is None or imu_base.pitch is None:
            virtual_imu.pitch = None
            virtual_imu.roll = None
            virtual_imu.yaw = None
            return virtual_imu

        # Calculate relative angles by subtracting base IMU angles from camera IMU angles
        virtual_imu.pitch = imu_camera.pitch - imu_base.pitch
        virtual_imu.roll = imu_camera.roll - imu_base.roll
        
        # Special handling for yaw to handle wraparound at 360/0 degrees
        if imu_camera.yaw is not None and imu_base.yaw is not None:
            # Calculate the relative yaw angle
            relative_yaw = imu_camera.yaw - imu_base.yaw
            
            # Normalize to -180 to 180 range
            if relative_yaw > 180:
                relative_yaw -= 360
            elif relative_yaw < -180:
                relative_yaw += 360
                
            virtual_imu.yaw = relative_yaw
        else:
            virtual_imu.yaw = None

        return virtual_imu




# vi: modeline tabstop=8 expandtab shiftwidth=4 softtabstop=4 syntax=python
