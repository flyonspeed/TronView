import pygame
import pygame_gui
import os
import json
from pygame_gui.elements import UIWindow, UILabel, UIButton, UITextEntryLine, UIDropDownMenu
from pygame_gui.windows import UIColourPickerDialog
from lib.common import shared

############################################################################################
############################################################################################
# Show the options for a module. These are controls that are built based off the get_module_options() method in the module.
class EditOptionsBar:
    def __init__(self, screen_object, pygame_gui_manager, smartdisplay):
        self.screen_object = screen_object
        self.pygame_gui_manager = pygame_gui_manager
        self.visible = True
        self.ui_elements = []
        self.text_entry_active: UITextEntryLine | None = None  # Add this line
        
        window_width = 260
        window_height = self.calculate_height()
        
        # Position the window to the right of the screen object
        x = min(screen_object.x + screen_object.width, smartdisplay.x_end - window_width)
        y = screen_object.y
        
        # Ensure the window fits within the screen
        if y + window_height > smartdisplay.y_end:
            y = max(0, smartdisplay.y_end - window_height)
        
        
        self.window = UIWindow(
            pygame.Rect(x, y, window_width, window_height),
            self.pygame_gui_manager,
            window_display_title=f"Options: {screen_object.title}",
            object_id="#options_window",
            draggable=False
        )
        
        # Create a scrollable container inside the window
        self.scrollable_container = pygame_gui.elements.UIScrollingContainer(
            relative_rect=pygame.Rect(0, 0, window_width, window_height - 30),
            manager=self.pygame_gui_manager,
            container=self.window,
            anchors={'left': 'left', 'right': 'right', 'top': 'top', 'bottom': 'bottom'},
            allow_scroll_x=False
        )
        
        self.color_pickers = {}  # To keep track of open color pickers
        
        self.build_ui()
        self.update_position()

    def calculate_height(self):
        if self.screen_object.type == 'module':
            if self.screen_object.module is None:
                return 0
            if not hasattr(self.screen_object.module, "get_module_options"):
                return 30    
            options = self.screen_object.module.get_module_options()
            height = 10  # Initial padding
            for option, details in options.items():
                height += 25  # Label height
                height += 30  # Option input height
                height += 5   # Padding between options
            height += 10  # Additional padding at the bottom
            
            # Ensure a minimum height of 100 pixels
            return max(min(height, 500), 100)  # Limit height between 100 and 500 pixels
        if self.screen_object.type == 'group':
            return 300
        return 0

    def build_ui(self):
        
        y_offset = 10
        x_offset = 10
        # clear the ui elements if they exist remove them
        for element in self.ui_elements:
            element.kill()
        self.ui_elements = []

        if self.screen_object.type == 'group':
            label = UILabel(
                relative_rect=pygame.Rect(x_offset, y_offset, 180, 20),
                text="Group Options Not Implemented Yet",
                manager=self.pygame_gui_manager,
                container=self.scrollable_container,
                object_id="#options_group_"
            )
            self.ui_elements.append(label)
            return

        if not hasattr(self.screen_object.module, "get_module_options"):
            # add a label saying options not implemented yet
            label = UILabel(
                relative_rect=pygame.Rect(10, 10, 180, 20),
                text="Options Not Implemented Yet",
                manager=self.pygame_gui_manager,
                container=self.scrollable_container,
                object_id="#options_label_not_implemented"
            )
            self.ui_elements.append(label)
            return
        
        # else this is a module
        options = self.screen_object.module.get_module_options()
        total_height = 10  # Initial padding

        for option, details in options.items():
            if details.get('hidden', False):
                continue  # Skip hidden options
            # Add height for label
            total_height += 25
            label = UILabel(
                relative_rect=pygame.Rect(x_offset, y_offset, 180, 20),
                text=details['label'],
                manager=self.pygame_gui_manager,
                container=self.scrollable_container,
                object_id="#options_label_" + option
            )
            y_offset += 25
            label.object_id = "#options_label_" + option
            self.ui_elements.append(label)

            # Add height for option control
            total_height += 30
            if details['type'] == 'bool':
                checkbox = UIButton(
                    relative_rect=pygame.Rect(x_offset, y_offset, 180, 20),
                    text='On' if getattr(self.screen_object.module, option) else 'Off',
                    manager=self.pygame_gui_manager,
                    container=self.scrollable_container
                )
                checkbox.option_name = option
                checkbox.object_id = "#options_checkbox_" + option
                self.ui_elements.append(checkbox)
            elif details['type'] == 'int':
                slider = pygame_gui.elements.UIHorizontalSlider(
                    relative_rect=pygame.Rect(x_offset, y_offset, 180, 20),
                    start_value=getattr(self.screen_object.module, option),
                    value_range=(details['min'], details['max']),
                    manager=self.pygame_gui_manager,
                    container=self.scrollable_container
                )
                slider.option_name = option
                slider.object_id = "#options_slider_" + option
                self.ui_elements.append(slider)
                # show the current value by appending it to the label already created
                label.set_text(label.text + " " + str(getattr(self.screen_object.module, option)))
            elif details['type'] in ['float', 'text']:
                text_entry = UITextEntryLine(
                    relative_rect=pygame.Rect(x_offset, y_offset, 180, 20),
                    manager=self.pygame_gui_manager,
                    container=self.scrollable_container
                )
                text_entry.set_text(str(getattr(self.screen_object.module, option)))
                text_entry.option_name = option
                text_entry.object_id = "#options_text_" + option
                self.ui_elements.append(text_entry)
            elif details['type'] == 'color':
                # for color add a button that will trigger showing a color picker
                current_color = getattr(self.screen_object.module, option)
                current_color_pygame = pygame.Color(*current_color)
                color_button = UIButton(
                    relative_rect=pygame.Rect(x_offset, y_offset, 180, 20),
                    text='',
                    manager=self.pygame_gui_manager,
                    container=self.scrollable_container,
                )
                # color_button.background_colour = current_color
                # convert current_color to #RRGGBBAA
                color_button.colours['normal_bg'] =  current_color_pygame
                color_button.option_name = option
                color_button.object_id = "#options_color_" + option
                color_button.rebuild()
                self.ui_elements.append(color_button)
            elif details['type'] == 'dropdown':
                current_value = getattr(self.screen_object.module, option)
                options_list = details['options']
                
                # Ensure the current value is in the options list
                if current_value not in options_list and current_value is not None and current_value != 0:
                    print(f"Warning: current value '{current_value}' not in options list for dropdown '{option}'")
                    options_list.append(current_value)
                
                dropdown = UIDropDownMenu(
                    options_list=options_list,
                    starting_option=current_value,
                    relative_rect=pygame.Rect(x_offset, y_offset, 200, 25),
                    manager=self.pygame_gui_manager,
                    container=self.scrollable_container
                )
                y_offset += 5 # make room for the dropdown
                dropdown.option_name = option
                dropdown.object_id = "#options_dropdown_" + option
                self.ui_elements.append(dropdown)

            y_offset += 30 # move down 30 pixels so we can draw another control
            total_height += 5  # Padding between options

        # Set the scrollable area
        self.scrollable_container.set_scrollable_area_dimensions((180, total_height))

    def handle_event(self, event):

        #print("event: %s" % event)
        if event.type == pygame.MOUSEBUTTONDOWN:
            #print("MOUSEBUTTONDOWN")
            # check if they clicked on a text entry field
            foundClickedTextEntry = False
            for element in self.ui_elements:
                if isinstance(element, UITextEntryLine) and element.rect.collidepoint(event.pos):
                    print("Text entry field clicked")
                    self.text_entry_active = element
                    foundClickedTextEntry = True
                    break           
            if foundClickedTextEntry == False:
                self.text_entry_active = None # else they didn't click on a text entry field

        if event.type == pygame_gui.UI_BUTTON_PRESSED:
            for element in self.ui_elements:
                if isinstance(element, UIButton) and event.ui_element == element:
                    if hasattr(element, 'option_name'):
                        option = element.option_name
                        if self.screen_object.module.get_module_options()[option]['type'] == 'color':
                            self.show_color_picker(option)  # clicked on a button to open a color picker
                        else:
                            self.on_checkbox_click(option)
        elif event.type == pygame_gui.UI_COLOUR_PICKER_COLOUR_PICKED:
            # check if this event is for a color picker
            for option, picker in list(self.color_pickers.items()):
                if event.ui_element == picker:
                    self.on_color_picked(option, event.colour)
        elif event.type == pygame_gui.UI_HORIZONTAL_SLIDER_MOVED:
            for element in self.ui_elements:
                if isinstance(element, pygame_gui.elements.UIHorizontalSlider) and event.ui_element == element:
                    self.on_slider_moved(element.option_name, event.value)
        elif event.type == pygame_gui.UI_TEXT_ENTRY_CHANGED:
            self.text_entry_active = event.ui_element
        elif event.type == pygame_gui.UI_TEXT_ENTRY_FINISHED:
            print("Text entry finished")
            self.text_entry_active = None
            self.on_text_submit_change(event.ui_element.option_name, event.text) # send the option name and the text entered
        elif event.type == pygame_gui.UI_DROP_DOWN_MENU_CHANGED:
            for element in self.ui_elements:
                if isinstance(element, UIDropDownMenu) and event.ui_element == element:
                    self.on_dropdown_selection(element.option_name, event.text)

    def on_checkbox_click(self, option):
        current_value = getattr(self.screen_object.module, option)
        new_value = not current_value
        shared.Change_history.add_change("option_change", {
            "object": self.screen_object,
            "option": option,
            "old_value": current_value,
            "new_value": new_value
        })
        setattr(self.screen_object.module, option, new_value)
        for element in self.ui_elements:
            if isinstance(element, UIButton) and element.option_name == option:
                element.set_text('On' if new_value else 'Off')
                break
        if hasattr(self.screen_object.module, 'update_option'):
            self.screen_object.module.update_option(option, new_value)
        
        # Check for post_change_function
        options = self.screen_object.module.get_module_options()
        if 'post_change_function' in options[option]:
            post_change_function = getattr(self.screen_object.module, options[option]['post_change_function'], None)
            if post_change_function:
                post_change_function()

    def on_slider_moved(self, option, value):
        old_value = getattr(self.screen_object.module, option)
        shared.Change_history.add_change("option_change", {
            "object": self.screen_object,
            "option": option,
            "old_value": old_value,
            "new_value": int(value)
        })
        setattr(self.screen_object.module, option, int(value))
        if hasattr(self.screen_object.module, 'update_option'):
            self.screen_object.module.update_option(option, int(value))
        
        # Check for post_change_function
        options = self.screen_object.module.get_module_options()
        if 'post_change_function' in options[option]:
            post_change_function = getattr(self.screen_object.module, options[option]['post_change_function'], None)
            if post_change_function:
                post_change_function()
        # update the label with the new value by finding it by object_id
        for element in self.ui_elements:
            if isinstance(element, UILabel):
                # make sure element has object_id
                #print("element.text: %s" % element.text)
                if hasattr(element, 'object_id'):
                    #print("element.object_id: %s" % element.object_id)
                    if element.object_id == "#options_label_" + option:
                        element.set_text(options[option]['label'] + ": " + str(int(value)))
                        break

    def on_text_submit_change(self, option, text):
        old_value = getattr(self.screen_object.module, option)
        option_type = self.screen_object.module.get_module_options()[option]['type']
        if option_type == 'float':
            # check if there is a decimal point
            if '.' in text:
                value = float(text)
            else:
                value = int(text)
        elif option_type == 'int':
            value = int(text)
        else:
            value = text
        shared.Change_history.add_change("option_change", {
            "object": self.screen_object,
            "option": option,
            "old_value": old_value,
            "new_value": value
        })
        setattr(self.screen_object.module, option, value)
        if hasattr(self.screen_object.module, 'update_option'):
            self.screen_object.module.update_option(option, value)
        
        # Check for post_change_function
        options = self.screen_object.module.get_module_options()
        if 'post_change_function' in options[option]:
            post_change_function = getattr(self.screen_object.module, options[option]['post_change_function'], None)
            if post_change_function:
                post_change_function()
        # unfocus the text entry
        for element in self.ui_elements:
            if isinstance(element, UITextEntryLine) and element.option_name == option:
                element.is_focused = False
                break

    def show_color_picker(self, option):
        # close any open color pickers
        for picker in self.color_pickers.values():
            picker.hide()
        self.color_pickers = {}  # clear the color pickers
        print("show_color_picker: %s" % option)
        current_color = getattr(self.screen_object.module, option)
        # Convert to pygame Color object if necessary
        if isinstance(current_color, (list, tuple)):
            if len(current_color) == 3:
                current_color = pygame.Color(*current_color, 255)  # Add alpha channel if missing
            elif len(current_color) == 4:
                current_color = pygame.Color(*current_color)
        elif not isinstance(current_color, pygame.Color):
            # If it's not a recognized format, default to white
            current_color = pygame.Color(255, 255, 255, 255)

        color_picker = UIColourPickerDialog(
            rect=pygame.Rect(300, 50, 390, 390),
            manager=self.pygame_gui_manager,
            initial_colour=current_color,
            window_title=f"Color: {option}",
        )
        self.color_pickers[option] = color_picker  # set the color picker for this option

    def on_color_picked(self, option, color):
        print(f"color picked: {color}")
        # convert color to a list of ints
        newColorValue = [int(c) for c in color]
        setattr(self.screen_object.module, option, newColorValue)
        for element in self.ui_elements:
            if isinstance(element, UIButton) and getattr(element, 'option_name', None) == option:
                current_color_pygame = pygame.Color(*color)
                element.colours['normal_bg'] = current_color_pygame
                element.rebuild()
                #break
        if hasattr(self.screen_object.module, 'update_option'):
            self.screen_object.module.update_option(option, newColorValue)
        
        # Check for post_change_function
        options = self.screen_object.module.get_module_options()
        if 'post_change_function' in options[option]:
            post_change_function = getattr(self.screen_object.module, options[option]['post_change_function'], None)
            if post_change_function:
                post_change_function()
        
        self.color_pickers = {}  # clear the color pickers

    def on_dropdown_selection(self, option, value):
        old_value = getattr(self.screen_object.module, option)
        shared.Change_history.add_change("option_change", {
            "object": self.screen_object,
            "option": option,
            "old_value": old_value,
            "new_value": value
        })
        setattr(self.screen_object.module, option, value)
        if hasattr(self.screen_object.module, 'update_option'):
            self.screen_object.module.update_option(option, value)
        
        # Check for post_change_function
        options = self.screen_object.module.get_module_options()
        if option in options and 'post_change_function' in options[option]:
            post_change_function = getattr(self.screen_object.module, options[option]['post_change_function'], None)
            if post_change_function:
                post_change_function()
        # refesh all the options in the EditOptionsWindow
        self.build_ui()


    def update_position(self):
        window_width = self.window.get_abs_rect().width
        window_height = self.window.get_abs_rect().height
        screen_width, screen_height = pygame.display.get_surface().get_size()

        # Calculate x position
        x = self.screen_object.x + self.screen_object.width

        # Calculate y position
        y = self.screen_object.y

        # Check if the bottom of the window goes off the screen
        if y + window_height > screen_height:
            # Adjust y to keep the bottom of the window on the screen
            y = screen_height - window_height

        # Ensure it doesn't go above the top of the screen
        y = max(0, y)

        # if x + window_width is off the screen to the right, then move it to the left side of the screen_object
        if x + window_width > screen_width:
            x = self.screen_object.x - window_width

        # what if the window is off the screen to the left? then draw it on the right side of the screen_object
        if x < 0:
            x = self.screen_object.width - window_width

        self.window.set_position((x, y))

    #
    def update(self, time_delta):
        if self.visible:
            self.update_position()  # Update position before updating the UI
            self.pygame_gui_manager.update(time_delta)

    def draw(self, screen):
        if self.visible:
            self.pygame_gui_manager.draw_ui(screen)

    def show(self):
        self.visible = True
        self.window.show()

    def hide(self):
        self.visible = False
        self.window.hide()

    def remove_ui(self):
        self.window.kill()
        self.ui_elements.clear()
    
    # check if the gui is busy, i.e. if a colour picker is active
    def is_busy(self):
        # check if a colour picker is active
        if hasattr(self, 'color_pickers'):
            for picker in self.color_pickers.values():
                if picker.visible:
                    return True
        return False
