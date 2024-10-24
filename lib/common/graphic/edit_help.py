import pygame
import pygame_gui
from pygame_gui.elements import UIWindow, UITextBox

def show_help_dialog(pygame_gui_manager):
    help_text = """
    Key Commands:
    ? - Show this help dialog
    E - Exit Edit Mode (goto normal mode)
    Q - Quit
    ESC - unselect all objects
    A - Add new screen object
    G - Group selected objects
    Ctrl G - Ungroup selected group
    B - Toggle boundary boxes
    C - Clone selected object(s)    
    DELETE or BACKSPACE - Delete selected object
    S - Save screen to JSON
    L - Load last savedscreen from JSON
    Cntrl L - Load default screen
    F - Toggle FPS and draw time display
    R - Toggle ruler mode and grid display mode
    Arrow keys - Move selected object(s)
    Ctrl + Arrow keys - Move selected object(s) by 10 pixels
    PAGE UP - Move selected object up in draw order
    PAGE DOWN - Move selected object down in draw order
    Ctrl Z - Undo last change
    TAB - Cycle through selected objects
    """

    window_width = 450
    window_height = 550
    screen_width, screen_height = pygame.display.get_surface().get_size()
    x = (screen_width - window_width) // 2
    y = (screen_height - window_height) // 2

    help_window = UIWindow(pygame.Rect(x, y, window_width, window_height),
                           pygame_gui_manager,
                           window_display_title="Help",
                           object_id="#help_window")

    UITextBox(help_text,
              pygame.Rect(10, 10, window_width - 20, window_height - 40),
              pygame_gui_manager,
              container=help_window,
              object_id="#help_textbox")

    print("Help window created")  # Add this line for debugging
    return help_window
