#!/usr/bin/env python

#######################################################################################################################################
#######################################################################################################################################
# Edit mode
# Topher 2024
# while in edit mode, the user can add, move, resize, and delete screen objects
# the user can also select multiple objects and move them as a group
# This is a modified version of the play mode.  special keys are used to perform actions.
# And debug modes, frame rate, ruler, anchor grid, and help dialog are available.
#######################################################################################################################################
####################################################################################################################################### 
import os
import re
import time
from lib.common import shared
import pygame, pygame_gui
from lib import hud_utils
from lib import hud_graphics
from lib.common.graphic.edit_history import ChangeHistory, undo_last_change
from lib.common.graphic.edit_help import show_help_dialog
from lib.common.graphic.edit_clone import clone_screen_objects
from lib.common.graphic.edit_TronViewScreenObject import TronViewScreenObject
from lib.common.graphic.edit_rulers import draw_ruler
from lib.common.graphic.edit_find_module import find_module
from lib.common.graphic.edit_save_load import save_screen_to_json, load_screen_from_json
from lib.common.graphic.edit_EditToolBar import EditToolBar
from lib.common.graphic.edit_EditOptionsBar import EditOptionsBar
from lib.common.graphic.edit_TronViewScreenObject import GridAnchorManager
from lib.common.graphic.edit_EditEventsWindow import EditEventsWindow, save_event_handlers_to_json, load_event_handlers_from_json
from lib.common.graphic.edit_dropdown import DropDown
from lib.common.graphic.growl_manager import GrowlManager, GrowlPosition
from lib.common.dataship.dataship import Interface
from lib.common.graphic.edit_textinput import TextInput

#############################################
## Function: main edit loop
def main_edit_loop():

    pygamescreen, size = hud_graphics.initDisplay()

    if shared.Change_history is None:
        shared.Change_history = ChangeHistory()

    # init common things.
    maxframerate = hud_utils.readConfigInt("Main", "maxframerate", 40)
    clock = pygame.time.Clock()
    pygame.time.set_timer(pygame.USEREVENT, 1000) # fire User events ever sec.
    debug_font = pygame.font.SysFont("monospace", 25, bold=False)

    exit_edit_mode = False
    pygame.mouse.set_visible(True)
    print("Entering Edit Mode")
    shared.GrowlManager.initScreen()
    # clear screen using pygame
    pygamescreen.fill((0, 0, 0))
    pygame.display.update()
    anchor_manager = GridAnchorManager(pygamescreen, shared.smartdisplay.x_end, shared.smartdisplay.y_end)

    # if shared.CurrentScreen.ScreenObjects exists.. if it doesn't create it as array
    if not hasattr(shared.CurrentScreen, "ScreenObjects"):
        shared.CurrentScreen.ScreenObjects = []

    selected_screen_object = None
    dragging = False # are we dragging a screen object?
    offset_x = 0 # x offset for dragging
    offset_y = 0 # y offset for dragging
    resizing = False  # are we resizing?
    active_dropdown = None  # Single dropdown menu for all dropdown needs
    modulesFound, listModules = find_module(debugOutput=False)
    showAllBoundryBoxes = False
    selected_screen_objects = []
    pygame_gui_manager = pygame_gui.UIManager((shared.smartdisplay.x_end, shared.smartdisplay.y_end))
    edit_options_bar: EditOptionsBar = None
    edit_events_window: EditEventsWindow = None
    text_input: TextInput = None
    fps_font = pygame.font.SysFont("monospace", 30)
    show_ruler = False
    show_anchor_grid = False
    ruler_color = (100, 100, 100, 6)  # Light gray for non-selected objects
    selected_ruler_color = (0, 255, 0, 6)  # Green for selected objects
    help_window = None
    text_entry_active = False
    drag_start_positions = {}  # To store initial positions of dragged objects

    ############################################################################################
    ############################################################################################
    # Main edit draw loop
    while not shared.Dataship.errorFoundNeedToExit and not exit_edit_mode:
        pygamescreen.fill((0, 0, 0)) # clear screen
        event_list = pygame.event.get() # get all events
        action_performed = False  # Flag to check if an action was performed
        time_delta = clock.tick(maxframerate) / 1000.0 # get the time delta and limit the framerate.

        ## loop through events and process them
        for event in event_list:
            if text_input:      # if text input is active, process the event...
                text_input.process_event(event) 

            pygame_gui_manager.process_events(event)
            if event.type == pygame_gui.UI_BUTTON_PRESSED:
                #print("gui Button pressed: %s" % event.ui_element.text)
                if edit_options_bar:
                    edit_options_bar.handle_event(event)
                if edit_events_window:
                    edit_events_window.handle_event(event)
                action_performed = True
                continue
            if event.type == pygame_gui.UI_HORIZONTAL_SLIDER_MOVED:
                #print("gui Slider moved: %s" % event.ui_element.option_name)
                if edit_options_bar:
                    edit_options_bar.handle_event(event)
                if edit_events_window:
                    edit_events_window.handle_event(event)
                action_performed = True
                continue

            # if options bar is visible, handle the event
            if edit_options_bar:
                edit_options_bar.handle_event(event)
                text_entry_active = edit_options_bar.text_entry_active
            # if events window is visible, handle the event
            if edit_events_window:
                edit_events_window.handle_event(event)
                if edit_events_window.is_busy():
                    continue

            # check dropdown menu if visible
            # we use a global dropdown menu for some dropdown needs.
            # TODO: this needs to be refactored and cleaned up.
            if active_dropdown and active_dropdown.visible:
                selection, selected_text = active_dropdown.update(event_list)
                if selection >= 0:
                    if active_dropdown.menu_type == "module":
                        new_x = active_dropdown.storeObject["x"]
                        new_y = active_dropdown.storeObject["y"]
                        print("Adding module: %s at %d x %d" % (listModules[selection], new_x, new_y))
                        newObject = TronViewScreenObject(
                            pygamescreen, 
                            'module', 
                            f"A_{len(shared.CurrentScreen.ScreenObjects)}", 
                            module=find_module(byName=listModules[selection])[0][0],
                            x=new_x, y=new_y)
                        shared.Change_history.add_change("add", {"object": newObject})
                        shared.CurrentScreen.ScreenObjects.append(newObject)
                        newObject.selected = True
                        selected_screen_object = newObject
                        selected_screen_objects = [newObject]
                    elif active_dropdown.menu_type == "template":
                        print("Selected template: %s" % selected_text)
                        shared.Change_history.clear()
                        if selection == 0:  # First option is "CLEAR SCREEN"
                            shared.CurrentScreen.clear()
                        else:
                            load_screen_from_json(selected_text, from_templates=True)
                    elif active_dropdown.menu_type == "input":
                        print("Selected input: %s" % selected_text)
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    active_dropdown = None
            else:
                ############################################################################################
                # KEY MAPPINGS
                if event.type == pygame.KEYDOWN and not text_entry_active:
                    mods = pygame.key.get_mods()
                    if event.key == pygame.K_3 or event.key == pygame.K_KP3:
                        # do nothing
                        pass
                    elif event.key == pygame.K_q:
                        shared.Dataship.errorFoundNeedToExit = True
                    elif event.key == pygame.K_d:
                        shared.Dataship.debug_mode += 1
                        if shared.Dataship.debug_mode > 2:
                            shared.Dataship.debug_mode = 0
                        print("Debug mode: %d" % shared.Dataship.debug_mode)
                        shared.GrowlManager.add_message("Debug mode set : %d" % shared.Dataship.debug_mode)
                    elif event.key == pygame.K_ESCAPE:
                        # Unselect all selected objects
                        for sObject in shared.CurrentScreen.ScreenObjects:
                            sObject.selected = False
                        selected_screen_objects.clear()
                        if edit_options_bar:
                            edit_options_bar.remove_ui()
                            edit_options_bar = None
                        if edit_events_window:
                            edit_events_window.hide()
                        if active_dropdown:
                            active_dropdown.visible = False
                            active_dropdown = None
                        print("All objects unselected")
                    elif event.key == pygame.K_TAB:
                        # Cycle through selected objects
                        if selected_screen_objects:
                            current_index = shared.CurrentScreen.ScreenObjects.index(selected_screen_objects[-1])
                            next_index = (current_index + 1) % len(shared.CurrentScreen.ScreenObjects)
                            
                            # Unselect all objects
                            for sObject in shared.CurrentScreen.ScreenObjects:
                                sObject.selected = False
                            selected_screen_objects.clear()
                            
                            # Select the next object
                            next_object = shared.CurrentScreen.ScreenObjects[next_index]
                            next_object.selected = True
                            selected_screen_objects.append(next_object)
                            
                            # Update edit options bar
                            if edit_options_bar:
                                edit_options_bar.remove_ui()
                            edit_options_bar = EditOptionsBar(next_object, pygame_gui_manager, shared.smartdisplay)
                            
                            print(f"Tab Selected object: {next_object.title}")
                        else:
                            # If no objects are selected, select the first one
                            if shared.CurrentScreen.ScreenObjects:
                                first_object = shared.CurrentScreen.ScreenObjects[0]
                                first_object.selected = True
                                selected_screen_objects.append(first_object)
                                
                                # Create edit options bar for the first object
                                if edit_options_bar:
                                    edit_options_bar.remove_ui()
                                edit_options_bar = EditOptionsBar(first_object, pygame_gui_manager, shared.smartdisplay)
                                
                                print(f"Tab Selected first object: {first_object.title}")

                    # Exit Edit Mode
                    elif event.key == pygame.K_e:
                        shared.Dataship.interface = Interface.GRAPHIC_2D  # exit edit mode
                        exit_edit_mode = True

                    # UNGROUP a selected group
                    elif event.key == pygame.K_g and (pygame.key.get_mods() & pygame.KMOD_CTRL):
                        if selected_screen_object.type == 'group':
                            print("Ungrouping modules: %s" % [module.title for module in selected_screen_object.childScreenObjects])
                            shared.CurrentScreen.ScreenObjects.remove(selected_screen_object)
                            selected_screen_objects.clear()
                            for sObject in selected_screen_object.childScreenObjects:
                                shared.CurrentScreen.ScreenObjects.append(sObject)
                                sObject.selected = True
                                sObject.showOptions = False # hide the options bar when moving multiple objects
                                selected_screen_objects.append(sObject)
                            # remove the group from the screen objects
                            selected_screen_object = None
                    # CREATE GROUP from selected modules
                    elif event.key == pygame.K_g:
                        if len(selected_screen_objects) > 1:
                            print("Creating group with %d modules. Modules: %s" % (len(selected_screen_objects), [module.title for module in selected_screen_objects]))
                            current_group = TronViewScreenObject(pygamescreen, 'group', f"Group_{len(shared.CurrentScreen.ScreenObjects)}")
                            for sObject in selected_screen_objects:
                                sObject.selected = False
                                current_group.addChildScreenObject(sObject)
                                shared.CurrentScreen.ScreenObjects.remove(sObject) # remove from screen objects
                            current_group.selected = True # set the new group to selected
                            shared.CurrentScreen.ScreenObjects.append(current_group) # add to screen objects
                            selected_screen_objects.clear()
                            # hide the edit options bar
                            if edit_options_bar:
                                edit_options_bar.remove_ui()
                                edit_options_bar = None
                        else:
                            print("You must select multiple modules to create a group.")                            
                    # SHOW BOUNDRY BOXES
                    elif event.key == pygame.K_b:
                        showAllBoundryBoxes = not showAllBoundryBoxes
                        print("showAllBoxes: ", showAllBoundryBoxes)
                        for sObject in shared.CurrentScreen.ScreenObjects:
                            sObject.setShowBounds(showAllBoundryBoxes)

                    # DELETE SCREEN OBJECT
                    elif event.key == pygame.K_BACKSPACE or event.key == pygame.K_DELETE:
                        print("Delete key pressed")
                        # delete the selected module by going through the list of modules and removing the selected one.
                        for sObject in shared.CurrentScreen.ScreenObjects:
                            if sObject.selected:
                                shared.Change_history.add_change("delete", {"object": sObject})
                                shared.CurrentScreen.ScreenObjects.remove(sObject)
                                if edit_options_bar and edit_options_bar.screen_object == sObject:
                                    edit_options_bar.remove_ui()
                                    edit_options_bar = None
                                if edit_events_window and edit_events_window.screen_object == sObject:
                                    edit_events_window = None
                                break
                    # ADD SCREEN OBJECT.  Show the dropdown menu for adding a new module
                    elif event.key == pygame.K_a:
                        for sObject in shared.CurrentScreen.ScreenObjects:
                            sObject.selected = False
                        selected_screen_objects.clear()
                        if edit_options_bar:
                            edit_options_bar.remove_ui()
                            edit_options_bar = None
                        if edit_events_window:
                            edit_events_window.hide()

                        # first unselect all modules
                        for sObject in shared.CurrentScreen.ScreenObjects:
                            sObject.selected = False
                        selected_screen_objects.clear()
                        # Show the dropdown menu for adding a new module
                        mx, my = pygame.mouse.get_pos()
                        active_dropdown = DropDown(
                            x=mx, y=my, w=140, h=30,
                            menuTitle="Add Screen Module", options=listModules)
                        active_dropdown.menu_type = "module"  # Add type identifier
                        active_dropdown.visible = True
                        active_dropdown.draw_menu = True
                        active_dropdown.storeObject = {"type": "module", "x": mx, "y": my} # store the mouse position

                    # LOAD TEMPLATE.  Show the dropdown menu for loading a template
                    elif event.key == pygame.K_l and (pygame.key.get_mods() & pygame.KMOD_CTRL):
                        mx, my = pygame.mouse.get_pos()
                        print("Load template key pressed at %d x %d" % (mx, my))
                        active_dropdown = DropDown(
                            x=mx, y=my, w=140, h=30,
                            menuTitle="Screen Templates")
                        active_dropdown.menu_type = "template"  # Add type identifier
                        root_dir = os.path.dirname(os.path.abspath(__file__))
                        active_dropdown.load_file_dir_as_options(os.path.join(root_dir+"/../../screens", "templates"))
                        active_dropdown.insert_option("CLEAR SCREEN", 0)
                        active_dropdown.visible = True
                        active_dropdown.draw_menu = True

                    # INPUTS
                    # TODO: show inputs and let user edit them.
                    elif event.key == pygame.K_i:
                        print("Inputs key pressed")
                        mx, my = pygame.mouse.get_pos()
                        # get the list of inputs
                        options = [input.name for input in shared.Inputs.values()]
                        active_dropdown = DropDown(
                            x=mx, y=my, w=140, h=30,
                            menuTitle="Select Input", options=options)
                        active_dropdown.menu_type = "input"  # Add type identifier
                        active_dropdown.visible = True
                        active_dropdown.draw_menu = True
                        
                    # LOAD SCREEN FROM JSON
                    elif event.key == pygame.K_l:
                        load_screen_from_json("screen.json")
                        shared.GrowlManager.add_message("Loaded screen from JSON")

                    # MOVE SCREEN OBJECT UP IN DRAW ORDER (page up)
                    elif event.key == pygame.K_PAGEUP:
                        for sObject in shared.CurrentScreen.ScreenObjects:
                            if sObject.selected:
                                # move it to the bottom of the list
                                shared.CurrentScreen.ScreenObjects.remove(sObject)
                                shared.CurrentScreen.ScreenObjects.append(sObject)
                                shared.GrowlManager.add_message("Moved module to bottom of list")
                                break
                    # MOVE SCREEN OBJECT DOWN IN DRAW ORDER (page down)
                    elif event.key == pygame.K_PAGEDOWN:
                        for sObject in shared.CurrentScreen.ScreenObjects:
                            if sObject.selected:
                                # move it to the top of the list
                                shared.CurrentScreen.ScreenObjects.remove(sObject)
                                shared.CurrentScreen.ScreenObjects.insert(0, sObject)
                                shared.GrowlManager.add_message("Moved module to top of list")
                                break

                    # SAVE SCREEN TO JSON
                    elif event.key == pygame.K_s:
                        # check if the screen has a filename
                        if shared.CurrentScreen.filename is None or shared.CurrentScreen.filename == "":
                            def handle_save_filename(filename,result):
                                """Handle saving the screen when user enters filename in text input dialog"""
                                if result == "OK":
                                    save_screen_to_json(filename)
                                    shared.GrowlManager.add_message("Saved: %s" % filename)
                                elif result == "CANCEL":
                                    shared.GrowlManager.add_message("Cancelled")

                                nonlocal text_input, text_entry_active
                                text_input.kill()
                                text_input = None
                                text_entry_active = False

                            if shared.CurrentScreen.loaded_from_template is not None:
                                filenameToUse = shared.CurrentScreen.loaded_from_template
                            else:
                                filenameToUse = "" # default filename to use for new screens?

                            # show a dialog using edit_textinput.py
                            text_entry_active = True
                            text_input = TextInput(manager=pygame_gui_manager,
                                                 x=None, y=None, width=200, height=50, 
                                                 with_background=True,
                                                 dark_background=True,
                                                 initial_text=filenameToUse,
                                                 label_text="Enter filename",
                                                 button_text="Save",
                                                 button_action=handle_save_filename)
                            
                            # delay a bit to allow the text entry to be created

                            continue
                        else:
                            save_screen_to_json(shared.CurrentScreen.filename)
                            shared.GrowlManager.add_message("Saved: %s" % shared.CurrentScreen.filename)

                    # Toggle FPS display when 'F' is pressed
                    elif event.key == pygame.K_f:
                        shared.CurrentScreen.show_FPS = not shared.CurrentScreen.show_FPS

                    # Toggle ruler when 'R' is pressed
                    elif event.key == pygame.K_r:
                        if(not show_ruler and not show_anchor_grid):
                            show_ruler = True
                        elif(show_ruler and not show_anchor_grid):
                            show_ruler = False
                            show_anchor_grid = True
                        elif(not show_ruler and show_anchor_grid):
                            show_anchor_grid = False

                    # Move selected screen object with arrow keys
                    elif event.key in [pygame.K_UP, pygame.K_DOWN, pygame.K_LEFT, pygame.K_RIGHT]:
                        move_distance = 10 if pygame.key.get_mods() & pygame.KMOD_CTRL else 1
                        for sObject in shared.CurrentScreen.ScreenObjects:
                            if sObject.selected:
                                if event.key == pygame.K_UP:
                                    sObject.move(sObject.x, sObject.y - move_distance)
                                elif event.key == pygame.K_DOWN:
                                    sObject.move(sObject.x, sObject.y + move_distance)
                                elif event.key == pygame.K_LEFT:
                                    sObject.move(sObject.x - move_distance, sObject.y)
                                elif event.key == pygame.K_RIGHT:
                                    sObject.move(sObject.x + move_distance, sObject.y)
                                
                                # Update EditOptionsBar position if it exists
                                if edit_options_bar and edit_options_bar.screen_object == sObject:
                                    edit_options_bar.update_position()
                                if edit_events_window and edit_events_window.screen_object == sObject:
                                    edit_events_window.update_position()

                    # Show help dialog when '?' is pressed
                    elif event.key == pygame.K_QUESTION or event.key == pygame.K_SLASH:
                        print("Help key pressed")
                        if help_window is None:
                            help_window = show_help_dialog(pygame_gui_manager)
                        else:
                            help_window.kill()
                            help_window = None

                    # Clone selected screen objects
                    elif event.key == pygame.K_c:
                        mx, my = pygame.mouse.get_pos()
                        cloned_objects = clone_screen_objects(selected_screen_objects, mx, my)
                        
                        if cloned_objects:
                            for cloned_obj in cloned_objects:
                                shared.CurrentScreen.ScreenObjects.append(cloned_obj)
                            
                            # Update selected objects to be the cloned ones
                            selected_screen_objects = cloned_objects
                            for obj in shared.CurrentScreen.ScreenObjects:
                                obj.selected = obj in cloned_objects
                                # hide the edit options bar
                                if edit_options_bar and edit_options_bar.screen_object == obj:
                                    edit_options_bar.remove_ui()
                                    edit_options_bar = None
                            
                            # add the cloned objects to the change history
                            shared.Change_history.add_change("add", {"object": cloned_objects})

                        print(f"Cloned {len(cloned_objects)} objects")

                    # Undo functionality
                    elif event.key == pygame.K_z and (mods & pygame.KMOD_CTRL):
                        undo_last_change(shared.Change_history, shared)
                
                # check for joystick events
                if event.type == pygame.JOYBUTTONDOWN or event.type == pygame.JOYBUTTONUP:
                    print("Joystick event: %s" % pygame.event.event_name(event.type))

                if event.type == pygame.JOYDEVICEADDED:
                    # This event will be generated when the program starts for every
                    # joystick, filling up the list without needing to create them manually.
                    joy = pygame.joystick.Joystick(event.device_index)
                    # look if there is any gyro_joystick in the list
                    for index, inputObj in shared.Inputs.items():
                        print("inputObj: %s" % inputObj.name)
                        if inputObj.name == "imuJoystick":
                            inputObj.setJoystick(joy)
                            shared.GrowlManager.add_message("IMU Joystick connected")
                            break

                # check for Mouse events
                if event.type == pygame.MOUSEBUTTONDOWN or event.type == pygame.FINGERDOWN:
                    if event.type == pygame.FINGERDOWN:
                        mx, my =  event.x, event.y
                    else:
                        mx, my = pygame.mouse.get_pos()
                    if shared.Dataship.debug_mode > 0:
                        print("Click %d x %d" % (mx, my))
                    
                    # Check for GUI interactions first
                    gui_handled = False
                    
                    # Check for EditOptionsBar interactions
                    if edit_options_bar and edit_options_bar.visible:
                        if edit_options_bar.is_busy():  # is it busy with a color picker (or something else..)
                            gui_handled = True
                        elif edit_options_bar.window.get_abs_rect().collidepoint(mx, my):
                            gui_handled = True
                    # Check for EditEventsWindow interactions
                    if edit_events_window and edit_events_window.visible:
                        if edit_events_window.is_busy():  # is it busy with a color picker (or something else..)
                            gui_handled = True
                        elif edit_events_window.window.get_abs_rect().collidepoint(mx, my):
                            gui_handled = True

                    # Check for help window interactions
                    if help_window and help_window.get_abs_rect().collidepoint(mx, my):
                        gui_handled = True
                    
                    # Handle EditToolBar clicks for selected objects
                    if not gui_handled:
                        for sObject in shared.CurrentScreen.ScreenObjects:
                            if sObject.selected:
                                action = sObject.edit_toolbar.handle_click((mx, my))
                                if action:
                                    gui_handled = True
                                    if action == "delete":
                                        shared.CurrentScreen.ScreenObjects.remove(sObject)
                                    elif action == "move_down":
                                        shared.CurrentScreen.ScreenObjects.remove(sObject)
                                        shared.CurrentScreen.ScreenObjects.insert(0, sObject)
                                        shared.GrowlManager.add_message("Moved to back: %s" % sObject.title)
                                    elif action == "move_up":
                                        # move to the front
                                        shared.CurrentScreen.ScreenObjects.remove(sObject)
                                        shared.CurrentScreen.ScreenObjects.append(sObject)
                                        shared.GrowlManager.add_message("Moved to front: %s" % sObject.title)
                                    elif action == "center":
                                        shared.Change_history.add_change("move", {"object": sObject, "old_pos": (sObject.x, sObject.y), "new_pos": sObject.center()})
                                        sObject.center()
                                        shared.GrowlManager.add_message("Centered: %s" % sObject.title)
                                    elif action == "align_left":
                                        sObject.align_left()
                                    elif action == "align_right":
                                        sObject.align_right()
                                    elif action == "edit_options":
                                        sObject.showOptions = not sObject.showOptions
                                        if sObject.showOptions:
                                            sObject.showEvents = False
                                    elif action == "edit_events":
                                        sObject.showEvents = not sObject.showEvents
                                        if sObject.showEvents:
                                            sObject.showOptions = False
                                    break  # Stop checking other objects if action performed
                    
                    # If no GUI item was clicked, handle screen object selection
                    if not gui_handled:
                        # Check if Shift is held down
                        shift_held = pygame.key.get_mods() & pygame.KMOD_SHIFT

                        atLeastOneSelectedObjectIsClicked = False
                        if not shift_held:
                            # are we clicking on a selected object?
                            for sObject in shared.CurrentScreen.ScreenObjects:
                                if sObject.selected:
                                    if sObject.x <= mx <= sObject.x + sObject.width and sObject.y <= my <= sObject.y + sObject.height:
                                        atLeastOneSelectedObjectIsClicked = True
                            if not atLeastOneSelectedObjectIsClicked:
                                selected_screen_objects.clear()
                                # deselect all modules (unselect all)
                                for sObject in shared.CurrentScreen.ScreenObjects:
                                    sObject.selected = False
                                if edit_options_bar:
                                    edit_options_bar.remove_ui() # remove the edit options bar
                                    edit_options_bar = None # set it to None
                                if edit_events_window:
                                    edit_events_window.hide()
                                    edit_events_window = None

                        # Check if the mouse click is inside any screenObject (check from the top down)
                        for sObject in shared.CurrentScreen.ScreenObjects[::-1]:
                            if sObject.x <= mx <= sObject.x + sObject.width and sObject.y <= my <= sObject.y + sObject.height:
                                if shift_held:
                                    if sObject not in selected_screen_objects:
                                        selected_screen_objects.append(sObject)
                                        sObject.selected = True
                                        if shared.Dataship.debug_mode > 0:
                                            print("Selected module: %s (shift) current modules: %d" % (sObject.title, len(selected_screen_objects)))
                                    # update the mouse offset for all selected modules
                                    for sObject in selected_screen_objects:
                                        sObject.mouse_offset_x = mx - sObject.x
                                        sObject.mouse_offset_y = my - sObject.y
                                        sObject.showOptions = False # hide the options bar when moving multiple objects
                                else:
                                    if len(selected_screen_objects) > 1 and atLeastOneSelectedObjectIsClicked:
                                        if shared.Dataship.debug_mode > 0:
                                            print("Multiple modules selected, updating mouse offsets (moving objects)")
                                        for sObject in selected_screen_objects:
                                            sObject.mouse_offset_x = mx - sObject.x
                                            sObject.mouse_offset_y = my - sObject.y
                                    else:
                                        # unselect all other modules
                                        for unSelectObj in shared.CurrentScreen.ScreenObjects:
                                            unSelectObj.selected = False

                                        selected_screen_objects = [sObject]
                                        sObject.selected = True
                                        if shared.Dataship.debug_mode > 0:
                                            print("Selected module: %s" % sObject.title)
                                #################
                                # RESIZE MODULE
                                if mx >= sObject.x + sObject.width - 10 and my >= sObject.y + sObject.height - 10 and mx <= sObject.x + sObject.width and my <= sObject.y + sObject.height:
                                    # Click is in the bottom right corner, start resizing
                                    selected_screen_object = sObject
                                    sObject.selected = True
                                    resizing = True
                                    resize_start_size = (sObject.width, sObject.height)  # Store initial size
                                    offset_x = mx - sObject.x
                                    offset_y = my - sObject.y
                                    dropdown_add_new_module = None
                                ##################
                                # DROPDOWN MENU (select module) top right corner
                                elif sObject.y <= my <= sObject.y + 20 and (sObject.module is None) and sObject.type == 'module':  # Assuming the title area is 20 pixels high
                                    # only if module is not a group or has no module
                                    selected_screen_object = sObject
                                    sObject.selected = True
                                    dropdown_add_new_module = DropDown(
                                        x=sObject.x, y=sObject.y, w=140, h=30, 
                                        font=pygame.font.SysFont(None, 25), 
                                        main="Select Module", options=listModules)
                                    dropdown_add_new_module.visible = True
                                    dropdown_add_new_module.draw_menu = True
                                ##################
                                # MOVE MODULE
                                else:
                                    dropdown_add_new_module = None
                                    # Click is inside the module, start moving
                                    selected_screen_object = sObject
                                    dragging = True
                                    offset_x = mx - sObject.x 
                                    offset_y = my - sObject.y
                                    sObject.selected = True
                                    # Store initial positions when starting to drag
                                    if dragging:
                                        drag_start_positions = {obj: (obj.x, obj.y) for obj in selected_screen_objects}
                                break

                # Mouse button up
                elif event.type == pygame.MOUSEBUTTONUP or event.type == pygame.FINGERUP:
                    if dragging:
                        moves = handle_drag_end(selected_screen_objects, drag_start_positions)
                        drag_start_positions.clear()
                        if moves > 0:
                            #print("Dragging end, %d moves happened" % moves)
                            pass
                        else: # send the click event to the screen object. translate the mouse position to the screen object.
                            for sObject in selected_screen_objects:
                                sObject.click(shared.Dataship, mx - sObject.x, my - sObject.y)
                    elif resizing and selected_screen_object:
                        if shared.Dataship.debug_mode > 0:
                            print("Resizing end")
                        handle_resize_end(selected_screen_object, resize_start_size)
                    dragging = False
                    resizing = False
                    #print("Mouse Up")

                # Mouse move.. resize or move the module??
                elif event.type == pygame.MOUSEMOTION or event.type == pygame.FINGERMOTION:
                    if event.type == pygame.FINGERMOTION:
                        print("Finger motion: %d x %d , %d x %d" % (event.x, event.y, event.dx, event.dy))
                        # print all atrribs of event object
                        for attr in dir(event):
                            print("obj.%s = %r" % (attr, getattr(event, attr)))
                        mx, my = event.x, event.y
                    else:
                        mx, my = pygame.mouse.get_pos()
                    if dragging and len(selected_screen_objects) == 1:  # if dragging a single screen object
                        selected_screen_objects[0].move(mx - offset_x, my - offset_y)
                        # Update EditOptionsBar position if it exists
                        if edit_options_bar and edit_options_bar.screen_object == selected_screen_objects[0]:
                            edit_options_bar.update_position()
                    
                    elif dragging and len(selected_screen_objects) > 1:  # if dragging multiple screen objects
                        # move all children of the selected screen objects
                        for sObject in selected_screen_objects:
                            # get the difference in x and y from the current position to the new position
                            diffX = mx - sObject.mouse_offset_x
                            diffY = my - sObject.mouse_offset_y
                            #print("Moving %s by %d, %d " % (sObject.title, diffX, diffY))
                            sObject.move(diffX, diffY)
                            # Update EditOptionsBar position if it exists
                            if edit_options_bar and edit_options_bar.screen_object == sObject:
                                edit_options_bar.update_position()
                        pygamescreen.fill((0, 0, 0)) # fill the screen with black to clear the screen
                    elif dragging and selected_screen_object:  # dragging a single screen object
                        selected_screen_object.move(mx, my)
                        # Update EditOptionsBar position if it exists
                        if edit_options_bar and edit_options_bar.screen_object == selected_screen_object:
                            edit_options_bar.update_position()
                    elif resizing and selected_screen_object: # resizing a single screen object
                        temp_width = mx - selected_screen_object.x
                        temp_height = my - selected_screen_object.y
                        selected_screen_object.resize(temp_width, temp_height)
                        pygamescreen.fill((0, 0, 0))

        if action_performed:
            continue  # Skip the rest of the loop and start over (which will trigger the draw)

        # Draw the modules
        for sObject in shared.CurrentScreen.ScreenObjects:
            # if multiple objects are selected, don't show the toolbar or if shift is held (shift is for multiple selection)
            shift_held = pygame.key.get_mods() & pygame.KMOD_SHIFT
            shouldDrawToolbar = not len(selected_screen_objects) > 1 and not shift_held
            sObject.draw(shared.Dataship, shared.smartdisplay, shouldDrawToolbar)

            # draw Options Bar?
            if sObject.selected and sObject.showOptions:
                if edit_options_bar is None or edit_options_bar.screen_object != sObject:
                    if edit_options_bar:
                        edit_options_bar.remove_ui()
                    edit_options_bar = EditOptionsBar(sObject, pygame_gui_manager, shared.smartdisplay)
                edit_options_bar.update(time_delta)
            elif edit_options_bar and edit_options_bar.screen_object == sObject and not sObject.showOptions:
                edit_options_bar.remove_ui()
                edit_options_bar = None
            
            # draw Events Window?
            if sObject.selected and sObject.showEvents:
                if edit_events_window is None or edit_events_window.screen_object != sObject:
                    if edit_events_window:
                        edit_events_window.hide()
                    edit_events_window = EditEventsWindow(sObject, pygame_gui_manager, shared.smartdisplay)
                edit_events_window.update(time_delta)
            elif edit_events_window and edit_events_window.screen_object == sObject and not sObject.showEvents:
                edit_events_window.hide()
                edit_events_window = None


        pygame_gui_manager.update(time_delta)

        # Draw FPS if enabled
        if shared.CurrentScreen.show_FPS:
            fps = clock.get_fps()
            fps_text = fps_font.render(f"FPS: {fps:.2f}", True, (255, 255, 255), (0, 0, 0, 0), pygame.SRCALPHA)
            fps_rect = fps_text.get_rect(topright=(shared.smartdisplay.x_end - 10, 10))
            pygamescreen.blit(fps_text, fps_rect)

            # Add total draw time for all modules
            total_draw_time = sum(getattr(obj, 'draw_time', 0) for obj in shared.CurrentScreen.ScreenObjects)
            total_time_text = f"DrawTime: {total_draw_time:.2f}ms" # show time in ms
            total_time_surface = fps_font.render(total_time_text, True, (255, 255, 255), (0, 0, 0, 0))
            total_time_rect = total_time_surface.get_rect(topright=(shared.smartdisplay.x_end - 10, 40))
            pygamescreen.blit(total_time_surface, total_time_rect)

        # Draw ruler if enabled
        if show_ruler:
            draw_ruler(pygamescreen, shared.CurrentScreen.ScreenObjects, ruler_color, selected_ruler_color)

        # Draw anchor points if enabled
        if show_anchor_grid:
            anchor_manager.anchor_draw(selected_screen_objects)

        #Draw the dropdown menu if visible over the top of everything.
        if active_dropdown and active_dropdown.visible:
            # Create a semi-transparent overlay
            screen_width = shared.smartdisplay.x_end
            screen_height = shared.smartdisplay.y_end
            overlay = pygame.Surface((screen_width, screen_height))
            overlay.fill((0, 0, 0))  # Black background
            overlay.set_alpha(200)    # 50% transparency (0-255)
            pygamescreen.blit(overlay, (0, 0))            
            active_dropdown.draw(pygamescreen)
        else:
            # if event details window is visible, create a semi transparent overlay
            if (edit_events_window and edit_events_window.details_window) or \
                (text_input and text_input.visible):
                # create a semi transparent overlay
                screen_width = shared.smartdisplay.x_end
                screen_height = shared.smartdisplay.y_end
                overlay = pygame.Surface((screen_width, screen_height))
                overlay.fill((0,0,0))
                overlay.set_alpha(200)
                pygamescreen.blit(overlay, (0,0))

            # give some draw time to the gui manager
            pygame_gui_manager.draw_ui(pygamescreen)

        # Draw Growl messages
        shared.GrowlManager.draw(pygamescreen)

        # Draw dashed border for edit mode
        dash_length = 20
        border_colors = [(150, 150, 0), (100, 0, 0)]  # Yellow and White
        screen_width = shared.smartdisplay.x_end
        screen_height = shared.smartdisplay.y_end
        
        # Draw dashed border
        for i in range(0, screen_width, dash_length * 2):
            # Top border
            color_index = (i // (dash_length * 2)) % 2
            pygame.draw.line(pygamescreen, border_colors[color_index], (i, 0), 
                           (min(i + dash_length, screen_width), 0), 5)
            # Bottom border
            pygame.draw.line(pygamescreen, border_colors[color_index], (i, screen_height-1), 
                           (min(i + dash_length, screen_width), screen_height-1), 5)
        
        for i in range(0, screen_height, dash_length * 2):
            # Left border
            color_index = (i // (dash_length * 2)) % 2
            pygame.draw.line(pygamescreen, border_colors[color_index], (0, i), 
                           (0, min(i + dash_length, screen_height)), 5)
            # Right border
            pygame.draw.line(pygamescreen, border_colors[color_index], (screen_width-1, i), 
                           (screen_width-1, min(i + dash_length, screen_height)), 5)

        # Draw "Edit Mode" text with background
        edit_mode_font = pygame.font.SysFont("monospace", 40, bold=True)
        edit_mode_text = edit_mode_font.render("Edit Mode", True, (255, 255, 0))  # Yellow text
        text_rect = edit_mode_text.get_rect(bottomright=(screen_width - 20, screen_height - 20))
        
        # Draw a semi-transparent background behind the text
        background_rect = text_rect.inflate(20, 10)  # Make background slightly larger than text
        background_surface = pygame.Surface((background_rect.width, background_rect.height))
        background_surface.fill((0, 0, 0))
        background_surface.set_alpha(128)  # Semi-transparent
        pygamescreen.blit(background_surface, background_rect)
        
        # Draw the text
        pygamescreen.blit(edit_mode_text, text_rect)

        # now make pygame update display.
        pygame.display.update()

    get_ready_to_exit_edit_mode()

def handle_drag_end(selected_objects, start_positions):
    movesHappened = 0
    for obj in selected_objects:
        start_pos = start_positions.get(obj)
        if start_pos and (obj.x, obj.y) != start_pos:
            movesHappened += 1
            shared.Change_history.add_change("move", {
                "object": obj,
                "old_pos": start_pos,
                "new_pos": (obj.x, obj.y)
            })
    return movesHappened

def handle_resize_end(screen_object, start_size):
    if (screen_object.width, screen_object.height) != start_size:
        shared.Change_history.add_change("resize", {
            "object": screen_object,
            "old_size": start_size,
            "new_size": (screen_object.width, screen_object.height)
        })

def get_ready_to_exit_edit_mode():
    # go through all screen objects and turn off box selection
    for sObject in shared.CurrentScreen.ScreenObjects:
        sObject.selected = False
        sObject.showBounds = False

    # turn off the edit mode
    shared.Dataship.interface = Interface.GRAPHIC_2D
    shared.CurrentScreen.show_FPS = False # turn off showing FPS

    return True

# vi: modeline tabstop=8 expandtab shiftwidth=4 softtabstop=4 syntax=python


