#!/usr/bin/env python

#######################################################################################################################################
#######################################################################################################################################
# edit mode
#
# import random
# import string
from lib.common import shared
import pygame, pygame_gui
from lib import hud_utils
from lib.common.graphic.edit_history import ChangeHistory, undo_last_change
from lib.common.graphic.edit_help import show_help_dialog
from lib.common.graphic.edit_clone import clone_screen_objects
from lib.common.graphic.edit_TronViewScreenObject import TronViewScreenObject
from lib.common.graphic.edit_rulers import draw_ruler
from lib.common.graphic.edit_find_module import find_module
from lib.common.graphic.edit_save_load import save_screen_to_json, load_screen_from_json
from lib.common.graphic.edit_EditToolBar import EditToolBar
from lib.common.graphic.edit_EditOptionsBar import EditOptionsBar

# Add this near the top of the file, after the imports

#############################################
## Function: main edit loop
def main_edit_loop():

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
    fps_font = pygame.font.SysFont("monospace", 30)
    show_ruler = False
    ruler_color = (100, 100, 100, 6)  # Light gray for non-selected objects
    selected_ruler_color = (0, 255, 0, 6)  # Green for selected objects
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
                        shared.aircraft.show_FPS = not shared.aircraft.show_FPS

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
                        undo_last_change(shared.Change_history, shared)

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
        if shared.aircraft.show_FPS:
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
# DropDown class used to pick the module from the list of modules.
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

COLOR_INACTIVE = (100, 100, 100)
COLOR_ACTIVE = (255, 255, 255)
COLOR_LIST_INACTIVE = (100, 100, 100)
COLOR_LIST_ACTIVE = (255, 255, 255)

# vi: modeline tabstop=8 expandtab shiftwidth=4 softtabstop=4 syntax=python
