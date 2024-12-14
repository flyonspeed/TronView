import os
import math
from kivy.app import App
from kivy.clock import Clock
from kivy.core.window import Window
from kivy3 import Scene, Renderer, PerspectiveCamera
from kivy3.objects.mesh import Mesh
from kivy3.materials import Material
from kivy.uix.floatlayout import FloatLayout


class ObjectTrackball(FloatLayout):
    def __init__(self, camera, radius, *args, **kw):
        super(ObjectTrackball, self).__init__(*args, **kw)
        self.camera = camera
        self.radius = radius
        self.phi = 90
        self.theta = 0
        self._touches = []
        self.camera.pos.z = radius
        camera.look_at((0, 0, 0))
        self.auto_rotate = False
        self._keyboard = Window.request_keyboard(self._on_keyboard_closed, self)
        self._keyboard.bind(on_key_down=self._on_key_down)
        Clock.schedule_interval(self._update_rotation, 1.0/60.0)

    def _on_keyboard_closed(self):
        self._keyboard.unbind(on_key_down=self._on_key_down)
        self._keyboard = None

    def _on_key_down(self, keyboard, keycode, text, modifiers):
        if keycode[1] == 'a':
            self.auto_rotate = not self.auto_rotate
        elif keycode[1] == 'q':
            App.get_running_app().stop()
        elif keycode[1] == 'c':
            self.camera.pos = (0, 0, 0)
            self.camera.look_at((1, 0, 0))  # Look along X-axis when centered
        return True

    def _update_rotation(self, dt):
        if self.auto_rotate:
            self.theta += 1  # Rotate 1 degree per frame
            _phi = math.radians(self.phi)
            _theta = math.radians(self.theta)
            z = self.radius * math.cos(_theta) * math.sin(_phi)
            x = self.radius * math.sin(_theta) * math.sin(_phi)
            y = self.radius * math.cos(_phi)
            self.camera.pos = x, y, z
            self.camera.look_at((0, 0, 0))

    def define_rotate_angle(self, touch):
        theta_angle = (touch.dx / self.width) * -360
        phi_angle = -1 * (touch.dy / self.height) * 360
        return phi_angle, theta_angle

    def on_touch_down(self, touch):
        touch.grab(self)
        self._touches.append(touch)

    def on_touch_up(self, touch):
        touch.ungrab(self)
        self._touches.remove(touch)

    def on_touch_move(self, touch):
        if touch in self._touches and touch.grab_current == self:
            if len(self._touches) == 1:
                self.do_rotate(touch)

    def do_rotate(self, touch):
        d_phi, d_theta = self.define_rotate_angle(touch)
        self.phi += d_phi
        self.theta += d_theta
        _phi = math.radians(self.phi)
        _theta = math.radians(self.theta)
        z = self.radius * math.cos(_theta) * math.sin(_phi)
        x = self.radius * math.sin(_theta) * math.sin(_phi)
        y = self.radius * math.cos(_phi)
        self.camera.pos = x, y, z
        self.camera.look_at((0, 0, 0))


def create_wireframe_sphere(radius=1.0, segments=20):
    vertices = []
    indices = []
    
    # Create vertices
    for i in range(segments + 1):
        lat = math.pi * (-0.5 + float(i) / segments)
        for j in range(segments + 1):
            lon = 2 * math.pi * float(j) / segments
            x = math.cos(lat) * math.cos(lon)
            y = math.cos(lat) * math.sin(lon)
            z = math.sin(lat)
            vertices.extend([x * radius, y * radius, z * radius])

    # Create indices for wireframe
    for i in range(segments):
        for j in range(segments):
            current = i * (segments + 1) + j
            next_row = (i + 1) * (segments + 1) + j
            
            # Horizontal lines
            indices.extend([current, current + 1])
            # Vertical lines
            indices.extend([current, next_row])

    return vertices, indices


class MainApp(App):
    def build(self):
        scene = Scene()
        camera = PerspectiveCamera(15, 1, 1, 1000)

        # Create renderer
        shader_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "simple.glsl")
        renderer = Renderer(shader_file=shader_path)
        renderer.set_camera(camera)

        # Create sphere mesh
        vertices, indices = create_wireframe_sphere(radius=3.0, segments=20)
        material = Material(color=(1, 1, 1))
        sphere_mesh = Mesh(vertices=vertices, indices=indices, material=material)
        scene.add(sphere_mesh)

        # Create trackball for camera
        trackball = ObjectTrackball(camera=camera, radius=10.0, size=renderer.size)

        root = FloatLayout()
        root.add_widget(renderer)
        root.add_widget(trackball)

        renderer.render(scene)
        return root

    def _adjust_aspect(self, inst, val):
        rsize = self.renderer.size
        aspect = rsize[0] / float(rsize[1])
        self.renderer.camera.aspect = aspect


if __name__ == '__main__':
    MainApp().run()
