import pygame
import pygame_gui
from pygame_gui.elements import UIWindow, UITextBox
from lib.version import __version__, __build_date__, __build__, __build_time__

def show_help_dialog(pygame_gui_manager):
    help_text = f"""
    TronView {__version__}
    Build: {__build__} {__build_date__} {__build_time__}
    By running this software you agree to the terms of the license.
    Use at own risk!
    TronView.org

    Key Commands:
    ? - Show this help dialog
    E - Exit Edit Mode (goto normal mode)
    Q - Quit
    ESC - unselect all objects
    DELETE or BACKSPACE - Delete selected object
    TAB - Cycle through selected objects
    SHIFT - multiple select objects

    A - Add new screen object
    G - Group selected objects
    Ctrl G - Ungroup selected group
    B - Toggle boundary boxes
    C - Clone selected object(s) 
       
    S - Save current screen to JSON
    L - Load screen from JSON
    F - Toggle FPS and draw time display
    R - Toggle ruler mode and grid display mode
    Arrow keys - Move selected object(s)
    Ctrl + Arrow keys - Move selected object(s) by 10 pixels
    PAGE UP - Move selected object up in draw order
    PAGE DOWN - Move selected object down in draw order
    Ctrl Z - Undo last change

    Text Formatting:
    Use curly braces {{}} to display dynamic data in text objects.
    
    Basic Examples:
    {{gpsData[0].latitude}} - Display GPS latitude
    {{airData[0].IAS}} - Display indicated airspeed
    {{gpsData[0].latitude:0.2f}} - Format to 2 decimal places
    
    Special Format Specifiers:
    :kts - Convert MPH to knots
    :kph - Convert MPH to kilometers per hour
    :mph - Display as MPH (no conversion)
    :km - Convert miles to kilometers
    :nm - Convert miles to nautical miles
    :ft - Display as feet (no conversion)
    :m - Convert feet to meters
    :c - Convert Fahrenheit to Celsius
    :f - Display as Fahrenheit (no conversion)
    :10th - Round to nearest 10 (101 becomes 100, 155 becomes 160)
    
    Advanced Examples:
    {{airData[0].IAS:kts}} - convert MPH to knots
    {{gpsData[0].altitude():ft}} - convert meters to feet
    """

    window_width = 500
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
