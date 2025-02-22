#!/usr/bin/env python
import pygame
import pygame_gui
from pygame_gui.elements import UITextEntryLine
from pygame_gui.elements import UILabel
from pygame_gui.elements import UIButton
from pygame_gui.elements import UIPanel
import time

class TextInput:
    def __init__(self, manager, x=None, y=None, width=300, height=30, label_text="", initial_text="", button_text="", 
                 button_action=None, with_background=False, padding=20, dark_background=False):
        """
        Create a text input with a label and button.
        
        Args:
            manager: pygame_gui.UIManager instance
            x: x position (if None, will center horizontally)
            y: y position (if None, will center vertically)
            width: total width of the component
            height: height of the component
            label_text: text to display before the input field
            initial_text: initial text in the input field
            button_text: text to display on the button
            button_action: callback function that takes text as input
            with_background: if True, creates a panel background
            padding: padding around components when using background
            dark_background: if True, creates a darker panel background
        """
        self.manager = manager
        self.button_action = button_action if button_action is not None else lambda text: None
        
        # Calculate label width based on text size
        font = pygame.font.Font(None, 36)  # Default pygame font
        label_width = font.size(label_text)[0] + 10  # Add small padding
        
        # Set component dimensions
        spacing = 10  # spacing between elements
        input_width = width  # full width for text input
        button_width = width // 4 if button_text else 0  # button takes 1/4 of width
        component_height = height  # height of each component
        total_height = component_height * 3 + (spacing * 2)  # total height for all components
        
        # Calculate center position if x or y is None
        window_width = manager.get_root_container().get_rect().width
        window_height = manager.get_root_container().get_rect().height
        
        if x is None:
            x = (window_width - width) // 2
        if y is None:
            y = (window_height - total_height) // 2

        # Create background panel if requested
        self.panel = None
        if with_background:
            panel_width = width + (padding * 2)
            panel_height = total_height + (padding * 2)
            panel_x = x - padding
            panel_y = y - padding
            
            # Recenter if coordinates were None
            if x is None:
                panel_x = (window_width - panel_width) // 2
                x = panel_x + padding
            if y is None:
                panel_y = (window_height - panel_height) // 2
                y = panel_y + padding
                
            panel_kwargs = {
                'relative_rect': pygame.Rect(panel_x, panel_y, panel_width, panel_height),
                'manager': manager
            }
            
            if dark_background:
                panel_kwargs['object_id'] = '#dark_panel'
                
            self.panel = UIPanel(**panel_kwargs)
            
            # Reset x and y to 0 for elements inside panel
            x = padding
            y = padding
        
        # Create label (first row)
        self.label = UILabel(
            relative_rect=pygame.Rect(x, y, label_width, component_height),
            text=label_text,
            manager=manager,
            container=self.panel
        )
        
        # Create text entry (second row)
        self.text_entry = UITextEntryLine(
            relative_rect=pygame.Rect(
                x,
                y + component_height + spacing,
                input_width,
                component_height
            ),
            manager=manager,
            container=self.panel
        )
        
        # Create button if button_text is provided (third row, right-aligned)
        self.button = None
        if button_text:
            self.button = UIButton(
                relative_rect=pygame.Rect(
                    x + width - button_width,
                    y + (component_height + spacing) * 2,
                    button_width,
                    component_height
                ),
                text=button_text,
                manager=manager,
                container=self.panel
            )
        
        if initial_text:
            self.text_entry.set_text(initial_text)
            
        # Auto-focus the text entry
        # delay a bit to allow the text entry to be created        
        self.visible = True

    def set_focus(self):
        """Set the focus to the text entry."""
        self.text_entry.focus()
            
    def get_text(self):
        """Get the current text in the input field."""
        return self.text_entry.get_text()
    
    def set_text(self, text):
        """Set the text in the input field."""
        self.text_entry.set_text(text)
        
    def clear(self):
        """Clear the text input field."""
        self.text_entry.set_text("")
        
    def kill(self):
        """Remove the text input, label, button, and panel from the UI."""
        if self.panel:
            self.panel.kill()
        else:
            self.label.kill()
            self.text_entry.kill()
            if self.button:
                self.button.kill()
        
    def set_visible(self, visible):
        """Show or hide the text input components."""
        if self.panel:
            self.panel.visible = visible
        else:
            self.label.visible = visible
            self.text_entry.visible = visible
            if self.button:
                self.button.visible = visible
        
    def process_event(self, event):
        """
        Process events related to the text input and button.
        Returns the text if enter is pressed, None otherwise.
        Also handles button clicks.
        """
        if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
            if self.text_entry.is_focused:
                text = self.get_text()
                if self.button_action:
                    print("button_action: ", self.button_action)
                    self.button_action(text,"OK")
                return text
        
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            if self.text_entry.is_focused:
                if self.button_action:
                    self.button_action(None,"CANCEL")
                return None

        if event.type == pygame.USEREVENT:
            # Check if event has user_type attribute
            if hasattr(event, 'user_type'):
                if (self.button and event.user_type == pygame_gui.UI_BUTTON_PRESSED 
                    and event.ui_element == self.button):
                    text = self.get_text()
                    if self.button_action:
                        print("button_action: ", self.button_action)
                        self.button_action(text,"OK")
                    return text
            else:
                print("event: ", event)
        return None

# Example usage:
"""
# Initialize pygame and pygame_gui
pygame.init()
window_surface = pygame.display.set_mode((800, 600))
manager = pygame_gui.UIManager((800, 600))

# Create text input
text_input = TextInput(
    manager=manager,
    x=100,
    y=100,
    width=300,
    height=30,
    label_text="Name:",
    initial_text="",
    button_text="Submit",
    button_action=lambda text: print(f"Submitted text: {text}")
)

# Main loop
clock = pygame.time.Clock()
is_running = True

while is_running:
    time_delta = clock.tick(60)/1000.0

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            is_running = False
            
        # Process text input events
        result = text_input.process_event(event)
        if result is not None:
            print(f"Entered text: {result}")

        manager.process_events(event)

    manager.update(time_delta)
    
    window_surface.fill((0, 0, 0))
    manager.draw_ui(window_surface)
    
    pygame.display.update()
"""

# vi: modeline tabstop=8 expandtab shiftwidth=4 softtabstop=4 syntax=python 