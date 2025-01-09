from kivy.app import App
from kivy.uix.widget import Widget
from kivy.core.window import Window
from kivy.graphics.instructions import RenderContext
from kivy.graphics.transformation import Matrix
from kivy.graphics import Mesh
from kivy.clock import Clock
import os

class MyRoot(Widget):
    axis = (0,0,1)
    angle = 0
    def __init__(self):
        super().__init__()
        shader_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'cube.glsl')
        self.canvas = RenderContext()
        self.canvas.shader.source = shader_path
        ff = ( (b'my_vertex_position', 3, 'float'), )
        vv = ( 0, 0, 0,    1., 0, 0,    1., 1., 0,    0, 1., 0,
               0, 0, 1.,   1., 0, 1.,   1., 1., 1.,   0, 1., 1. )
        ii = ( 0,1,    1,2,    2,3,    3,0,    0,4,    1,5,
               2,6,    3,7,    4,5,    5,6,    6,7,    7,4 )
        with self.canvas:
            Mesh(fmt=ff, vertices=vv, indices=ii, mode='lines')
        self.canvas['center_the_cube'] = Matrix().translate(-.5,-.5,-.5)
        self.canvas['my_view'] = Matrix().look_at(3,3,2, 0,0,0, 0,0,1)
        self.canvas['my_proj'] = Matrix()
        aspect = Window.size[0] / Window.size[1]
        self.canvas['my_proj'].perspective(30,aspect,.1,100)
        Clock.schedule_interval(self.increase_angle, 1/60)
    def increase_angle(self,_):
        self.angle += .01
        self.canvas['my_rotation'] = Matrix().rotate(self.angle,*self.axis)

class MyApp(App):
    def build(self): return MyRoot()

MyApp().run()