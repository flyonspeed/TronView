import os
import math
from kivy.app import App
from kivy.clock import Clock
from kivy.core.window import Window
from kivy3 import Scene, Renderer, PerspectiveCamera
from kivy3.loaders import OBJLoader
from kivy.uix.floatlayout import FloatLayout
from kivy.core.window import Window
from kivy.uix.label import Label

# Resources pathes
_this_path = os.path.dirname(os.path.realpath(__file__))
obj_file = os.path.join(_this_path, "./MQ-27.obj")
#obj_file = os.path.join(_this_path, "./test1.obj")


class ObjectTrackball(FloatLayout):

    def __init__(self, camera, radius, obj3d=None, *args, **kw):
        super(ObjectTrackball, self).__init__(*args, **kw)
        self.camera = camera
        self.radius = radius
        self.obj3d = obj3d  # Store reference to the 3D object
        self.phi = 90
        self.theta = 0
        self._touches = []
        self.camera.pos.z = radius
        self.zoom_speed = 100  # Units to zoom per key press
        self.look_at_point = (0, 0, 0)  # Store look at point
        self.initial_touch_pos = None  # Store initial touch position
        self.initial_obj_pos = None    # Store initial object position
        self.initial_camera_pos = None  # Store initial camera position
        camera.look_at(self.look_at_point)
        self.auto_rotate = False
        self.camera_rotate = False
        self._keyboard = Window.request_keyboard(self._on_keyboard_closed, self)
        self._keyboard.bind(on_key_down=self._on_key_down)
        Clock.schedule_interval(self._update_rotation, 1.0/60.0)
        
        # Add labels for object and camera info
        self.obj_info = Label(
            text='Object Info',
            pos_hint={'x': 0.02, 'top': 0.98},
            size_hint=(None, None),
            halign='left',
            valign='top'
        )
        self.camera_info = Label(
            text='Camera Info',
            pos_hint={'x': 0.02, 'y': 0.02},
            size_hint=(None, None),
            halign='left',
            valign='bottom'
        )
        self.add_widget(self.obj_info)
        self.add_widget(self.camera_info)
        Clock.schedule_interval(self._update_info, 1.0/30.0)

    def _on_keyboard_closed(self):
        self._keyboard.unbind(on_key_down=self._on_key_down)
        self._keyboard = None

    def _on_key_down(self, keyboard, keycode, text, modifiers):
        if keycode[1] == 'a':
            self.auto_rotate = not self.auto_rotate
            self.camera_rotate = False  # Stop camera rotation when starting object rotation
        elif keycode[1] == 'q':
            App.get_running_app().stop()
        elif keycode[1] == 'c':
            # Move camera to center (0,0,0)
            self.camera.pos = (0, 0, 0)
            # Look slightly along positive X axis so we can see the object
            self.camera.look_at((1, 0, 0))
            self.phi = 90
            self.theta = 0
            self.auto_rotate = False
            self.camera_rotate = False
        elif keycode[1] == 's':
            self.camera_rotate = not self.camera_rotate
            self.auto_rotate = False  # Stop object rotation when starting camera rotation
        elif keycode[1] == 'z':
            # Move camera closer
            direction = (
                self.look_at_point[0] - self.camera.pos.x,
                self.look_at_point[1] - self.camera.pos.y,
                self.look_at_point[2] - self.camera.pos.z
            )
            length = math.sqrt(direction[0]**2 + direction[1]**2 + direction[2]**2)
            if length > self.zoom_speed:  # Prevent getting too close
                self.camera.pos.x += direction[0] * (self.zoom_speed / length)
                self.camera.pos.y += direction[1] * (self.zoom_speed / length)
                self.camera.pos.z += direction[2] * (self.zoom_speed / length)
        elif keycode[1] == 'x':
            # Move camera farther
            direction = (
                self.look_at_point[0] - self.camera.pos.x,
                self.look_at_point[1] - self.camera.pos.y,
                self.look_at_point[2] - self.camera.pos.z
            )
            length = math.sqrt(direction[0]**2 + direction[1]**2 + direction[2]**2)
            self.camera.pos.x -= direction[0] * (self.zoom_speed / length)
            self.camera.pos.y -= direction[1] * (self.zoom_speed / length)
            self.camera.pos.z -= direction[2] * (self.zoom_speed / length)
        return True

    def _update_rotation(self, dt):
        if self.auto_rotate and self.obj3d:
            # Calculate new position
            angle = math.radians(self.theta)
            radius = 31.0  # Distance from center
            self.obj3d.pos.x = radius * math.cos(angle)
            self.obj3d.pos.z = radius * math.sin(angle)
            
            # Update rotation matrix
            from kivy.graphics.transformation import Matrix
            rot_mat = Matrix().rotate(1, 0, 1, 0)  # Rotate 1 degree around Y axis
            
            if not hasattr(self.obj3d, 'current_rot'):
                self.obj3d.current_rot = Matrix()
            
            self.obj3d.current_rot = self.obj3d.current_rot.multiply(rot_mat)
            self.obj3d.rot_mat = self.obj3d.current_rot
            self.theta += 1

        elif self.camera_rotate:
            # Rotate camera around object
            angle = math.radians(self.theta)
            x = self.radius * math.cos(angle)
            z = self.radius * math.sin(angle)
            y = self.camera.pos.y  # Keep the same height
            self.camera.pos = x, y, z
            self.camera.look_at((0, 0, 0))
            self.theta += 1

    def _update_info(self, dt):
        # Update object information
        if self.obj3d:
            obj_text = f"Object Information:\n"
            obj_text += f"Position: ({self.obj3d.pos.x:.1f}, {self.obj3d.pos.y:.1f}, {self.obj3d.pos.z:.1f})\n"
            if hasattr(self.obj3d, 'current_rot'):
                rot_mat = self.obj3d.current_rot
                obj_text += f"Rotation Matrix:\n"
                for i in range(4):
                    row = [f"{rot_mat[i*4 + j]:.2f}" for j in range(4)]
                    obj_text += f"  {' '.join(row)}\n"
            obj_text += f"Auto Rotate: {'On' if self.auto_rotate else 'Off'}\n"
            obj_text += f"Theta: {self.theta:.1f}°"
            self.obj_info.text = obj_text

        # Update camera information
        cam_text = f"Camera Information:\n"
        cam_text += f"Position: ({self.camera.pos.x:.1f}, {self.camera.pos.y:.1f}, {self.camera.pos.z:.1f})\n"
        cam_text += f"Look At: ({self.look_at_point[0]:.1f}, {self.look_at_point[1]:.1f}, {self.look_at_point[2]:.1f})\n"
        cam_text += f"Camera Rotate: {'On' if self.camera_rotate else 'Off'}\n"
        cam_text += f"Phi: {self.phi:.1f}°\n"
        cam_text += f"Distance: {self._get_camera_distance():.1f}"
        self.camera_info.text = cam_text

    def _get_camera_distance(self):
        # Calculate current distance from camera to look_at point
        dx = self.camera.pos.x - self.look_at_point[0]
        dy = self.camera.pos.y - self.look_at_point[1]
        dz = self.camera.pos.z - self.look_at_point[2]
        return math.sqrt(dx*dx + dy*dy + dz*dz)

    def define_rotate_angle(self, touch):
        theta_angle = (touch.dx / self.width) * -720  # Doubled from 360
        phi_angle = -1 * (touch.dy / self.height) * 720  # Doubled from 360
        return phi_angle, theta_angle

    def on_touch_down(self, touch):
        if not self.collide_point(*touch.pos):
            return False
        touch.grab(self)
        self._touches.append(touch)
        if len(self._touches) == 1:
            self.initial_touch_pos = (touch.x, touch.y)
            if self.obj3d:
                self.initial_obj_pos = (self.obj3d.pos.x, self.obj3d.pos.y, self.obj3d.pos.z)
            self.initial_camera_pos = (self.camera.pos.x, self.camera.pos.y, self.camera.pos.z)
        return True

    def on_touch_up(self, touch):
        if touch.grab_current is self:
            touch.ungrab(self)
            if touch in self._touches:
                self._touches.remove(touch)
            # Reset initial positions
            self.initial_touch_pos = None
            self.initial_obj_pos = None
            self.initial_camera_pos = None
        return True

    def on_touch_move(self, touch):
        if touch in self._touches and touch.grab_current == self:
            if len(self._touches) == 1:
                # Left mouse button (button 'left') rotates object
                # Right mouse button (button 'right') rotates camera
                if hasattr(touch, 'button') and touch.button == 'right':
                    self.do_rotate_camera(touch)
                else:
                    self.do_rotate_object(touch)
            return True
        return False

    def do_rotate_camera(self, touch):
        if not self.initial_touch_pos or not self.initial_camera_pos:
            return
            
        d_phi, d_theta = self.define_rotate_angle(touch)
        self.phi += d_phi
        self.theta += d_theta

        _phi = math.radians(self.phi)
        _theta = math.radians(self.theta)
        
        # Calculate new position relative to initial camera position
        radius = self._get_camera_distance()
        z = radius * math.cos(_theta) * math.sin(_phi)
        x = radius * math.sin(_theta) * math.sin(_phi)
        y = radius * math.cos(_phi)
        
        # Update camera position
        self.camera.pos.x = x
        self.camera.pos.y = y
        self.camera.pos.z = z
        self.camera.look_at(self.look_at_point)

    def do_rotate_object(self, touch):
        if not self.initial_touch_pos or not self.initial_obj_pos:
            return
            
        # Calculate movement relative to initial touch position
        dx = (touch.x - self.initial_touch_pos[0]) / self.width
        dy = (touch.y - self.initial_touch_pos[1]) / self.height
        
        # Convert to angles (scale the movement)
        d_theta = dx * 360  # Increased from 180
        d_phi = dy * 360   # Increased from 180
        
        if self.obj3d:
            # Convert angles to radians
            phi = math.radians(d_phi)
            theta = math.radians(d_theta)
            
            # Calculate new position relative to initial position
            radius = 5.0  # Increased from 3.0 for more dramatic movement
            self.obj3d.pos.x = self.initial_obj_pos[0] + radius * math.sin(theta)
            self.obj3d.pos.z = self.initial_obj_pos[2] + radius * (1 - math.cos(theta))
            self.obj3d.pos.y = self.initial_obj_pos[1] + radius * math.sin(phi)
            
            # Create rotation matrices
            from kivy.graphics.transformation import Matrix
            rot_mat = Matrix()
            rot_mat = rot_mat.rotate(d_phi, 1, 0, 0)  # X-axis rotation
            rot_mat = rot_mat.rotate(d_theta, 0, 1, 0)  # Y-axis rotation
            
            if not hasattr(self.obj3d, 'current_rot'):
                self.obj3d.current_rot = Matrix()
            
            self.obj3d.current_rot = rot_mat
            self.obj3d.rot_mat = self.obj3d.current_rot

class MainApp(App):

    def build(self):
        self.renderer = Renderer()
        scene = Scene()
        camera = PerspectiveCamera(15, 1, 100, 2500)
        loader = OBJLoader()
        obj = loader.load(obj_file)
        self.obj3d = obj
        self.camera = camera
        root = ObjectTrackball(camera, 1500, obj)  # Pass obj to trackball

        scene.add(obj)

        self.renderer.render(scene, camera)
        self.renderer.main_light.intensity = 500

        root.add_widget(self.renderer)
        self.renderer.bind(size=self._adjust_aspect)
        return root

    def _adjust_aspect(self, inst, val):
        rsize = self.renderer.size
        aspect = rsize[0] / float(rsize[1])
        self.renderer.camera.aspect = aspect


if __name__ == '__main__':
    MainApp().run()
