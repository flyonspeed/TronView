from kivy.uix.widget import Widget
from kivy.graphics import (
    Mesh, Color, RenderContext, 
    PushMatrix, PopMatrix, Rotate,
    Callback, Translate
)
from kivy.graphics.transformation import Matrix
from kivy.graphics.opengl import glEnable, glDisable, GL_DEPTH_TEST
from kivy.clock import Clock
import math
import numpy as np

class Horizon3D(Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        # Initialize the render context with a vertex shader that supports 3D
        self.canvas = RenderContext(compute_normal_mat=True)
        
        # Set custom shader
        vertex_shader = self.get_vertex_shader()
        fragment_shader = self.get_fragment_shader()
        
        try:
            self.canvas.shader.fs = fragment_shader
            print("Fragment shader compiled successfully")
        except Exception as e:
            print(f"Error compiling fragment shader: {e}")
            
        try:
            self.canvas.shader.vs = vertex_shader
            print("Vertex shader compiled successfully")
        except Exception as e:
            print(f"Error compiling vertex shader: {e}")
        
        # Initial orientation values
        self.pitch = 0
        self.roll = 0
        self.yaw = 0
        
        # Camera settings
        self.camera_pos = [0, 10, -20]  # Position camera above and behind the grid
        self.camera_rotation = [30, 0, 0]  # Initial camera rotation (pitch, yaw, roll)
        self.is_mouse_dragging = False
        self.last_mouse_pos = None
        self.camera_distance = 20
        self.camera_sensitivity = 0.3
        self.min_zoom = 5  # Minimum zoom distance
        self.max_zoom = 50  # Maximum zoom distance
        self.zoom_speed = 1  # Zoom speed multiplier
        
        # Set up the mesh and initialize the scene
        self.setup_gl()
        self.setup_scene()
        
        # Start the update loop
        Clock.schedule_interval(self.update, 1.0 / 60.0)
        
        # Register event handlers
        self.register_event_type('on_touch_down')
        self.register_event_type('on_touch_move')
        self.register_event_type('on_touch_up')

    def get_vertex_shader(self):
        return '''
#version 120

attribute vec3 v_pos;
attribute vec4 v_color;
attribute vec2 tex_coord0;

uniform mat4 modelview_mat;
uniform mat4 projection_mat;

varying vec4 frag_color;
varying vec3 world_pos;

void main() {
    frag_color = v_color;
    vec4 pos = modelview_mat * vec4(v_pos, 1.0);
    world_pos = pos.xyz;
    gl_Position = projection_mat * pos;
}
'''

    def get_fragment_shader(self):
        return '''
#version 120

varying vec4 frag_color;
varying vec3 world_pos;

void main() {
    vec3 light_pos = vec3(0.0, 10.0, 0.0);
    vec3 light_dir = normalize(light_pos - world_pos);
    
    // Simple diffuse lighting
    float diff = max(dot(vec3(0.0, 1.0, 0.0), light_dir), 0.0);
    vec3 diffuse = diff * vec3(1.0);
    vec3 ambient = vec3(0.3);
    
    gl_FragColor = vec4((ambient + diffuse) * frag_color.rgb, frag_color.a);
}
'''

    def setup_gl(self, *args):
        """Set up OpenGL settings"""
        glEnable(GL_DEPTH_TEST)

    def reset_gl(self, *args):
        """Reset OpenGL state"""
        glDisable(GL_DEPTH_TEST)

    def setup_scene(self):
        """Create the 3D scene geometry"""
        with self.canvas:
            self.cb = Callback(self.setup_gl)
            PushMatrix()
            
            # Create lookAt matrix for camera
            look_at = Matrix().look_at(
                *self.camera_pos,  # Eye position
                0, 0, 0,          # Target position (origin)
                0, 1, 0           # Up vector
            )
            self.modelview_mat = look_at
            
            # Create the main rotation matrices
            self.pitch_rotation = Rotate(0, 1, 0, 0)  # pitch around x-axis
            self.roll_rotation = Rotate(0, 0, 1, 0)   # roll around y-axis
            self.yaw_rotation = Rotate(0, 0, 0, 1)    # yaw around z-axis
            
            # Create sphere grid
            Color(0.5, 0.5, 1, 1)  # Set color to light blue
            self.create_sphere()
            
            PopMatrix()
            self.cb = Callback(self.reset_gl)

    def create_sphere(self):
        """Create a sphere using latitude and longitude lines"""
        vertices = []
        indices = []
        vertex_count = 0
        radius = 10.0
        
        # Create latitude lines
        lat_steps = 20
        lon_steps = 40
        
        # Create longitude lines
        for lon in range(lon_steps):
            phi = (lon / lon_steps) * 2 * math.pi
            for lat in range(lat_steps + 1):
                theta = (lat / lat_steps) * math.pi
                
                # Calculate point on sphere
                x = radius * math.sin(theta) * math.cos(phi)
                y = radius * math.cos(theta)
                z = radius * math.sin(theta) * math.sin(phi)
                
                vertices.extend([
                    x, y, z,           # position
                    0.5, 0.5, 1, 1,    # color
                    phi/(2*math.pi), theta/math.pi  # texture coordinates
                ])
                
                if lat < lat_steps:
                    indices.extend([vertex_count, vertex_count + 1])
                vertex_count += 1
        
        # Create latitude lines
        for lat in range(1, lat_steps):
            theta = (lat / lat_steps) * math.pi
            for lon in range(lon_steps + 1):
                phi = (lon / lon_steps) * 2 * math.pi
                
                # Calculate point on sphere
                x = radius * math.sin(theta) * math.cos(phi)
                y = radius * math.cos(theta)
                z = radius * math.sin(theta) * math.sin(phi)
                
                vertices.extend([
                    x, y, z,           # position
                    0.5, 0.5, 1, 1,    # color
                    phi/(2*math.pi), theta/math.pi  # texture coordinates
                ])
                
                if lon < lon_steps:
                    indices.extend([vertex_count, vertex_count + 1])
                vertex_count += 1
        
        # Create and draw the mesh
        self.sphere_mesh = Mesh(
            vertices=vertices,
            indices=indices,
            mode='lines',
            fmt=[
                ('v_pos', 3, 'float'),      # 3D position
                ('v_color', 4, 'float'),    # RGBA color
                ('tex_coord0', 2, 'float')  # Texture coordinates
            ]
        )
        
        # Add the mesh to the canvas
        self.canvas.add(self.sphere_mesh)

    def update(self, dt):
        """Update the scene"""
        # Update rotation matrices based on current orientation
        self.pitch_rotation.angle = self.pitch
        self.roll_rotation.angle = self.roll
        self.yaw_rotation.angle = self.yaw
        
        # Update camera position based on spherical coordinates
        pitch_rad = math.radians(self.camera_rotation[0])
        yaw_rad = math.radians(self.camera_rotation[1])
        
        # Calculate new camera position
        self.camera_pos[0] = self.camera_distance * math.cos(pitch_rad) * math.sin(yaw_rad)
        self.camera_pos[1] = self.camera_distance * math.sin(pitch_rad)
        self.camera_pos[2] = self.camera_distance * math.cos(pitch_rad) * math.cos(yaw_rad)
        
        # Update modelview matrix for camera position
        look_at = Matrix().look_at(
            *self.camera_pos,  # Eye position
            0, 0, 0,          # Target position (origin)
            0, 1, 0           # Up vector
        )
        self.canvas['modelview_mat'] = look_at
        
        # Request redraw
        self.canvas.ask_update()

    def on_touch_down(self, touch):
        if touch.button == 'right':
            self.is_mouse_dragging = True
            self.last_mouse_pos = touch.pos
            return True
        elif 'button' in touch.profile:
            if touch.button == 'scrollup':
                # Zoom in
                self.camera_distance = max(self.min_zoom, 
                    self.camera_distance - self.zoom_speed)
                return True
            elif touch.button == 'scrolldown':
                # Zoom out
                self.camera_distance = min(self.max_zoom, 
                    self.camera_distance + self.zoom_speed)
                return True
        return super().on_touch_down(touch)

    def on_touch_move(self, touch):
        if self.is_mouse_dragging and self.last_mouse_pos:
            # Calculate mouse movement
            dx = touch.pos[0] - self.last_mouse_pos[0]
            dy = touch.pos[1] - self.last_mouse_pos[1]
            
            # Update camera rotation
            self.camera_rotation[1] += dx * self.camera_sensitivity  # Yaw
            self.camera_rotation[0] += dy * self.camera_sensitivity  # Pitch
            
            # Clamp pitch to prevent camera flipping
            self.camera_rotation[0] = max(-89, min(89, self.camera_rotation[0]))
            
            # Update camera position based on spherical coordinates
            pitch_rad = math.radians(self.camera_rotation[0])
            yaw_rad = math.radians(self.camera_rotation[1])
            
            # Calculate new camera position
            self.camera_pos[0] = self.camera_distance * math.cos(pitch_rad) * math.sin(yaw_rad)
            self.camera_pos[1] = self.camera_distance * math.sin(pitch_rad)
            self.camera_pos[2] = self.camera_distance * math.cos(pitch_rad) * math.cos(yaw_rad)
            
            self.last_mouse_pos = touch.pos
            return True
        return super().on_touch_move(touch)

    def on_touch_up(self, touch):
        if touch.button == 'right':
            self.is_mouse_dragging = False
            return True
        return super().on_touch_up(touch)

    def set_orientation(self, pitch, roll, yaw):
        """Set the orientation of the horizon"""
        self.pitch = pitch
        self.roll = roll
        self.yaw = yaw
