from kivy.app import App
from kivy.uix.widget import Widget
from kivy.core.window import Window
from kivy.clock import Clock
from kivy.graphics import *
from kivy.graphics.transformation import Matrix
from kivy.graphics.opengl import *
from kivy.graphics import Mesh, RenderContext
from kivy.uix.label import Label
import math
import numpy as np

# Vertex shader - handles 3D transformations
VERTEX_SHADER = '''
#ifdef GL_ES
    precision highp float;
#endif

attribute vec3 v_pos;
uniform mat4 modelview_mat;
uniform mat4 projection_mat;
uniform float scale;

void main(void) {
    vec4 pos = modelview_mat * vec4(v_pos * scale, 1.0);
    gl_Position = projection_mat * pos;
}
'''

# Fragment shader - handles coloring
FRAGMENT_SHADER = '''
#ifdef GL_ES
    precision highp float;
#endif

uniform vec4 color;

void main(void) {
    gl_FragColor = vec4(1.0, 0.0, 0.0, 1.0);  // Red color
}
'''

class Sphere3D(Widget):
    def __init__(self, **kwargs):
        super(Sphere3D, self).__init__(**kwargs)
        self.rotation_x = 0
        self.rotation_y = 0
        self.scale = 2.8
        self.last_x = 0
        self.last_y = 0
        self.mouse_down = False
        self.right_mouse_down = False
        
        # Camera parameters
        self.camera_x = 0
        self.camera_y = 0
        self.camera_z = 200
        self.target_x = 0
        self.target_y = 0
        self.target_z = 0

        # Create info label
        self.info_label = Label(pos=(10, 10), size_hint=(None, None))
        self.add_widget(self.info_label)

        # Set up shader
        with self.canvas:
            self.canvas = RenderContext()
            self.canvas.shader.fs = FRAGMENT_SHADER
            self.canvas.shader.vs = VERTEX_SHADER

        # Make widget receive all input events
        self._keyboard = Window.request_keyboard(self._on_keyboard_closed, self)
        self._keyboard.bind(on_key_down=self._on_key_down)
        
        # Create points for the sphere
        self.create_sphere_points()
        
        # Schedule updates
        Clock.schedule_interval(self.update, 1.0 / 60.0)

    def create_sphere_points(self, radius=100, segments=20):
        vertices = []
        indices = []
        vertex_count = 0

        # Create vertices
        for i in range(segments + 1):
            lat = math.pi * (-0.5 + float(i) / segments)
            for j in range(segments + 1):
                lon = 2 * math.pi * float(j) / segments
                x = math.cos(lat) * math.cos(lon)
                y = math.sin(lat)
                z = math.cos(lat) * math.sin(lon)
                vertices.extend([x * radius, y * radius, z * radius])

                # Create indices for lines
                if i < segments and j < segments:
                    # Horizontal lines
                    indices.extend([vertex_count, vertex_count + 1])
                    # Vertical lines
                    indices.extend([vertex_count, vertex_count + segments + 1])
                vertex_count += 1

        with self.canvas:
            self.mesh = Mesh(
                vertices=vertices,
                indices=indices,
                fmt=[('v_pos', 3, 'float')],
                mode='lines'
            )

    def update(self, dt):
        aspect = self.width / float(self.height)
        projection_mat = Matrix()
        projection_mat.perspective(45, aspect, 0.1, 1000.0)

        modelview_mat = Matrix()
        modelview_mat.look_at(
            self.camera_x, self.camera_y, self.camera_z,  # Camera position
            self.target_x, self.target_y, self.target_z,  # Look at point
            0, 1, 0  # Up vector
        )
        modelview_mat.rotate(self.rotation_x, 1, 0, 0)
        modelview_mat.rotate(self.rotation_y, 0, 1, 0)

        # Update shader matrices
        self.canvas['projection_mat'] = projection_mat
        self.canvas['modelview_mat'] = modelview_mat
        self.canvas['scale'] = float(self.scale)

        # Update info label
        self.info_label.text = f'Camera Position:\nX: {self.camera_x:.1f}\nY: {self.camera_y:.1f}\nZ: {self.camera_z:.1f}'

        # Clear and draw
        self.canvas.clear()
        with self.canvas:
            self.mesh

    def get_camera_position(self):
        return self.camera_x, self.camera_y, self.camera_z

    def rotate_points(self, points):
        # Convert angles to radians
        rx = math.radians(self.rotation_x)
        ry = math.radians(self.rotation_y)
        
        # Transform points relative to camera
        points = points.copy()
        points = points - np.array([self.camera_x, self.camera_y, self.camera_z])
        
        # Apply rotations
        rot_x = np.array([
            [1, 0, 0],
            [0, math.cos(rx), -math.sin(rx)],
            [0, math.sin(rx), math.cos(rx)]
        ])
        
        rot_y = np.array([
            [math.cos(ry), 0, math.sin(ry)],
            [0, 1, 0],
            [-math.sin(ry), 0, math.cos(ry)]
        ])
        
        points = points @ rot_y @ rot_x
        
        # Project to 2D
        projected_points = []
        for point in points:
            x, y, z = point
            # Perspective division with safety check
            z_offset = z + 1000  # Ensure we don't get too close to zero
            if abs(z_offset) < 0.0001:
                z_offset = 0.0001
            factor = 1000 / z_offset
            px = x * factor
            py = y * factor
            projected_points.extend([px, py])
            
        return projected_points

    def update_camera_from_rotations(self):
        # Convert current rotations to camera position
        rx = math.radians(self.rotation_x)
        ry = math.radians(self.rotation_y)
        
        distance = self.camera_z / self.scale
        self.camera_x = distance * math.sin(ry)
        self.camera_y = distance * math.sin(rx)
        self.camera_z = distance * math.cos(rx) * math.cos(ry)

    def _on_key_down(self, keyboard, keycode, text, modifiers):
        if keycode[1] == 'q':
            App.get_running_app().stop()
            return True
        elif keycode[1] == 'c':
            # Reset camera to center position (0, 0, 200)
            self.camera_x = 0
            self.camera_y = 0
            self.camera_z = 200
            self.target_x = 0
            self.target_y = 0
            self.target_z = 0
            self.rotation_x = 0
            self.rotation_y = 0
            self.scale = 1.0
            print("Camera reset to center")
            return True
        return False

    def on_touch_move(self, touch):
        if self.mouse_down:
            dx = touch.x - self.last_x
            dy = touch.y - self.last_y
            self.rotation_y += dx * 0.5
            self.rotation_x += dy * 0.5
            self.update_camera_from_rotations()
            self.last_x = touch.x
            self.last_y = touch.y
            print("Camera position:", self.get_camera_position())
            return True
        elif self.right_mouse_down:
            dy = touch.y - self.last_y
            # Move mouse up to zoom in, down to zoom out
            self.scale *= (1.0 + dy * 0.01)
            self.scale = max(0.1, min(self.scale, 10.0))
            self.update_camera_from_rotations()
            self.last_y = touch.y
            print("Scale:", self.scale)
            return True
        return super(Sphere3D, self).on_touch_move(touch)

    def _on_keyboard_closed(self):
        self._keyboard.unbind(on_key_down=self._on_key_down)
        self._keyboard = None

    def on_touch_down(self, touch):
        if touch.button == 'left':
            self.mouse_down = True
            self.last_x = touch.x
            self.last_y = touch.y
            print("Mouse down at", touch.x, touch.y)
            return True
        elif touch.button == 'right':
            self.right_mouse_down = True
            self.last_y = touch.y
            print("Right mouse down at", touch.x, touch.y)
            return True
        return super(Sphere3D, self).on_touch_down(touch)

    def on_touch_up(self, touch):
        if touch.button == 'left':
            self.mouse_down = False
            return True
        elif touch.button == 'right':
            self.right_mouse_down = False
            return True
        return super(Sphere3D, self).on_touch_up(touch)

class Sphere3DApp(App):
    def build(self):
        return Sphere3D()

if __name__ == '__main__':
    Sphere3DApp().run()
