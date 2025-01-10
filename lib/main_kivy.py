from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.core.window import Window
from kivy.clock import Clock
from kivy.graphics.transformation import Matrix
from modules_kivy.horizon_3d.horizon_3d import Horizon3D

class TronViewApp(App):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.modules = {}
        self.show_fps = False
        self.fps_counter = 0
        self.fps_time = 0
        self.current_fps = 0
        self._keyboard = None
        
    def build(self):
        # Create the main layout
        self.main_layout = BoxLayout(orientation='vertical')
        
        # Create FPS label
        self.fps_label = Label(
            text='FPS: 0',
            size_hint=(None, None),
            pos_hint={'right': 0.98, 'top': 0.98},  # Slightly inset from corners
            size=(100, 30),
            color=(1, 1, 0, 1)  # Yellow text
        )
        self.fps_label.opacity = 0  # Initially hidden
        
        # Create and initialize modules
        self.init_modules()
        
        # Add FPS label directly to window
        Window.add_widget(self.fps_label)
        
        # Set up keyboard after window is created
        Window.bind(on_key_down=self._on_key_down)
        
        # Set up the update loop
        Clock.schedule_interval(self.update, 1.0 / 60.0)
        
        # Bind to window resize
        Window.bind(on_resize=self.on_window_resize)
        
        # Initial perspective setup
        self.setup_perspective()
        
        return self.main_layout

    def _on_key_down(self, instance, keycode, text, scancode, modifiers):
        """Handle keyboard input"""
        if keycode == 113:  # 'q' key
            App.get_running_app().stop()
            return True
        elif keycode == 102:  # 'f' key
            self.toggle_fps()
            return True
        return False
    
    def toggle_fps(self):
        """Toggle FPS display"""
        self.show_fps = not self.show_fps
        self.fps_label.opacity = 1 if self.show_fps else 0
    
    def update_fps(self, dt):
        """Update FPS counter"""
        self.fps_counter += 1
        self.fps_time += dt
        
        if self.fps_time >= 1.0:  # Update every second
            self.current_fps = self.fps_counter
            self.fps_label.text = f'FPS: {self.current_fps}'
            self.fps_counter = 0
            self.fps_time = 0
    
    def init_modules(self):
        """Initialize all visualization modules"""
        # Create the horizon module
        horizon = Horizon3D(size_hint=(1, 1))
        self.modules['horizon'] = horizon
        self.main_layout.add_widget(horizon)
    
    def setup_perspective(self, *args):
        """Set up the perspective projection matrix"""
        aspect = Window.width / float(Window.height)
        fovy = 60.0  # Field of view in degrees
        near = 0.1   # Near clipping plane
        far = 100.0  # Far clipping plane
        
        # Create perspective projection matrix
        proj = Matrix()
        proj.perspective(fovy, aspect, near, far)
        
        # Apply to all modules that have a canvas
        for module in self.modules.values():
            if hasattr(module, 'canvas'):
                module.canvas['projection_mat'] = proj
    
    def on_window_resize(self, instance, width, height):
        """Handle window resize"""
        self.setup_perspective()
    
    def update(self, dt):
        """Main update loop"""
        # Update FPS if enabled
        if self.show_fps:
            self.update_fps(dt)
        
        # Update all modules
        for module in self.modules.values():
            if hasattr(module, 'update'):
                module.update(dt)
    
    def on_stop(self):
        """Clean up when the application stops"""
        Window.remove_widget(self.fps_label)
        Window.unbind(on_key_down=self._on_key_down)

def main():
    # Set window properties
    Window.size = (1024, 768)
    Window.title = "TronView Kivy"
    
    # Create and run the application
    app = TronViewApp()
    app.run()

if __name__ == '__main__':
    main()
