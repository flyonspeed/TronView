#!/usr/bin/env python

#######################################################################################################################################
#######################################################################################################################################
# edit mode
#
import random
import string
from lib.common import shared

import argparse, pygame
import time
from lib import hud_graphics
from lib import hud_utils
from lib import hud_text
from lib import aircraft
from lib import smartdisplay
from lib.util.virtualKeyboard import VirtualKeyboard
from lib.util import drawTimer
from lib.modules._module import Module
import os
import importlib
from lib.modules.efis.trafficscope import trafficscope
import json
from datetime import datetime
import pygame_gui
from pygame_gui.elements import UIButton, UILabel, UITextEntryLine, UIDropDownMenu
from pygame_gui.elements.ui_window import UIWindow
from pygame_gui.elements import UITextBox
from pygame_gui.windows import UIColourPickerDialog
from collections import deque
import inspect

# Add this near the top of the file, after the imports
global show_fps
show_fps = False

#############################################
## Function: main edit loop
def main_edit_loop():
    global debug_font
    global show_fps

    if shared.Change_history is None:
        shared.Change_history = ChangeHistory()

    # init common things.
    maxframerate = hud_utils.readConfigInt("Main", "maxframerate", 30)
    clock = pygame.time.Clock()
    pygame.time.set_timer(pygame.USEREVENT, 1000) # fire User events ever sec.
    debug_mode = 0
    debug_font = pygame.font.SysFont("monospace", 25, bold=False)

    exit_edit_mode = False
    pygame.mouse.set_visible(True)
    print("Entering Edit Mode")

    # clear screen using pygame
    pygamescreen = pygame.display.set_mode((shared.smartdisplay.x_end, shared.smartdisplay.y_end))
    pygamescreen.fill((0, 0, 0))
    pygame.display.update()

    # if shared.CurrentScreen.ScreenObjects exists.. if it doesn't create it as array
    if not hasattr(shared.CurrentScreen, "ScreenObjects"):
        shared.CurrentScreen.ScreenObjects = []

    selected_screen_object = None
    dragging = False # are we dragging a screen object?
    offset_x = 0 # x offset for dragging
    offset_y = 0 # y offset for dragging
    resizing = False  # are we resizing?
    dropdown = None # dropdown menu for module selection (if any)
    modulesFound, listModules = find_module(debugOutput=True)
    showAllBoundryBoxes = False

    selected_screen_objects = []

    pygame_gui_manager = pygame_gui.UIManager((shared.smartdisplay.x_end, shared.smartdisplay.y_end))
    edit_options_bar = None

    show_fps = False
    fps_font = pygame.font.SysFont("monospace", 30)

    show_ruler = False
    ruler_color = (100, 100, 100)  # Light gray for non-selected objects
    selected_ruler_color = (0, 255, 0)  # Green for selected objects

    help_window = None

    text_entry_active = False

    drag_start_positions = {}  # To store initial positions of dragged objects

    ############################################################################################
    ############################################################################################
    # Main edit draw loop
    while not shared.aircraft.errorFoundNeedToExit and not exit_edit_mode:
        clock.tick(maxframerate)
        pygamescreen.fill((0, 0, 0)) # clear screen
        event_list = pygame.event.get() # get all events
        action_performed = False  # Flag to check if an action was performed
        time_delta = clock.tick(maxframerate) / 1000.0

        for event in event_list:
            pygame_gui_manager.process_events(event)
            if event.type == pygame_gui.UI_BUTTON_PRESSED:
                #print("gui Button pressed: %s" % event.ui_element.text)
                if edit_options_bar:
                    edit_options_bar.handle_event(event)
                action_performed = True
                continue
            if event.type == pygame_gui.UI_HORIZONTAL_SLIDER_MOVED:
                #print("gui Slider moved: %s" % event.ui_element.option_name)
                if edit_options_bar:
                    edit_options_bar.handle_event(event)
                action_performed = True
                continue

            if edit_options_bar:
                edit_options_bar.handle_event(event)
                text_entry_active = edit_options_bar.text_entry_active

            if dropdown and dropdown.visible:
                selection = dropdown.update(event_list)
                if selection >= 0:
                    print("Selected module: %s" % listModules[selection])
                    selected_screen_object.title = listModules[selection]
                    newModules, titles  = find_module(listModules[selection])
                    selected_screen_object.setModule(newModules[0])
            else:
                # KEY MAPPINGS
                if event.type == pygame.KEYDOWN and not text_entry_active:
                    mods = pygame.key.get_mods()
                    if event.key == pygame.K_3 or event.key == pygame.K_KP3:
                        # do nothing
                        pass
                    elif event.key == pygame.K_q:
                        shared.aircraft.errorFoundNeedToExit = True
                    elif event.key == pygame.K_ESCAPE:
                        # Unselect all selected objects
                        for sObject in shared.CurrentScreen.ScreenObjects:
                            sObject.selected = False
                        selected_screen_objects.clear()
                        if edit_options_bar:
                            edit_options_bar.remove_ui()
                            edit_options_bar = None
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
                        shared.aircraft.editMode = False  # exit edit mode
                        exit_edit_mode = True

                    # UNGROUP
                    elif event.key == pygame.K_g and (pygame.key.get_mods() & pygame.KMOD_CTRL):
                        if selected_screen_object.type == 'group':
                            print("Ungrouping modules: %s" % [module.title for module in selected_screen_object.childScreenObjects])
                            shared.CurrentScreen.ScreenObjects.remove(selected_screen_object)
                            for sObject in selected_screen_object.childScreenObjects:
                                shared.CurrentScreen.ScreenObjects.append(sObject)
                                sObject.selected = False
                    # CREATE GROUP
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
                                break
                    # ADD SCREEN OBJECT
                    elif event.key == pygame.K_a:
                        # first unselect all modules
                        for sObject in shared.CurrentScreen.ScreenObjects:
                            sObject.selected = False
                        selected_screen_objects.clear()
                        # add a new Screen object
                        mx, my = pygame.mouse.get_pos()
                        newObject = TronViewScreenObject(pygamescreen, 'module', f"A_{len(shared.CurrentScreen.ScreenObjects)}", module=None, x=mx, y=my)
                        shared.Change_history.add_change("add", {"object": newObject})
                        shared.CurrentScreen.ScreenObjects.append(
                            newObject
                        )
                        newObject.selected = True
                        selected_screen_object = newObject
                        dropdown = DropDown([COLOR_INACTIVE, COLOR_ACTIVE],
                                [COLOR_LIST_INACTIVE, COLOR_LIST_ACTIVE], 
                            newObject.x, newObject.y, 140, 30, 
                            pygame.font.SysFont(None, 25), 
                            "Select Module", listModules)
                        dropdown.visible = True
                        dropdown.draw_menu = True

                    # MOVE SCREEN OBJECT UP IN DRAW ORDER (page up)
                    elif event.key == pygame.K_PAGEUP:
                        for sObject in shared.CurrentScreen.ScreenObjects:
                            if sObject.selected:
                                # move it to the bottom of the list
                                shared.CurrentScreen.ScreenObjects.remove(sObject)
                                shared.CurrentScreen.ScreenObjects.append(sObject)

                                break
                    # MOVE SCREEN OBJECT DOWN IN DRAW ORDER (page down)
                    elif event.key == pygame.K_PAGEDOWN:
                        for sObject in shared.CurrentScreen.ScreenObjects:
                            if sObject.selected:
                                # move it to the top of the list
                                shared.CurrentScreen.ScreenObjects.remove(sObject)
                                shared.CurrentScreen.ScreenObjects.insert(0, sObject)
                                break

                    # SAVE SCREEN TO JSON
                    elif event.key == pygame.K_s:
                        save_screen_to_json()

                    # LOAD SCREEN FROM JSON
                    elif event.key == pygame.K_l:
                        load_screen_from_json("screen.json")

                    # Toggle FPS display when 'F' is pressed
                    elif event.key == pygame.K_f:
                        show_fps = not show_fps
                        TronViewScreenObject.show_fps = show_fps

                    # Toggle ruler when 'R' is pressed
                    elif event.key == pygame.K_r:
                        show_ruler = not show_ruler

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

                        print(f"Cloned {len(cloned_objects)} objects")

                    # Undo functionality
                    elif event.key == pygame.K_z and (mods & pygame.KMOD_CTRL):
                        undo_last_change(shared.Change_history)

                    # List aircraft fields
                    elif event.key == pygame.K_i:  # 'i' for 'info'
                        print("Aircraft fields:")
                        list_aircraft_fields()

                # check for Mouse events
                if event.type == pygame.MOUSEBUTTONDOWN:
                    mx, my = pygame.mouse.get_pos()
                    print("Mouse Click %d x %d" % (mx, my))
                    
                    # Check for GUI interactions first
                    gui_handled = False
                    
                    # Check for EditOptionsBar interactions
                    if edit_options_bar and edit_options_bar.visible:
                        if edit_options_bar.is_busy():  # is it busy with a color picker (or something else..)
                            gui_handled = True
                        elif edit_options_bar.window.get_abs_rect().collidepoint(mx, my):
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
                                    elif action == "move_up":
                                        index = shared.CurrentScreen.ScreenObjects.index(sObject)
                                        if index < len(shared.CurrentScreen.ScreenObjects) - 1:
                                            shared.CurrentScreen.ScreenObjects[index], shared.CurrentScreen.ScreenObjects[index+1] = shared.CurrentScreen.ScreenObjects[index+1], shared.CurrentScreen.ScreenObjects[index]
                                    elif action == "move_down":
                                        index = shared.CurrentScreen.ScreenObjects.index(sObject)
                                        if index > 0:
                                            shared.CurrentScreen.ScreenObjects[index], shared.CurrentScreen.ScreenObjects[index-1] = shared.CurrentScreen.ScreenObjects[index-1], shared.CurrentScreen.ScreenObjects[index]
                                    elif action == "center":
                                        sObject.center()
                                    elif action == "align_left":
                                        sObject.align_left()
                                    elif action == "align_right":
                                        sObject.align_right()
                                    elif action == "edit_options":
                                        sObject.showOptions = not sObject.showOptions
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

                        # Check if the mouse click is inside any screenObject (check from the top down)
                        for sObject in shared.CurrentScreen.ScreenObjects[::-1]:
                            if sObject.x <= mx <= sObject.x + sObject.width and sObject.y <= my <= sObject.y + sObject.height:
                                if shift_held:
                                    if sObject not in selected_screen_objects:
                                        selected_screen_objects.append(sObject)
                                        sObject.selected = True
                                        print("Selected module: %s (shift) current modules: %d" % (sObject.title, len(selected_screen_objects)))
                                    # update the mouse offset for all selected modules
                                    for sObject in selected_screen_objects:
                                        sObject.mouse_offset_x = mx - sObject.x
                                        sObject.mouse_offset_y = my - sObject.y
                                else:
                                    if len(selected_screen_objects) > 1 and atLeastOneSelectedObjectIsClicked:
                                        for sObject in selected_screen_objects:
                                            sObject.mouse_offset_x = mx - sObject.x
                                            sObject.mouse_offset_y = my - sObject.y
                                    else:
                                        selected_screen_objects = [sObject]
                                        sObject.selected = True
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
                                    dropdown = None
                                ##################
                                # DROPDOWN MENU (select module) top right corner
                                elif sObject.y <= my <= sObject.y + 20 and (sObject.module is None) and sObject.type == 'module':  # Assuming the title area is 20 pixels high
                                    # only if module is not a group or has no module
                                    selected_screen_object = sObject
                                    sObject.selected = True
                                    dropdown = DropDown([COLOR_INACTIVE, COLOR_ACTIVE],
                                            [COLOR_LIST_INACTIVE, COLOR_LIST_ACTIVE], 
                                        sObject.x, sObject.y, 140, 30, 
                                        pygame.font.SysFont(None, 25), 
                                        "Select Module", listModules)
                                    dropdown.visible = True
                                    dropdown.draw_menu = True
                                ##################
                                # MOVE MODULE
                                else:
                                    dropdown = None
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

                # Mouse up
                elif event.type == pygame.MOUSEBUTTONUP:
                    if dragging:
                        handle_drag_end(selected_screen_objects, drag_start_positions)
                        drag_start_positions.clear()
                    if resizing and selected_screen_object:
                        handle_resize_end(selected_screen_object, resize_start_size)
                    dragging = False
                    resizing = False
                    #print("Mouse Up")

                # Mouse move.. resize or move the module??
                elif event.type == pygame.MOUSEMOTION:
                    if dragging and len(selected_screen_objects) == 1:  # if dragging a single screen object
                        mx, my = pygame.mouse.get_pos()
                        selected_screen_objects[0].move(mx - offset_x, my - offset_y)
                        # Update EditOptionsBar position if it exists
                        if edit_options_bar and edit_options_bar.screen_object == selected_screen_objects[0]:
                            edit_options_bar.update_position()
                    
                    elif dragging and len(selected_screen_objects) > 1:  # if dragging multiple screen objects
                        mx, my = pygame.mouse.get_pos()
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

                        pygamescreen.fill((0, 0, 0))
                    elif dragging and selected_screen_object:  # dragging a single screen object
                        mx, my = pygame.mouse.get_pos()
                        selected_screen_object.move(mx, my)
                        # Update EditOptionsBar position if it exists
                        if edit_options_bar and edit_options_bar.screen_object == selected_screen_object:
                            edit_options_bar.update_position()
                    elif resizing and selected_screen_object: # resizing
                        mx, my = pygame.mouse.get_pos()
                        temp_width = mx - selected_screen_object.x
                        temp_height = my - selected_screen_object.y
                        if temp_width < 40: temp_width = 40  # limit minimum size
                        if temp_height < 40: temp_height = 40
                        selected_screen_object.resize(temp_width, temp_height)
                        pygamescreen.fill((0, 0, 0))

        if action_performed:
            continue  # Skip the rest of the loop and start over (which will trigger the draw)

        # Draw the modules
        for sObject in shared.CurrentScreen.ScreenObjects:
            sObject.draw(shared.aircraft, shared.smartdisplay)

            if sObject.selected and sObject.showOptions:
                if edit_options_bar is None or edit_options_bar.screen_object != sObject:
                    if edit_options_bar:
                        edit_options_bar.remove_ui()
                    edit_options_bar = EditOptionsBar(sObject, pygame_gui_manager, shared.smartdisplay)
                edit_options_bar.update(time_delta)
            elif edit_options_bar and edit_options_bar.screen_object == sObject and not sObject.showOptions:
                edit_options_bar.remove_ui()
                edit_options_bar = None

            # Last... Draw the dropdown menu if visible over the top of everything.
            if dropdown and dropdown.visible and selected_screen_object == sObject:
                dropdown.draw(pygamescreen)

        pygame_gui_manager.update(time_delta)

        # Draw FPS if enabled
        if show_fps:
            fps = clock.get_fps()
            fps_text = fps_font.render(f"FPS: {fps:.2f}", True, (255, 255, 255))
            fps_rect = fps_text.get_rect(topright=(shared.smartdisplay.x_end - 10, 10))
            pygamescreen.blit(fps_text, fps_rect)

            # Add total draw time for all modules
            total_draw_time = sum(getattr(obj, 'draw_time', 0) for obj in shared.CurrentScreen.ScreenObjects)
            total_time_text = f"DrawTime: {total_draw_time:.2f}ms" # show time in ms
            total_time_surface = fps_font.render(total_time_text, True, (255, 255, 255))
            total_time_rect = total_time_surface.get_rect(topright=(shared.smartdisplay.x_end - 10, 40))
            pygamescreen.blit(total_time_surface, total_time_rect)

        # Draw ruler if enabled
        if show_ruler:
            draw_ruler(pygamescreen, shared.CurrentScreen.ScreenObjects, ruler_color, selected_ruler_color)

        pygame_gui_manager.draw_ui(pygamescreen)
        #now make pygame update display.
        pygame.display.update()
        clock.tick(maxframerate)

def handle_drag_end(selected_objects, start_positions):
    for obj in selected_objects:
        start_pos = start_positions.get(obj)
        if start_pos and (obj.x, obj.y) != start_pos:
            shared.Change_history.add_change("move", {
                "object": obj,
                "old_pos": start_pos,
                "new_pos": (obj.x, obj.y)
            })

def handle_resize_end(screen_object, start_size):
    if (screen_object.width, screen_object.height) != start_size:
        shared.Change_history.add_change("resize", {
            "object": screen_object,
            "old_size": start_size,
            "new_size": (screen_object.width, screen_object.height)
        })

############################################################################################
############################################################################################
# Find available modules
def find_module(byName = None, debugOutput = False):
    # find all modules in the lib/modules folder recursively. look for all .py files.
    # for each file, look for a class that inherits from Module.
    # return a list of all modules found.
    # example: lib/modules/efis/trafficscope/trafficscope.py
    modules = []
    moduleNames = []
    for root, dirs, files in os.walk("lib/modules"):
        for file in files:
            if file.endswith(".py") and not file.startswith("_"):
                # get full path to the file
                path = os.path.join(root, file)
                # get the name after lib/modules but before the file name and remove slashes
                modulePath = path.split("lib/modules/")[1].split("/"+file)[0].replace("/",".")
                # import the file
                module = ".%s" % (file[:-3])
                mod = importlib.import_module(module, "lib.modules."+modulePath)  # dynamically load class
                ClassToload = file[:-3]  # get classname to load
                class_ = getattr(mod, ClassToload)
                newModuleClass = class_()
                if byName is not None:
                    #print("Looking for "+byName+" .. Checking module: %s (%s)" % (newModuleClass.name, path))
                    if newModuleClass.name == byName:
                        #print("Found module: %s (%s)" % (newModuleClass.name, path))
                        modules.append(newModuleClass)
                        moduleNames.append(newModuleClass.name)
                        return modules, moduleNames
                else: 
                    if debugOutput:
                        print("module: %s (%s)" % (newModuleClass.name, path))
                    modules.append(newModuleClass)
                    moduleNames.append(newModuleClass.name)

    #print("Found %d modules" % len(modules))
    #print(modules)
    return modules, moduleNames


############################################################################################
############################################################################################
# TronViewScreenObject
class TronViewScreenObject:
    def __init__(self, pgscreen, type, title, module=None, x=0, y=0, width=100, height=100, id=None):
        self.pygamescreen = pgscreen
        self.type = type
        self.title = title
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.selected = False
        self.id = id or 'M_' + ''.join(random.choice(string.ascii_lowercase + string.digits) for _ in range(5))
        self.showBounds = False
        self.mouse_offset_x = 0
        self.mouse_offset_y = 0
        self.showOptions = False
        
        if type == 'group':
            self.childScreenObjects = []
            self.module = None
        else:
            # create a module object
            if module is not None:
                self.setModule(module)
            else:
                self.module = None

        self.edit_toolbar = EditToolBar(self)

    def isClickInside(self, mx, my):
        return self.x <= mx <= self.x + self.width and self.y <= my <= self.y + self.height

    def setShowBounds(self, show):
        self.showBounds = show
        if self.type == 'group':
            for module in self.childScreenObjects:
                module.showBounds = self.showBounds

    def draw(self, aircraft, smartdisplay):
        global show_fps
        if self.module is None and self.type == 'module':
            boxColor = (140, 0, 0)
            if self.selected:
                boxColor = (255, 255, 0)
            # draw a rect for the module with a x through it.
            pygame.draw.rect(self.pygamescreen, boxColor, (self.x, self.y, self.width, self.height), 1)
            #text = pygame.font.SysFont("monospace", 25, bold=False).render("X", True, (255, 255, 255))
            #self.pygamescreen.blit(text, (self.x + self.width/2 - 5, self.y + self.height/2 - 5))
            # draw a little resize handle in the bottom right corner
            pygame.draw.rect(self.pygamescreen, boxColor, (self.x + self.width - 10, self.y + self.height - 10, 10, 10), 1)
            return
        
        if self.type == 'group':
            if len(self.childScreenObjects) == 0:
                # draw a rect for the group with a gray background
                pygame.draw.rect(self.pygamescreen, (100, 100, 100), (self.x, self.y, self.width, self.height), 1)
                return
            # Draw group outline
            if self.showBounds:
                min_x = min(m.x for m in self.childScreenObjects)
                min_y = min(m.y for m in self.childScreenObjects)
                max_x = max(m.x + m.width for m in self.childScreenObjects)
                max_y = max(m.y + m.height for m in self.childScreenObjects)
                pygame.draw.rect(self.pygamescreen, (255, 150, 0), (min_x-5, min_y-5, max_x-min_x+10, max_y-min_y+10), 2)

            # Draw contained modules
            for module in self.childScreenObjects:
                module.draw(aircraft, smartdisplay)
        else:
            start_time = time.time()
            self.module.draw(aircraft, smartdisplay, (self.x, self.y))
            end_time = time.time()
            self.draw_time = (end_time - start_time) * 1000  # Convert to milliseconds

        # Draw selection box and title
        if self.selected:
            color = (0, 255, 0)
            pygame.draw.rect(self.pygamescreen, color, (self.x, self.y, self.width, self.height), 1)
            pygame.draw.rect(self.pygamescreen, color, (self.x + self.width - 10, self.y + self.height - 10, 10, 10), 1)
            self.edit_toolbar.draw(self.pygamescreen)
        elif self.showBounds:
            pygame.draw.rect(self.pygamescreen, (70, 70, 70), (self.x-5, self.y-5, self.width+10, self.height+10), 2)

        # At the end of the draw method
        if show_fps and hasattr(self, 'draw_time'):
            time_text = f"{self.draw_time:.2f}ms"
            time_surface = debug_font.render(time_text, True, (255, 255, 255))
            time_rect = time_surface.get_rect(bottomleft=(self.x + 5, self.y + self.height - 5))
            self.pygamescreen.blit(time_surface, time_rect)

    def resize(self, width, height):
        if self.type != 'group':
            if width < 40: width = 40
            if height < 40: height = 40
            self.width = width
            self.height = height
            if hasattr(self.module, "initMod"):
                self.module.initMod(self.pygamescreen, width, height)
            if hasattr(self.module, "setup"):
                self.module.setup()
            if hasattr(self.module, "resize"):
                self.module.resize(width, height)
        if self.type == 'group':
            print("Resizing group: %s to %d, %d (old size %d, %d)" % (self.title, width, height, self.width, self.height))
            # resize all modules in the group by difference
            dx = width - self.width
            dy = height - self.height
            for module in self.childScreenObjects:
                module.resize(module.width + dx, module.height + dy)
            self.generateBounds()
    
    def move(self, x, y):
        # figure out the difference in x and y from the current position to the new position
        if self.type != 'group':
            self.x = x
            self.y = y
        if self.type == 'group': # move all children of the group
            dx = x - self.x
            dy = y - self.y
            self.x = x
            self.y = y
            for childSObj in self.childScreenObjects:
                childSObj.move(childSObj.x + dx, childSObj.y + dy) # move the module
            self.generateBounds()

    def setModule(self, module, showOptions = True, width = None, height = None):
        if self.type == 'group':
            print("Cannot set module for a group type ScreenObject")
            return
        self.type = 'module'
        self.module = module
        self.title = module.name
        if width is None or height is None:
            self.module.initMod(self.pygamescreen) # use default width and height
        else:
            self.module.initMod(self.pygamescreen, width, height)
        self.width = self.module.width # then get the actual width and height from the module. it may have changed.
        self.height = self.module.height
        if hasattr(self.module, "setup"):
            self.module.setup()
        self.edit_toolbar = EditToolBar(self)
        if showOptions:
            self.showOptions = True

    def addChildScreenObject(self, sObject):
        if self.type != 'group':
            raise ValueError("Cannot add screen object to a non-group type screenObject")
        if sObject not in self.childScreenObjects:
            self.childScreenObjects.append(sObject)
        self.generateBounds()

    def removeChildScreenObject(self, sObject):
        if self.type != 'group':
            raise ValueError("Cannot remove screen object from a non-group type")
        self.childScreenObjects.remove(sObject)
        self.generateBounds()

    def generateBounds(self): # generate bounds for the group (the smallest rectangle that contains all the child modules)
        if self.type != 'group':
            return
        # generate bounds for the group
        self.x = min(m.x for m in self.childScreenObjects)
        self.y = min(m.y for m in self.childScreenObjects)
        # find the module that is the furthest to the right and down
        modMostRight = None
        modMostDown = None
        for childSObj in self.childScreenObjects:
            if modMostRight is None or childSObj.x + childSObj.width > modMostRight.x + modMostRight.width:
                modMostRight = childSObj
            if modMostDown is None or childSObj.y + childSObj.height > modMostDown.y + modMostDown.height:
                modMostDown = childSObj
        self.width = modMostRight.x + modMostRight.width - self.x
        self.height = modMostDown.y + modMostDown.height - self.y
        #print("Generated bounds for group: %s x:%d y:%d w:%d h:%d" % (self.title, self.x, self.y, self.width, self.height))

    def to_dict(self):
        # save everything about this object to json. modules, 
        data = {
            "type": self.type,
            "title": self.title,
            "x": self.x,
            "y": self.y,
            "width": self.width,
            "height": self.height,
        }
        if self.module:
            data["module"] = {
                "name": self.module.name,
                "options": []
            }
            if hasattr(self.module, "get_module_options"):
                options = self.module.get_module_options()
                for option, details in options.items():
                    data["module"]["options"].append({
                    "name": option,
                    "value": getattr(self.module, option)
                })

        if self.type == 'group' and self.childScreenObjects:
            data["screenObjects"] = []
            for childSObj in self.childScreenObjects:
                data["screenObjects"].append(childSObj.to_dict())
        if self.id:
            data["id"] = self.id

        return data
    def from_dict(self, data):
        self.type = data['type']
        self.title = data['title']
        self.x = data['x']
        self.y = data['y']
        self.width = data['width']
        self.height = data['height']
        if self.type == 'group' and data['screenObjects']:
            self.childScreenObjects = []
            for childSObj in data['screenObjects']:
                new_childSObj = TronViewScreenObject(
                    self.pygamescreen,
                    childSObj['type'],
                    childSObj['title'],
                )
                new_childSObj.from_dict(childSObj)
                self.addChildScreenObject(new_childSObj)
        if self.type == 'module':
            # load the module and options
            newModules, titles  = find_module(self.title)
            self.setModule(newModules[0], showOptions = False, width = data['width'], height = data['height'])
            
            # now load the options
            if hasattr(self.module, "get_module_options"):
                for option in data['module']['options']:
                    try:
                        setattr(self.module, option['name'], option['value'])
                        # if the option has a post_change_function, call it. check newModules[0].get_module_options()
                        if 'post_change_function' in newModules[0].get_module_options()[option['name']]:
                            post_change_function = getattr(self.module, newModules[0].get_module_options()[option['name']]['post_change_function'], None)
                            if post_change_function:
                                post_change_function()
                    except Exception as e:
                            print("Error setting module (%s) option (%s): %s" % (self.module.name, option['name'], e))

    def center(self):
        screen_width, screen_height = pygame.display.get_surface().get_size()
        self.x = (screen_width - self.width) // 2
        self.y = (screen_height - self.height) // 2

    def align_left(self):
        self.x = 0
    def align_right(self):
        screen_width, screen_height = pygame.display.get_surface().get_size()
        self.x = screen_width - self.width

############################################################################################
############################################################################################
# Show the options for a module. These are controls that are built based off the get_module_options() method in the module.
class EditOptionsBar:
    def __init__(self, screen_object, pygame_gui_manager, smartdisplay):
        self.screen_object = screen_object
        self.pygame_gui_manager = pygame_gui_manager
        self.visible = True
        self.ui_elements = []
        self.text_entry_active = False  # Add this line
        
        window_width = 220
        window_height = min(self.calculate_height(), 500)  # Limit window height to 500 pixels
        
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
            object_id="#options_window"
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
            return min(height, 500)  # Limit max height to 500 pixels
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
                if current_value not in options_list:
                    options_list.append(current_value)
                
                dropdown = UIDropDownMenu(
                    options_list=options_list,
                    starting_option=current_value,
                    relative_rect=pygame.Rect(x_offset, y_offset, 180, 20),
                    manager=self.pygame_gui_manager,
                    container=self.scrollable_container
                )
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
                    self.text_entry_active = True
                    foundClickedTextEntry = True
                    break           
            if foundClickedTextEntry == False:
                self.text_entry_active = False # else they didn't click on a text entry field

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
            self.text_entry_active = True
        elif event.type == pygame_gui.UI_TEXT_ENTRY_FINISHED:
            print("Text entry finished")
            self.text_entry_active = False
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
            value = float(text)
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
        setattr(self.screen_object.module, option, color)
        for element in self.ui_elements:
            if isinstance(element, UIButton) and getattr(element, 'option_name', None) == option:
                current_color_pygame = pygame.Color(*color)
                element.colours['normal_bg'] = current_color_pygame
                element.rebuild()
                #break
        if hasattr(self.screen_object.module, 'update_option'):
            self.screen_object.module.update_option(option, color)
        
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
        x = min(self.screen_object.x + self.screen_object.width, 
                screen_width - window_width)
        x = max(0, x)  # Ensure it doesn't go off the left edge

        # Calculate y position
        y = self.screen_object.y

        # Check if the bottom of the window goes off the screen
        if y + window_height > screen_height:
            # Adjust y to keep the bottom of the window on the screen
            y = screen_height - window_height

        # Ensure it doesn't go above the top of the screen
        y = max(0, y)

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

############################################################################################
############################################################################################
class EditToolBarButton:
    def __init__(self, text=None, icon=None, id=None, state=False):
        self.text = text
        self.icon = icon
        self.state = state  # is this button turned on or off? (color changed)
        self.font = pygame.font.Font(None, 25)  # Changed to 30pt
        self.width = self.calculate_width()
        self.height = 40  # Increased height to accommodate larger text
        self.rect = pygame.Rect(0, 0, self.width, self.height)
        self.id = id

    def calculate_width(self):
        if self.text:
            text_surface = self.font.render(self.text, True, (255, 255, 255))
            return max(text_surface.get_width() + 20, 40)  # Increased padding and minimum width
        return 40  # Default width for icon buttons

    def set_text(self, text):
        self.text = text
        self.width = self.calculate_width()

    def draw(self, surface, x, y):
        self.rect.topleft = (x, y)
        color = (0, 0, 255) if self.state else (50, 50, 50)
        pygame.draw.rect(surface, color, self.rect)
        if self.text:
            text_surf = self.font.render(self.text, True, (255, 255, 255))
            text_rect = text_surf.get_rect(center=self.rect.center)
            # draw a light gray rect around the inside of the button
            pygame.draw.rect(surface, (150, 150, 150), self.rect.inflate(-10, -10), 1)
            surface.blit(text_surf, text_rect)
        elif self.icon:
            # Draw icon (placeholder)
            pygame.draw.rect(surface, (255, 255, 255), self.rect.inflate(-10, -10))

############################################################################################
############################################################################################
class EditToolBar:
    def __init__(self, screen_object):
        self.screen_object = screen_object
        self.buttons = [
            EditToolBarButton(text=screen_object.title, id="title"),
            EditToolBarButton(text="|", id="center"),
            EditToolBarButton(text="<", id="align_left"),
            EditToolBarButton(text=">", id="align_right"),
            #EditToolBarButton(text="x", id="delete"),
            EditToolBarButton(text="+", id="move_up"),
            EditToolBarButton(text="-", id="move_down"),
            EditToolBarButton(text="O", id="edit_options", state=screen_object.showOptions)
        ]
        self.width = sum(button.width for button in self.buttons)
        self.height = 40  # Increased to match button height
        self.position = "top"  # Default to top

    def draw(self, surface):
        x, y = self.get_position()
        self.buttons[6].state = self.screen_object.showOptions # set the state of the edit options button
        for button in self.buttons:
            button.draw(surface, x, y)
            x += button.width

    def get_position(self):
        screen_width, screen_height = pygame.display.get_surface().get_size()
        
        # Always try to position at the top first
        x = self.screen_object.x
        y = self.screen_object.y - self.height - 5

        # Adjust if off-screen to the right
        if x + self.width > screen_width:
            x = screen_width - self.width

        # Adjust if off-screen to the left
        if x < 0:
            x = 0

        # If there's not enough space at the top, move to the bottom
        if y < 0:
            y = self.screen_object.y + self.screen_object.height + 5
            
            # If it's still off-screen at the bottom, keep it at the top
            if y + self.height > screen_height:
                y = 0

        return x, y

    def handle_click(self, pos):
        # get the id of the button that was clicked
        button_id = None
        for button in self.buttons:
            if button.rect.collidepoint(pos):
                button_id = button.id
                break
        if button_id:
            print("Button clicked: %s" % button_id)
            return button_id        
        return None


COLOR_INACTIVE = (30, 30, 30)
COLOR_ACTIVE = (100, 200, 255)
COLOR_LIST_INACTIVE = (100, 100, 100)
COLOR_LIST_ACTIVE = (100, 150, 100) # green

############################################################################################
############################################################################################
# DropDown class
class DropDown():
    def __init__(self, color_menu, color_option, x, y, w, h, font, main, options):
        self.color_menu = color_menu
        self.color_option = color_option
        self.rect = pygame.Rect(x, y, w, h)
        self.font = font
        self.main = main    # main text
        self.options = options
        self.draw_menu = False
        self.menu_active = False
        self.active_option = -1 # -1 means no option is selected else it is the index of the selected option.
        self.value = None # value of the selected option
        self.visible = False

    # draw the drop down.
    def draw(self, surf):
        #if not self.visible:
        #    return
        pygame.draw.rect(surf, self.color_menu[self.menu_active], self.rect, 0)
        msg = self.font.render(self.main, 1, (0, 0, 0))
        surf.blit(msg, msg.get_rect(center = self.rect.center))

        if self.draw_menu:
            for i, text in enumerate(self.options):
                rect = self.rect.copy()
                rect.y += (i+1) * self.rect.height
                pygame.draw.rect(surf, self.color_option[1 if i == self.active_option else 0], rect, 0)
                msg = self.font.render(text, 1, (0, 0, 0))
                surf.blit(msg, msg.get_rect(center = rect.center))

    # returns the index of the selected option
    def update(self, event_list):
        mpos = pygame.mouse.get_pos()
        self.menu_active = self.rect.collidepoint(mpos)
        self.active_option = -1
        self.value = None
        for i in range(len(self.options)):
            rect = self.rect.copy()
            rect.y += (i+1) * self.rect.height
            if rect.collidepoint(mpos):
                self.active_option = i
                #if self.menu_active:
                self.value = self.options[i]
                break

        if not self.menu_active and self.active_option == -1:
            self.draw_menu = False

        for event in event_list:
            if event.type == pygame.MOUSEBUTTONDOWN:
                if self.menu_active:
                    self.draw_menu = not self.draw_menu
                    self.visible = not self.visible
                    print("Menu active")
                elif self.draw_menu and self.active_option >= 0:
                    self.draw_menu = False
                    self.visible = False
                    return self.active_option
                
                self.visible = False
                self.draw_menu = False        
        return -1


    def toggle(self):
        self.draw_menu = not self.draw_menu
        self.visible = not self.visible
    

def save_screen_to_json():
    data = {
        "ver": {"version": "1.0"},  # You can update this version as needed
        "screen": {
            "title": "No Name",
            "width": shared.smartdisplay.x_end,
            "height": shared.smartdisplay.y_end
        },
        "screenObjects": [obj.to_dict() for obj in shared.CurrentScreen.ScreenObjects]
    }
    
    filename = "screen.json"

    #timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = shared.DataDir + "screens/" + filename
    # if it doesn't end with .json then add it.
    if not filename.endswith(".json"):
        filename = filename + ".json"
    
    with open(filename, "w") as f:
        json.dump(data, f, indent=2)
    
    print(f"Screen saved to {filename}")

def load_screen_from_json(filename):
    try:
        filename = shared.DataDir + "screens/" + filename
        # if it doesn't end with .json then add it.
        if not filename.endswith(".json"):
            filename = filename + ".json"
        with open(filename, 'r') as f:
            data = json.load(f)
        
        # Clear existing screen objects
        shared.CurrentScreen.ScreenObjects.clear()
        
        # Set screen properties
        shared.CurrentScreen.title = data['screen']['title']
        shared.smartdisplay.x_end = data['screen']['width']
        shared.smartdisplay.y_end = data['screen']['height']
        
        # Load screen objects using the from_dict method
        for obj_data in data['screenObjects']:
            new_obj = TronViewScreenObject(shared.CurrentScreen.pygamescreen, obj_data['type'], obj_data['title'])
            new_obj.from_dict(obj_data)
            shared.CurrentScreen.ScreenObjects.append(new_obj)
        
        print(f"Screen loaded from {filename}")
    except Exception as e:
        # get full error
        import traceback
        traceback.print_exc()
        print(f"Error loading screen from {filename}: {str(e)}")

def draw_ruler(screen, screen_objects, ruler_color, selected_ruler_color):
    screen_width, screen_height = screen.get_size()
    screen_center = (screen_width // 2, screen_height // 2)

    # Draw center lines of the screen
    draw_dashed_line(screen, ruler_color, (screen_center[0], 0), (screen_center[0], screen_height))
    draw_dashed_line(screen, ruler_color, (0, screen_center[1]), (screen_width, screen_center[1]))

    font = pygame.font.Font(None, 24)

    selected_objects = [obj for obj in screen_objects if obj.selected]
    
    if not selected_objects:
        return

    threshold = 10  # Proximity threshold for showing rulers
    align_threshold = 1  # Threshold for considering objects aligned

    for selected_obj in selected_objects:
        aligned_edges = get_aligned_edges(selected_obj, screen_objects, align_threshold)
        draw_object_rulers(screen, selected_obj, selected_ruler_color, font, aligned_edges)

        for obj in screen_objects:
            if obj.type == 'module' and obj.module is None:
                continue
            if obj.selected:
                continue

            if is_close_to_selected(selected_obj, obj, threshold):
                obj_aligned_edges = get_aligned_edges(obj, [selected_obj], align_threshold)
                draw_object_rulers(screen, obj, ruler_color, font, obj_aligned_edges)

def get_aligned_edges(selected_obj, screen_objects, threshold):
    aligned_edges = {
        'left': False, 'right': False, 'top': False, 'bottom': False,
        'center_x': False, 'center_y': False
    }
    
    for obj in screen_objects:
        if obj == selected_obj or (obj.type == 'module' and obj.module is None):
            continue
        
        if abs(selected_obj.x - obj.x) < threshold:
            aligned_edges['left'] = True
        if abs((selected_obj.x + selected_obj.width) - (obj.x + obj.width)) < threshold:
            aligned_edges['right'] = True
        if abs(selected_obj.y - obj.y) < threshold:
            aligned_edges['top'] = True
        if abs((selected_obj.y + selected_obj.height) - (obj.y + obj.height)) < threshold:
            aligned_edges['bottom'] = True
        
        selected_center_x = selected_obj.x + selected_obj.width // 2
        selected_center_y = selected_obj.y + selected_obj.height // 2
        obj_center_x = obj.x + obj.width // 2
        obj_center_y = obj.y + obj.height // 2
        
        if abs(selected_center_x - obj_center_x) < threshold:
            aligned_edges['center_x'] = True
        if abs(selected_center_y - obj_center_y) < threshold:
            aligned_edges['center_y'] = True
    
    return aligned_edges

def draw_object_rulers(screen, obj, color, font, aligned_edges):
    screen_width, screen_height = screen.get_size()
    obj_center = (obj.x + obj.width // 2, obj.y + obj.height // 2)
    
    magenta = (255, 0, 255)
    
    # Draw small plus at the center of the object
    plus_size = 10
    pygame.draw.line(screen, color, (obj_center[0] - plus_size, obj_center[1]), (obj_center[0] + plus_size, obj_center[1]))
    pygame.draw.line(screen, color, (obj_center[0], obj_center[1] - plus_size), (obj_center[0], obj_center[1] + plus_size))

    # Draw vertical center line
    center_x_color = magenta if aligned_edges['center_x'] else color
    draw_dashed_line(screen, center_x_color, (obj_center[0], 0), (obj_center[0], screen_height))

    # Draw horizontal center line
    center_y_color = magenta if aligned_edges['center_y'] else color
    draw_dashed_line(screen, center_y_color, (0, obj_center[1]), (screen_width, obj_center[1]))

    # Draw left vertical line
    left_color = magenta if aligned_edges['left'] else color
    draw_dashed_line(screen, left_color, (obj.x, 0), (obj.x, screen_height))

    # Draw right vertical line
    right_color = magenta if aligned_edges['right'] else color
    draw_dashed_line(screen, right_color, (obj.x + obj.width, 0), (obj.x + obj.width, screen_height))

    # Draw top horizontal line
    top_color = magenta if aligned_edges['top'] else color
    draw_dashed_line(screen, top_color, (0, obj.y), (screen_width, obj.y))

    # Draw bottom horizontal line
    bottom_color = magenta if aligned_edges['bottom'] else color
    draw_dashed_line(screen, bottom_color, (0, obj.y + obj.height), (screen_width, obj.y + obj.height))

    if obj.selected:
        # Draw position (x, y) in the top-left corner
        pos_text = f"({obj.x}, {obj.y})"
        pos_surface = font.render(pos_text, True, color)
        screen.blit(pos_surface, (obj.x + 5, obj.y + 5))

        # Draw width at the bottom
        width_text = f"W: {obj.width}"
        width_surface = font.render(width_text, True, color)
        width_rect = width_surface.get_rect(center=(obj.x + obj.width // 2, obj.y + obj.height - 15))
        screen.blit(width_surface, width_rect)

        # Draw height on the right side
        height_text = f"H: {obj.height}"
        height_surface = font.render(height_text, True, color)
        height_surface = pygame.transform.rotate(height_surface, 90)
        height_rect = height_surface.get_rect(center=(obj.x + obj.width - 15, obj.y + obj.height // 2))
        screen.blit(height_surface, height_rect)

def is_close_to_selected(selected_obj, obj, threshold):
    # Check horizontal lines
    if (abs(selected_obj.y - obj.y) < threshold or
        abs(selected_obj.y - (obj.y + obj.height)) < threshold or
        abs((selected_obj.y + selected_obj.height) - obj.y) < threshold or
        abs((selected_obj.y + selected_obj.height) - (obj.y + obj.height)) < threshold):
        return True

    # Check vertical lines
    if (abs(selected_obj.x - obj.x) < threshold or
        abs(selected_obj.x - (obj.x + obj.width)) < threshold or
        abs((selected_obj.x + selected_obj.width) - obj.x) < threshold or
        abs((selected_obj.x + selected_obj.width) - (obj.x + obj.width)) < threshold):
        return True

    # Check center lines
    selected_center_x = selected_obj.x + selected_obj.width // 2
    selected_center_y = selected_obj.y + selected_obj.height // 2
    obj_center_x = obj.x + obj.width // 2
    obj_center_y = obj.y + obj.height // 2

    if abs(selected_center_x - obj_center_x) < threshold or abs(selected_center_y - obj_center_y) < threshold:
        return True

    return False

def draw_dashed_line(surface, color, start_pos, end_pos, dash_length=10):
    x1, y1 = start_pos
    x2, y2 = end_pos
    dx = x2 - x1
    dy = y2 - y1
    distance = max(abs(dx), abs(dy))
    if distance == 0:
        return
    dx = dx / distance
    dy = dy / distance

    for i in range(0, int(distance), dash_length * 2):
        start = (int(x1 + i * dx), int(y1 + i * dy))
        end = (int(x1 + (i + dash_length) * dx), int(y1 + (i + dash_length) * dy))
        pygame.draw.line(surface, color, start, end, 1)

def show_help_dialog(pygame_gui_manager):
    help_text = """
    Key Commands:
    ? - Show this help dialog
    E - Exit Edit Mode (goto normal mode)
    Q - Quit
    ESC - unselect all objects
    A - Add new screen object
    G - Group selected objects
    Ctrl+G - Ungroup selected group
    B - Toggle boundary boxes
    C - Clone selected object(s)    
    DELETE or BACKSPACE - Delete selected object
    S - Save screen to JSON
    L - Load screen from JSON
    F - Toggle FPS and draw time display
    R - Toggle ruler
    Arrow keys - Move selected object(s)
    Ctrl + Arrow keys - Move selected object(s) by 10 pixels
    PAGE UP - Move selected object up in draw order
    PAGE DOWN - Move selected object down in draw order
    Ctrl+z - Undo last change
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

def clone_screen_objects(selected_objects, mouse_x, mouse_y):
    if not selected_objects:
        return []

    cloned_objects = []
    reference_obj = selected_objects[0]
    offset_x = mouse_x - reference_obj.x
    offset_y = mouse_y - reference_obj.y

    for obj in selected_objects:
        new_obj = TronViewScreenObject(
            obj.pygamescreen,
            obj.type,
            obj.title + "_clone",
            module=None,
            x=obj.x + offset_x,
            y=obj.y + offset_y,
            width=obj.width,
            height=obj.height,
            id=None
        )
        
        new_obj.showBounds = obj.showBounds
        new_obj.showOptions = obj.showOptions
        
        if obj.type == 'group':
            new_obj.childScreenObjects = [clone_screen_object(child, offset_x, offset_y) for child in obj.childScreenObjects]
        else:
            if obj.module:
                new_module = type(obj.module)()
                for attr, value in vars(obj.module).items():
                    if not callable(value) and not attr.startswith("__"):
                        setattr(new_module, attr, value)
                new_obj.setModule(new_module)
        
        cloned_objects.append(new_obj)
    
    return cloned_objects

def clone_screen_object(obj, offset_x, offset_y):
    new_obj = TronViewScreenObject(
        obj.pygamescreen,
        obj.type,
        obj.title + "_clone",
        module=None,
        x=obj.x + offset_x,
        y=obj.y + offset_y,
        width=obj.width,
        height=obj.height,
        id=None
    )
    
    new_obj.showBounds = obj.showBounds
    new_obj.showOptions = obj.showOptions
    
    if obj.type == 'group':
        new_obj.childScreenObjects = [clone_screen_object(child, offset_x, offset_y) for child in obj.childScreenObjects]
    else:
        if obj.module:
            new_module = type(obj.module)()
            for attr, value in vars(obj.module).items():
                if not callable(value) and not attr.startswith("__"):
                    setattr(new_module, attr, value)
            new_obj.setModule(new_module)
    
    return new_obj

class ChangeHistory:
    def __init__(self, max_history=100):
        self.history = deque(maxlen=max_history)

    def add_change(self, change_type, data):
        self.history.append({"type": change_type, "data": data})
        print(f"history added: {change_type}, {data}")

    def undo(self):
        if self.history:
            return self.history.pop()
        return None

def undo_last_change(change_history):
    change = change_history.undo()
    if change:
        print(f"undoing change: {change}")
        if change["type"] == "move":
            change["data"]["object"].move(*change["data"]["old_pos"])
        elif change["type"] == "delete":
            shared.CurrentScreen.ScreenObjects.append(change["data"]["object"])
        elif change["type"] == "add":
            shared.CurrentScreen.ScreenObjects.remove(change["data"]["object"])
        elif change["type"] == "option_change":
            setattr(change["data"]["object"].module, change["data"]["option"], change["data"]["old_value"])
            if hasattr(change["data"]["object"].module, 'update_option'):
                change["data"]["object"].module.update_option(change["data"]["option"], change["data"]["old_value"])
        elif change["type"] == "resize":
            change["data"]["object"].resize(*change["data"]["old_size"])
    else:
        print("no change to undo")

def get_aircraft_fields(obj, prefix=''):
    fields = []
    
    for name, value in inspect.getmembers(obj):
        # Skip private and special methods
        if name.startswith('__'):
            continue
        
        full_name = f"{prefix}{name}" if prefix else name
        
        if isinstance(value, (str, int, float, list, tuple, dict)):
            fields.append(full_name)
        elif inspect.isfunction(value) or inspect.ismethod(value):
            fields.append(f"{full_name}()")
        elif inspect.isclass(value):
            # Skip classes
            continue
        elif hasattr(value, '__dict__'):
            # It's an object, recurse into it
            fields.extend(get_aircraft_fields(value, f"{full_name}."))
    
    return fields

# Example usage:
def list_aircraft_fields():
    fields = get_aircraft_fields(shared.aircraft)
    for field in fields:
        print(field)

# vi: modeline tabstop=8 expandtab shiftwidth=4 softtabstop=4 syntax=python
