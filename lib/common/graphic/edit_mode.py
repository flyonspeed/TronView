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
import inspect
import importlib
from lib.modules.efis.trafficscope import trafficscope
import json
from datetime import datetime


#############################################
## Function: main edit loop
def main_edit_loop():
    global debug_font
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
        shared.CurrentScreen.ScreenObjects.append(
            TronViewScreenObject(pygamescreen, 'module', f"A_{len(shared.CurrentScreen.ScreenObjects)}")
        )

    selected_screen_object = None
    dragging = False # are we dragging a screen object?
    offset_x = 0 # x offset for dragging
    offset_y = 0 # y offset for dragging
    resizing = False  # are we resizing?
    dropdown = None # dropdown menu for module selection (if any)
    modulesFound, listModules = find_module()
    showAllBoundryBoxes = False

    selected_screen_objects = []

    ##########################################
    # Main edit draw loop
    while not shared.aircraft.errorFoundNeedToExit and not exit_edit_mode:
        clock.tick(maxframerate)
        pygamescreen.fill((0, 0, 0)) # clear screen

        event_list = pygame.event.get() # get all events
        if dropdown and dropdown.visible:
            #dropdown.draw(pygamescreen)
            selection = dropdown.update(event_list)
            if selection >= 0:
                print("Selected module: %s" % listModules[selection])
                selected_screen_object.title = listModules[selection]
                newModules, titles  = find_module(listModules[selection])
                selected_screen_object.setModule(newModules[0])
        else:
            for event in event_list:  # check for event like keyboard input.
                if event.type == pygame.QUIT:
                    shared.aircraft.errorFoundNeedToExit = True
                # KEY MAPPINGS
                if event.type == pygame.KEYDOWN:
                    mods = pygame.key.get_mods()
                    if event.key == pygame.K_3 or event.key == pygame.K_KP3:
                        # do nothing
                        pass
                    elif event.key == pygame.K_q or event.key == pygame.K_ESCAPE:
                        shared.aircraft.errorFoundNeedToExit = True

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
                                shared.CurrentScreen.ScreenObjects.remove(sObject)
                                break
                    # ADD SCREEN OBJECT
                    elif event.key == pygame.K_a:
                        # add a new Screen object
                        mx, my = pygame.mouse.get_pos()
                        shared.CurrentScreen.ScreenObjects.append(
                            TronViewScreenObject(pygamescreen, 'module', f"A_{len(shared.CurrentScreen.ScreenObjects)}", module=None, x=mx, y=my)
                        )
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
                        filename = input("Enter the filename to load: ")
                        load_screen_from_json(filename)

                # check for Mouse events
                if event.type == pygame.MOUSEBUTTONDOWN:
                    mx, my = pygame.mouse.get_pos()
                    print("Mouse Click %d x %d" % (mx, my))
                    
                    # Check if Shift is held down
                    shift_held = pygame.key.get_mods() & pygame.KMOD_SHIFT

                    atLeastOneSelectedObjectIsClicked = False
                    if not shift_held: # if shift is not held, we are clicking on a single object
                        # are we clicking on a selected object?
                        for sObject in shared.CurrentScreen.ScreenObjects:
                            if sObject.selected:
                                if sObject.x <= mx <= sObject.x + sObject.width and sObject.y <= my <= sObject.y + sObject.height:
                                    atLeastOneSelectedObjectIsClicked = True
                        if atLeastOneSelectedObjectIsClicked == False :
                            selected_screen_objects.clear()
                            # deselect all modules
                            for sObject in shared.CurrentScreen.ScreenObjects:
                                sObject.selected = False

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
                                offset_x = mx - sObject.x
                                offset_y = my - sObject.y
                                dropdown = None
                            ##################
                            # DROPDOWN MENU (select module)
                            elif sObject.y <= my <= sObject.y + 20:  # Assuming the title area is 20 pixels high
                                # Click is on the title, toggle dropdown menu
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
                            break

                # Mouse up
                elif event.type == pygame.MOUSEBUTTONUP:
                    dragging = False
                    resizing = False
                    print("Mouse Up")

                # Mouse move.. resize or move the module??
                elif event.type == pygame.MOUSEMOTION:
                    if dragging and len(selected_screen_objects) == 1:  # if dragging a single screen object
                        mx, my = pygame.mouse.get_pos()
                        selected_screen_objects[0].move(mx - offset_x, my - offset_y)
                    
                    elif dragging and len(selected_screen_objects) > 1:  # if dragging multiple screen objects
                        mx, my = pygame.mouse.get_pos()
                        # move all children of the selected screen objects
                        for sObject in selected_screen_objects:
                            # get the difference in x and y from the current position to the new position
                            diffX = mx - sObject.mouse_offset_x
                            diffY = my - sObject.mouse_offset_y
                            #print("Moving %s by %d, %d " % (sObject.title, diffX, diffY))
                            sObject.move(diffX, diffY)

                        pygamescreen.fill((0, 0, 0))
                    elif dragging and selected_screen_object:  # dragging a single screen object
                        mx, my = pygame.mouse.get_pos()
                        selected_screen_object.move(mx, my)
                    elif resizing and selected_screen_object: # resizing
                        mx, my = pygame.mouse.get_pos()
                        temp_width = mx - selected_screen_object.x
                        temp_height = my - selected_screen_object.y
                        if temp_width < 40: temp_width = 40  # limit minimum size
                        if temp_height < 40: temp_height = 40
                        selected_screen_object.resize(temp_width, temp_height)
                        pygamescreen.fill((0, 0, 0))

        # draw the modules
        for sObject in shared.CurrentScreen.ScreenObjects:
            sObject.draw(shared.aircraft, shared.smartdisplay) # draw

            # Last... Draw the dropdown menu if visible over the top of everything.
            if dropdown and dropdown.visible and selected_screen_object == sObject:
                dropdown.draw(pygamescreen)

        #now make pygame update display.
        pygame.display.update()



##############################################
# Find available modules
def find_module(byName = None):
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
                    print("module: %s (%s)" % (newModuleClass.name, path))
                    modules.append(newModuleClass)
                    moduleNames.append(newModuleClass.name)

    #print("Found %d modules" % len(modules))
    #print(modules)
    return modules, moduleNames
    



##############################################
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
        
        if type == 'group':
            self.childScreenObjects = []
            self.module = None
        else:
            self.module = module
            if module:
                self.module.initMod(self.pygamescreen, width, height)
            
    def isClickInside(self, mx, my):
        return self.x <= mx <= self.x + self.width and self.y <= my <= self.y + self.height

    def setShowBounds(self, show):
        self.showBounds = show
        if self.type == 'group':
            for module in self.childScreenObjects:
                module.showBounds = self.showBounds

    def draw(self, aircraft, smartdisplay):
        if self.module is None and self.type == 'module':
            boxColor = (140, 0, 0)
            if self.selected:
                boxColor = (255, 255, 0)
            # draw a rect for the module with a x through it.
            pygame.draw.rect(self.pygamescreen, boxColor, (self.x, self.y, self.width, self.height), 1)
            text = pygame.font.SysFont("monospace", 25, bold=False).render("X", True, (255, 255, 255))
            self.pygamescreen.blit(text, (self.x + self.width/2 - 5, self.y + self.height/2 - 5))
            # draw a little resize handle in the bottom right corner
            pygame.draw.rect(self.pygamescreen, boxColor, (self.x + self.width - 10, self.y + self.height - 10, 10, 10), 1)
            return
        
        if self.type == 'group':
            if len(self.childScreenObjects) == 0:
                # draw a rect for the group with a gray background
                pygame.draw.rect(self.pygamescreen, (100, 100, 100), (self.x, self.y, self.width, self.height), 1)
                text = pygame.font.SysFont("monospace", 25, bold=False).render("Empty", True, (255, 255, 255))
                self.pygamescreen.blit(text, (self.x + self.width/2 - 5, self.y + self.height/2 - 5))
                return
            #print("Drawing group: %s" % self.title)
            # Draw group outline
            if self.showBounds:
                min_x = min(m.x for m in self.childScreenObjects)
                min_y = min(m.y for m in self.childScreenObjects)
                max_x = max(m.x + m.width for m in self.childScreenObjects)
                max_y = max(m.y + m.height for m in self.childScreenObjects)
                pygame.draw.rect(self.pygamescreen, (255, 150, 0), (min_x-5, min_y-5, max_x-min_x+10, max_y-min_y+10), 2)
                text = pygame.font.SysFont("monospace", 25, bold=False).render(self.title+" mods:"+str(len(self.childScreenObjects)), True, (255, 255, 255))
                self.pygamescreen.blit(text, (min_x-5, min_y-5))

            # Draw contained modules
            for module in self.childScreenObjects:
                module.draw(aircraft, smartdisplay)
        else:
            self.module.draw(aircraft, smartdisplay, (self.x, self.y))
        
        # Draw selection box and title
        if self.selected:
            color = (0, 255, 0)
            pygame.draw.rect(self.pygamescreen, color, (self.x, self.y, self.width, self.height), 1)
            text = pygame.font.SysFont("monospace", 21, bold=False).render(self.title, True, (255, 255, 255))
            self.pygamescreen.blit(text, (self.x + 5, self.y + 5))
            pygame.draw.rect(self.pygamescreen, color, (self.x + self.width - 10, self.y + self.height - 10, 10, 10), 1)
        elif self.showBounds:
            pygame.draw.rect(self.pygamescreen, (70, 70, 70), (self.x-5, self.y-5, self.width+10, self.height+10), 2)

    def resize(self, width, height):
        if self.type != 'group':
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
        if self.type == 'group':
            dx = x - self.x
            dy = y - self.y
            self.x = x
            self.y = y
            #print("Moving screen object: %s to %d, %d from %d,%d, dx:%d dy:%d" % (self.title, x, y, self.x, self.y, dx, dy))
            for childSObj in self.childScreenObjects:
                childSObj.move(childSObj.x + dx, childSObj.y + dy) # move the module
            self.generateBounds()

    def setModule(self, module):
        if self.type == 'group':
            print("Cannot set module for a group type ScreenObject")
            return
        self.module = module
        self.title = module.name
        self.module.initMod(self.pygamescreen, self.width, self.height)
        if hasattr(self.module, "setup"):
            self.module.setup()

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

    def generateBounds(self):
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
            }
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
                    x=childSObj['x'],
                    y=childSObj['y'],
                    width=childSObj['width'],
                    height=childSObj['height']
                )
                self.addChildScreenObject(new_childSObj)


COLOR_INACTIVE = (30, 30, 30)
COLOR_ACTIVE = (100, 200, 255)
COLOR_LIST_INACTIVE = (100, 100, 100)
COLOR_LIST_ACTIVE = (100, 150, 100) # green

#############################################
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
                    return self.active_option
                
                self.visible = False
                self.draw_menu = False

            #     else:
            #         #print("No selection")
            # else:
            #     #print("No button down.")
        
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
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"screen_save_{timestamp}.json"
    
    with open(filename, "w") as f:
        json.dump(data, f, indent=2)
    
    print(f"Screen saved to {filename}")

def load_screen_from_json(filename):
    try:
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
        print(f"Error loading screen from {filename}: {str(e)}")

# vi: modeline tabstop=8 expandtab shiftwidth=4 softtabstop=4 syntax=python
