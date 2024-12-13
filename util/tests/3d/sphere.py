from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.floatlayout import FloatLayout
from kivy.core.window import Window
from kivy.graphics.instructions import RenderContext
from kivy.graphics.transformation import Matrix
from kivy.graphics import Mesh, Color, Rectangle
from kivy.clock import Clock
from kivy.core.text import Label as CoreLabel
import os
import math
import time

class Sphere3D(Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.canvas = RenderContext()
        shader_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'sphere.glsl')
        self.canvas.shader.source = shader_path
        
        # Create sphere mesh
        self.create_sphere(radius=1.0, segments=20)
        
        # Initialize matrices
        self.canvas['center_the_sphere'] = Matrix().translate(0, 0, 0)
        self.canvas['my_view'] = Matrix().look_at(3, 3, 2, 0, 0, 0, 0, 0, 1)
        self.canvas['my_proj'] = Matrix()
        aspect = Window.size[0] / float(Window.size[1])
        self.canvas['my_proj'].perspective(30, aspect, 0.1, 100)
        
        # Set up rotation
        self.angle = 0
        Clock.schedule_interval(self.update, 1.0/60.0)

    def create_sphere(self, radius=1.0, segments=20):
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
                fmt=[(b'my_vertex_position', 3, 'float')],
                mode='lines'
            )

    def update(self, dt):
        self.angle += 0.01
        self.canvas['my_rotation'] = Matrix().rotate(self.angle, 0, 0, 1)

class MainWidget(FloatLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        # Add 3D sphere
        self.sphere = Sphere3D()
        self.add_widget(self.sphere)
        
        # Set up keyboard
        self._keyboard = Window.request_keyboard(self._on_keyboard_closed, self)
        self._keyboard.bind(on_key_down=self._on_key_down)
        
        # FPS counter setup
        self.fps = 0
        self.frame_count = 0
        self.last_time = time.time()
        
        with self.canvas.after:
            self.fps_color = Color(1, 1, 1, 1)
            self.fps_rect = Rectangle(pos=(0, 0), size=(0, 0))
        
        Clock.schedule_interval(self.update_fps, 1.0/60.0)

    def update_fps(self, dt):
        self.frame_count += 1
        current_time = time.time()
        if current_time - self.last_time > 1.0:
            self.fps = self.frame_count / (current_time - self.last_time)
            self.frame_count = 0
            self.last_time = current_time
            
            # Update FPS display
            label = CoreLabel(text=f'FPS: {self.fps:.1f}', font_size=20)
            label.refresh()
            texture = label.texture
            self.fps_rect.pos = (Window.width - texture.width - 10,
                               Window.height - texture.height - 10)
            self.fps_rect.size = texture.size
            self.fps_rect.texture = texture

    def _on_keyboard_closed(self):
        self._keyboard.unbind(on_key_down=self._on_key_down)
        self._keyboard = None

    def _on_key_down(self, keyboard, keycode, text, modifiers):
        if keycode[1] == 'q':
            App.get_running_app().stop()
            return True
        return False

class MyApp(App):
    def build(self):
        return MainWidget()

if __name__ == '__main__':
    MyApp().run()
