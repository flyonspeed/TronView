#!/usr/bin/env python

from lib.modules._module import Module
from lib import hud_graphics
from lib import hud_utils
from lib import smartdisplay
import pygame
import math
import moderngl
import numpy as np
from lib.common import shared
from lib.common.dataship.dataship import Dataship

class object3d_gl(Module):
    def __init__(self):
        Module.__init__(self)
        self.name = "object 3D"
        self.MainColor = (1.0, 1.0, 1.0)  # Changed to normalized colors for OpenGL
        self.font_size = 20
        self.source_imu_index_name = ""
        self.source_imu_index = 0
        self.ctx = None
        self.prog = None
        self.vbo = None
        self.vao = None

    def initMod(self, pygamescreen, width=None, height=None):
        if width is None:
            width = 500
        if height is None:
            height = 500
        Module.initMod(self, pygamescreen, width, height)
        print(f"Init Mod: {self.name} {self.width}x{self.height}")

        # Initialize ModernGL context
        self.ctx = moderngl.create_context()
        
        # Shader programs
        vertex_shader = '''
            #version 330
            in vec3 in_position;
            in vec3 in_color;
            uniform mat4 mvp;
            out vec3 color;
            void main() {
                gl_Position = mvp * vec4(in_position, 1.0);
                color = in_color;
            }
        '''

        fragment_shader = '''
            #version 330
            in vec3 color;
            out vec4 fragColor;
            void main() {
                fragColor = vec4(color, 0.6);
            }
        '''

        self.prog = self.ctx.program(
            vertex_shader=vertex_shader,
            fragment_shader=fragment_shader,
        )

        # Cube vertices and colors
        vertices = np.array([
            # Front face (red)
            -0.5, -0.5, -0.5,  1.0, 0.0, 0.0,
             0.5, -0.5, -0.5,  1.0, 0.0, 0.0,
             0.5,  0.5, -0.5,  1.0, 0.0, 0.0,
            -0.5,  0.5, -0.5,  1.0, 0.0, 0.0,
            # Back face (green)
            -0.5, -0.5,  0.5,  0.0, 1.0, 0.0,
             0.5, -0.5,  0.5,  0.0, 1.0, 0.0,
             0.5,  0.5,  0.5,  0.0, 1.0, 0.0,
            -0.5,  0.5,  0.5,  0.0, 1.0, 0.0,
        ], dtype='f4')

        # Indices for drawing the cube
        indices = np.array([
            0, 1, 2, 2, 3, 0,  # Front
            4, 5, 6, 6, 7, 4,  # Back
            0, 4, 7, 7, 3, 0,  # Left
            1, 5, 6, 6, 2, 1,  # Right
            3, 2, 6, 6, 7, 3,  # Top
            0, 1, 5, 5, 4, 0,  # Bottom
        ], dtype='i4')

        self.vbo = self.ctx.buffer(vertices.tobytes())
        self.ibo = self.ctx.buffer(indices.tobytes())
        
        self.vao = self.ctx.vertex_array(
            self.prog,
            [
                (self.vbo, '3f 3f', 'in_position', 'in_color'),
            ],
            self.ibo
        )

        self.font = pygame.font.SysFont(None, self.font_size)
        self.surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        self.imu_ids = []
        self.draw_arrows = True
        self.zero_position = None
        
        # Create framebuffer
        self.fbo = self.ctx.framebuffer(
            color_attachments=[self.ctx.texture((self.width, self.height), 4)]
        )

    def draw(self, aircraft, smartdisplay, pos=(None, None)):
        if not self.ctx or not self.prog:
            return

        # Get IMU data
        if aircraft.imus and self.source_imu_index < len(aircraft.imus):
            source_imu = aircraft.imus[self.source_imu_index]
            new_position = self.getUpdatedPostion(source_imu.pitch, source_imu.roll, source_imu.yaw)
            pitch, roll, yaw = new_position
        else:
            roll = pitch = yaw = None

        if roll is None or pitch is None:
            # Handle error case
            self.surface.fill((0, 0, 0, 0))
            pygame.draw.line(self.surface, (255,0,0), (0,0), (self.width,self.height), 4)
            pygame.draw.line(self.surface, (255,0,0), (self.width,0), (0,self.height), 4)
            text = self.font.render("IMU-"+str(self.source_imu_index+1) +" ERROR", True, (255,0,0))
            text_rect = text.get_rect(center=(self.width//2, self.height//2-20))
            self.surface.blit(text, text_rect)
            smartdisplay.pygamescreen.blit(self.surface, pos)
            return

        # Convert angles to radians
        pitch = math.radians(pitch)
        roll = math.radians(roll)
        yaw = math.radians(yaw if yaw is not None else 0)

        # Create model-view-projection matrix
        model = self.create_model_matrix(pitch, roll, yaw)
        view = self.create_view_matrix()
        projection = self.create_projection_matrix()
        mvp = projection @ view @ model

        # Render to framebuffer
        self.fbo.use()
        self.ctx.clear(0.0, 0.0, 0.0, 0.0)
        self.ctx.enable(moderngl.BLEND)
        self.prog['mvp'].write(mvp.astype('f4').tobytes())
        self.vao.render()

        # Get the rendered image
        data = self.fbo.read(components=4)
        rendered_surface = pygame.image.frombuffer(data, (self.width, self.height), 'RGBA')
        
        # Blit to the target surface
        smartdisplay.pygamescreen.blit(rendered_surface, pos if pos != (None, None) else (0, 0))

    def create_model_matrix(self, pitch, roll, yaw):
        # Create rotation matrices
        rx = np.array([
            [1, 0, 0, 0],
            [0, np.cos(pitch), -np.sin(pitch), 0],
            [0, np.sin(pitch), np.cos(pitch), 0],
            [0, 0, 0, 1]
        ])
        
        ry = np.array([
            [np.cos(yaw), 0, np.sin(yaw), 0],
            [0, 1, 0, 0],
            [-np.sin(yaw), 0, np.cos(yaw), 0],
            [0, 0, 0, 1]
        ])
        
        rz = np.array([
            [np.cos(roll), -np.sin(roll), 0, 0],
            [np.sin(roll), np.cos(roll), 0, 0],
            [0, 0, 1, 0],
            [0, 0, 0, 1]
        ])
        
        return rz @ ry @ rx

    def create_view_matrix(self):
        return np.array([
            [1, 0, 0, 0],
            [0, 1, 0, 0],
            [0, 0, -1, -3],  # Move camera back 3 units
            [0, 0, 0, 1]
        ])

    def create_projection_matrix(self):
        fov = 60.0
        aspect = self.width / self.height
        near = 0.1
        far = 100.0
        
        f = 1.0 / math.tan(math.radians(fov) / 2.0)
        return np.array([
            [f/aspect, 0, 0, 0],
            [0, f, 0, 0],
            [0, 0, (far+near)/(near-far), (2*far*near)/(near-far)],
            [0, 0, -1, 0]
        ])

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
        self.zero_position = None

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
        if pitch is None or roll is None:
            return [None, None, None]

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
