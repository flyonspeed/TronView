import pygame
import pygame_gui
import os
import json
from pygame_gui.elements import UIWindow, UILabel, UIButton, UITextEntryLine, UIDropDownMenu
from pygame_gui.windows import UIColourPickerDialog
from lib.common import shared
from lib.common.graphic.edit_dropdown import DropDown

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
        self.last_dropdown_click_time = 0  # Track when dropdown was clicked
        
        print(f"Creating EditOptionsBar for {screen_object.title}")
        
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
            elif details['type'] == 'float':
                # check if min and max are set. if not then show a text entry field
                if 'min' not in details or 'max' not in details:
                    text_entry = UITextEntryLine(
                        relative_rect=pygame.Rect(x_offset, y_offset, 180, 20),
                        manager=self.pygame_gui_manager,
                        container=self.scrollable_container
                    )
                    text_entry.set_text(str(getattr(self.screen_object.module, option)))
                    text_entry.option_name = option
                    text_entry.object_id = "#options_text_" + option
                    self.ui_elements.append(text_entry)
                else:
                    # For float sliders, use a smaller click increment for finer control
                    click_increment = details.get('increment', 0.001)  # Default to 0.001 if not specified
                    slider = pygame_gui.elements.UIHorizontalSlider(
                        relative_rect=pygame.Rect(x_offset, y_offset, 180, 20),
                        start_value=getattr(self.screen_object.module, option),
                        value_range=(details['min'], details['max']),
                        manager=self.pygame_gui_manager,
                        container=self.scrollable_container,
                        click_increment=click_increment
                    )   
                    slider.option_name = option
                    slider.object_id = "#float_slider_" + option
                    self.ui_elements.append(slider)
                    # show the current value by appending it to the label with 3 decimal places
                    current_value = getattr(self.screen_object.module, option)
                    label.set_text(label.text + f" {current_value:.3f}")

            
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


            elif details['type'] == 'dataship_var':
                current_value = getattr(self.screen_object.module, option)
                
                # Check if current value is "Error" and handle specially
                if current_value == "Error":
                    var_button = UIButton(
                        relative_rect=pygame.Rect(x_offset, y_offset, 180, 20),
                        text="Error (click to reset)",
                        manager=self.pygame_gui_manager,
                        container=self.scrollable_container,
                        tool_tip_text="Variable has error value. Click to select a different variable."
                    )
                    var_button.rebuild()
                else:
                    var_button = UIButton(
                        relative_rect=pygame.Rect(x_offset, y_offset, 180, 20),
                        text=current_value if current_value else 'Select variable ▼',
                        manager=self.pygame_gui_manager,
                        container=self.scrollable_container,
                        tool_tip_text="Click to select a Dataship variable"
                    )
                    var_button.rebuild()
                
                var_button.option_name = option
                var_button.object_id = "#options_dataship_var_" + option
                self.ui_elements.append(var_button)
                print(f"Created dataship_var button for option: {option}, value: {current_value}")

            elif details['type'] == 'tuple_int':
                current_value = getattr(self.screen_object.module, option)
                labels = details.get('labels', [f"Value {i+1}" for i in range(len(current_value))])
                
                # Create a text entry for each tuple element, 2 per row
                for i, (value, label) in enumerate(zip(current_value, labels)):
                    # Calculate position for 2-column layout
                    row = i // 2  # Integer division to determine row
                    col = i % 2   # Modulo to determine column (0 or 1)
                    
                    # Position calculations
                    entry_width = 85  # Narrower width to fit 2 per row
                    entry_x = x_offset + (col * (entry_width + 10))  # 10px spacing between columns
                    entry_y = y_offset + (row * 50)  # 50px per row to accommodate label + entry
                    
                    # Create label for this tuple element
                    tuple_label = UILabel(
                        relative_rect=pygame.Rect(entry_x, entry_y, entry_width, 20),
                        text=label,
                        manager=self.pygame_gui_manager,
                        container=self.scrollable_container
                    )
                    self.ui_elements.append(tuple_label)
                    
                    # Create text entry for this tuple element
                    text_entry = UITextEntryLine(
                        relative_rect=pygame.Rect(entry_x, entry_y + 20, entry_width, 20),
                        manager=self.pygame_gui_manager,
                        container=self.scrollable_container
                    )
                    text_entry.set_text(str(value))
                    text_entry.option_name = option
                    text_entry.tuple_index = i  # Store the index in the tuple
                    text_entry.object_id = f"#options_tuple_{option}_{i}"
                    self.ui_elements.append(text_entry)
                
                # Adjust y_offset based on number of rows needed
                num_rows = (len(current_value) + 1) // 2  # Round up division
                y_offset += (num_rows * 50) - 30  # Subtract 30 since we'll add it back at the end of the loop

            y_offset += 30 # move down 30 pixels so we can draw another control
            total_height += 5  # Padding between options

        # Set the scrollable area
        self.scrollable_container.set_scrollable_area_dimensions((180, total_height))


    def handle_event(self, event):
        """
        Handle events for the EditOptionsBar.  This is called by the main event loop.
        Args:
            event: pygame event
        """
        #if event.type != pygame.MOUSEMOTION and event.type != pygame.USEREVENT:
        #    print("EditOptionsBar handle_event: %s " % event)
        if event.type == pygame.MOUSEBUTTONDOWN:
            #print("MOUSEBUTTONDOWN")
            if self.text_entry_active is not None: # check if there is a current text entry field.
                # update the value of the text entry field
                self.on_text_submit_change( 
                    self.text_entry_active.option_name, 
                    self.text_entry_active.text, 
                    self.text_entry_active)

            # check if they clicked on a text entry field
            foundClickedTextEntry = False
            for element in self.ui_elements:
                if isinstance(element, UITextEntryLine) and element.rect.collidepoint(event.pos):
                    print("EditOptionsBar handle_event: Text entry field clicked")
                    self.text_entry_active = element
                    foundClickedTextEntry = True
                    element.is_focused = True
                    break           
            if foundClickedTextEntry == False:
                #
                self.text_entry_active = None # else they didn't click on a text entry field

        if event.type == pygame_gui.UI_BUTTON_PRESSED:
            print(f"Button pressed: {event.ui_element}")
            for element in self.ui_elements:
                if isinstance(element, UIButton) and event.ui_element == element:
                    print(f"Found matching button: {element.object_id}")
                    if hasattr(element, 'option_name'):
                        option = element.option_name
                        print(f"Button has option_name: {option}")
                        
                        # Get the option type
                        options = self.screen_object.module.get_module_options()
                        if option in options:
                            option_type = options[option]['type']
                            print(f"Option type: {option_type}")
                            
                            if option_type == 'color':
                                self.show_color_picker(option)  # clicked on a button to open a color picker
                            elif option_type == 'dataship_var':
                                print("Calling show_variable_picker")
                                self.show_variable_picker(option)  # clicked on a button to open variable picker
                                return  # Return to prevent further processing
                            else:
                                self.on_checkbox_click(option)
                        else:
                            print(f"Option {option} not found in module options")
                    else:
                        print("Button does not have option_name attribute")
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
            self.on_text_submit_change(event.ui_element.option_name, event.text, event.ui_element) # send the option name and the text entered
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
        # Get the option type to handle float values correctly
        option_type = self.screen_object.module.get_module_options()[option]['type']
        
        if option_type == 'float':
            # Round to 3 decimal places for floats
            value = round(float(value), 3)
        else:
            value = int(value)
            
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
        # update the label with the new value by finding it by object_id
        for element in self.ui_elements:
            if isinstance(element, UILabel):
                if hasattr(element, 'object_id'):
                    if element.object_id == "#options_label_" + option:
                        # check if there is a details['options'] and set if there is postion in the list
                        if 'options' in options[option]:
                            # how many options are there? see if we can get the label in the options for this postion.
                            try:
                                value_str = options[option]['options'][value]
                            except:
                                value_str = str(value)
                        else:
                            # else its a float or int
                            # Format float values with 3 decimal places
                            if option_type == 'float':
                                value_str = f"{value:.3f}"
                            else:
                                value_str = str(value)
                        
                        element.set_text(options[option]['label'] + ": " + value_str)
                        break

    def on_text_submit_change(self, option, text, element):
        old_value = getattr(self.screen_object.module, option)
        option_type = self.screen_object.module.get_module_options()[option]['type']
        
        if option_type == 'tuple_int':
            #id = self.text_entry_active.object_id
            print(f"tuple_int on_text_submit_change: {option} = {text} index: {element.tuple_index}")
            # For tuple_int, we need to update just one element of the tuple
            current_value = list(getattr(self.screen_object.module, option))

            try:
                # get object_id from element
                index = element.tuple_index
                value = int(text)  # Convert to integer
                current_value[index] = value  # Update the specific tuple element
                new_value = tuple(current_value)  # Convert back to tuple
                print(f"new_value: {new_value}")
                shared.Change_history.add_change("option_change", {
                    "object": self.screen_object,
                    "option": option,
                    "old_value": old_value,
                    "new_value": new_value
                })
                
                setattr(self.screen_object.module, option, new_value)
                if hasattr(self.screen_object.module, 'update_option'):
                    self.screen_object.module.update_option(option, new_value)
            except ValueError:
                # If conversion fails, revert to old value
                element.set_text(str(old_value[index]))
        else:
            # Existing handling for other types
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

    def show_variable_picker(self, option):
        """Show dropdown menu with available Dataship variables"""
        # Get mouse position for the dropdown
        mx, my = pygame.mouse.get_pos()
        print(f"Show variable picker at {mx}, {my} for option {option}")
        self.last_dropdown_click_time = pygame.time.get_ticks()
        
        def variable_selected_callback(dropdown, id, index_path, text):
            """Handle variable selection from dropdown"""
            print(f"Variable selected: {text}")
            
            # Store the old value for change history
            old_value = getattr(self.screen_object.module, option)
            
            # Update the module with the selected variable
            shared.Change_history.add_change("option_change", {
                "object": self.screen_object,
                "option": option,
                "old_value": old_value,
                "new_value": text
            })
            
            # Set the new value
            setattr(self.screen_object.module, option, text)
            
            # Update UI to show the selected variable name
            for element in self.ui_elements:
                if isinstance(element, UIButton) and element.option_name == option:
                    element.set_text(text)
                    break
            
            # Call update_option if it exists
            if hasattr(self.screen_object.module, 'update_option'):
                self.screen_object.module.update_option(option, text)
            
            # Check for post_change_function
            options = self.screen_object.module.get_module_options()
            if 'post_change_function' in options[option]:
                post_change_function = getattr(self.screen_object.module, options[option]['post_change_function'], None)
                if post_change_function:
                    post_change_function()
        
        # Create the dropdown with all available Dataship variables
        try:
            # Get all available Dataship fields
            dataship_fields = shared.Dataship._get_all_fields()
            print(f"Available Dataship fields: {len(dataship_fields)}")
            
            # Create the dropdown and set it directly in shared
            dropdown = DropDown(
                id="dropdown_select_dataship_var",
                x=mx, y=my, w=200, h=30,
                menuTitle="Choose Variable", 
                options=dataship_fields,
                callback=variable_selected_callback
            )
            
            # These properties are essential for the dropdown to be visible and drawn
            dropdown.visible = True
            dropdown.draw_menu = True
            
            # Set storeObject with all necessary info
            dropdown.storeObject = {
                "type": "dataship_var", 
                "option": option,
                "x": mx, 
                "y": my,
                "origin": "EditOptionsBar"
            }
            
            # Set it in shared module directly
            shared.active_dropdown = dropdown
            
            print("Created dropdown and stored in shared.active_dropdown")
            
        except Exception as e:
            print(f"Error creating variable picker dropdown: {e}")
            import traceback
            traceback.print_exc()

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
                    
        # Check if there's an active dropdown in edit_mode
        try:
            from lib.common.graphic import edit_mode
            if edit_mode.active_dropdown and edit_mode.active_dropdown.visible:
                return True
        except (ImportError, AttributeError):
            pass
            
        return False
