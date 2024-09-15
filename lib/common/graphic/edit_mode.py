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

    # list of modules
    #listModules = ["Heading", "Roll", "Horizon", "AOA", "SlipSkid", "Wind", "TrafficScope", "CDI", "GCross", "Calibration", "Test"]

    # clear screen using pygame
    pygamescreen = pygame.display.set_mode((shared.smartdisplay.x_end, shared.smartdisplay.y_end))
    pygamescreen.fill((0, 0, 0))
    pygame.display.update()

    # if shared.CurrentScreen.ScreenObjects exists.. if it doesn't create it as array
    if not hasattr(shared.CurrentScreen, "ScreenObjects"):
        shared.CurrentScreen.ScreenObjects = []
        # create _class in Modules that has name,id, x,y, width, height, and color.
        shared.CurrentScreen.ScreenObjects.append(
            TronViewScreenObject(pygamescreen, 'module', f"A_{len(shared.CurrentScreen.ScreenObjects)}")
        )


    selected_module = None
    dragging = False # are we dragging a module?
    offset_x = 0 # x offset for dragging
    offset_y = 0 # y offset for dragging
    resizing = False  # are we resizing a module?
    dropdown = None # dropdown menu for module selection (if any)
    modulesFound, listModules = find_module()
    showAllBoundryBoxes = False

    selected_modules = []
    current_group = None

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
                selected_module.title = listModules[selection]
                newModules, titles  = find_module(listModules[selection])
                selected_module.setModule(newModules[0])
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
                    elif event.key == pygame.K_e:
                        shared.aircraft.editMode = False  # exit edit mode
                        exit_edit_mode = True
                    # g will create a new group if there is multiple modules selected
                    elif event.key == pygame.K_g:
                        if len(selected_modules) > 1:
                            print("Creating group with %d modules. Modules: %s" % (len(selected_modules), [module.title for module in selected_modules]))
                            current_group = TronViewScreenObject(pygamescreen, 'group', f"Group_{len(shared.CurrentScreen.ScreenObjects)}")
                            for module in selected_modules:
                                module.selected = False
                                current_group.addModule(module)
                                shared.CurrentScreen.ScreenObjects.remove(module) # remove from screen objects
                            shared.CurrentScreen.ScreenObjects.append(current_group) # add to screen objects
                        else:
                            print("You must select multiple modules to create a group.")
                    # look for cntl b to show all boxes
                    elif event.key == pygame.K_b:
                        showAllBoundryBoxes = not showAllBoundryBoxes
                        print("showAllBoxes: ", showAllBoundryBoxes)
                        for module in shared.CurrentScreen.ScreenObjects:
                            module.setShowBounds(showAllBoundryBoxes)

                    # look for delete key
                    elif event.key == pygame.K_BACKSPACE or event.key == pygame.K_DELETE:
                        print("Delete key pressed")
                        # delete the selected module by going through the list of modules and removing the selected one.
                        for module in shared.CurrentScreen.ScreenObjects:
                            if module.selected:
                                shared.CurrentScreen.ScreenObjects.remove(module)
                                break

                    elif event.key == pygame.K_a:
                        # add a new module
                        mx, my = pygame.mouse.get_pos()
                        shared.CurrentScreen.ScreenObjects.append(
                            TronViewScreenObject(pygamescreen, 'module', f"A_{len(shared.CurrentScreen.ScreenObjects)}", module=None, x=mx, y=my)
                        )

                # check for Mouse events
                if event.type == pygame.MOUSEBUTTONDOWN:
                    mx, my = pygame.mouse.get_pos()
                    print("Mouse Click %d x %d" % (mx, my))
                    
                    # Check if Shift is held down
                    shift_held = pygame.key.get_mods() & pygame.KMOD_SHIFT

                    if not shift_held:
                        selected_modules.clear()
                        # deselect all modules
                        for module in shared.CurrentScreen.ScreenObjects:
                            module.selected = False

                    # Check if the mouse click is inside any screenObject (check from the top down)
                    for module in shared.CurrentScreen.ScreenObjects[::-1]:
                        if module.x <= mx <= module.x + module.width and module.y <= my <= module.y + module.height:
                            if shift_held:
                                if module not in selected_modules:
                                    selected_modules.append(module)
                                    module.selected = True
                                    print("Selected module: %s (shift) current modules: %d" % (module.title, len(selected_modules)))
                            else:
                                selected_modules = [module]
                                module.selected = True
                                print("Selected module: %s" % module.title)
                            #################
                            # RESIZE MODULE
                            if mx >= module.x + module.width - 10 and my >= module.y + module.height - 10:
                                # Click is in the bottom right corner, start resizing
                                selected_module = module
                                module.selected = True
                                resizing = True
                                offset_x = mx - module.x
                                offset_y = my - module.y
                                dropdown = None
                            ##################
                            # DROPDOWN MENU (select module)
                            elif module.y <= my <= module.y + 20:  # Assuming the title area is 20 pixels high
                                # Click is on the title, toggle dropdown menu
                                selected_module = module
                                module.selected = True
                                dropdown = DropDown([COLOR_INACTIVE, COLOR_ACTIVE],
                                        [COLOR_LIST_INACTIVE, COLOR_LIST_ACTIVE], 
                                        module.x, module.y, 140, 30, 
                                        pygame.font.SysFont(None, 25), 
                                        "Select Module", listModules)
                                dropdown.visible = True
                                dropdown.draw_menu = True
                            ##################
                            # MOVE MODULE
                            else:
                                dropdown = None
                                # Click is inside the module, start moving
                                selected_module = module
                                dragging = True
                                offset_x = mx - module.x 
                                offset_y = my - module.y
                                module.selected = True
                            break

                # Mouse up
                elif event.type == pygame.MOUSEBUTTONUP:
                    if event.button == 3:  # Right mouse button
                        for module in selected_modules:
                            if module.parent_group:
                                module.parent_group.removeModule(module)
                                if not module.parent_group.modules:
                                    shared.CurrentScreen.ScreenObjects.remove(module.parent_group)
                                    print(f"Removed module from group: {module.parent_group.title}")
                        current_group = None

                    dragging = False
                    resizing = False
                    print("Mouse Up")
                    # selected_module = None
                    # for module in shared.CurrentScreen.ScreenObjects:
                    #     module.selected = False

                # Mouse move.. resize or move the module??
                elif event.type == pygame.MOUSEMOTION:
                    if dragging and len(selected_modules) == 1:  # if dragging a single module
                        mx, my = pygame.mouse.get_pos()
                        selected_modules[0].move(mx - offset_x, my - offset_y)
                        
                        # selected_modules[0].x = mx - offset_x
                        # selected_modules[0].y = my - offset_y
                        # # if the module is in a group, update the group offset
                        # if selected_modules[0].parent_group:
                        #     print("Module is in a group: %s" % selected_modules[0].parent_group.title)
                        #     # go through all modules in the group and update their x and y
                        #     for module in selected_modules[0].parent_group.modules:
                        #         # first get position of where it is from the current mouse position
                        #         temp_x = module.x - selected_modules[0].x
                        #         temp_y = module.y - selected_modules[0].y
                        #         module.x = mx - temp_x
                        #         module.y = my - temp_y
                    elif dragging and len(selected_modules) > 1:  # if dragging multiple modules
                        mx, my = pygame.mouse.get_pos()
                        dx, dy = mx - offset_x, my - offset_y
                        for module in selected_modules:
                            module.x = mx - offset_x
                            module.y = my - offset_y
                        #offset_x, offset_y = mx, my
                        pygamescreen.fill((0, 0, 0))
                    elif dragging and selected_module:  # dragging a single screen object
                        mx, my = pygame.mouse.get_pos()
                        selected_module.move(mx, my)
                    elif resizing and selected_module: # resizing the module
                        mx, my = pygame.mouse.get_pos()
                        temp_width = mx - selected_module.x
                        temp_height = my - selected_module.y
                        if temp_width < 40: temp_width = 40  # limit minimum size
                        if temp_height < 40: temp_height = 40
                        #selected_module.width = temp_width
                        #selected_module.height = temp_height
                        selected_module.resize(temp_width, temp_height)
                        # clear screen using pygame
                        pygamescreen.fill((0, 0, 0))

            # if selection >= 0:
            #     print("Selected module: %s" % listModules[selection])
            #     selected_module.title = listModules[selection]
            #     newModules, titles  = find_module(listModules[selection]) # find the module by name
            #     selected_module.setModule(newModules[0])
            #     dropdown.toggle()
            #     dropdown = None
            # else:
            #     print("No selection "+str(selection))

        # draw the modules
        for sObject in shared.CurrentScreen.ScreenObjects:
            sObject.draw(shared.aircraft, shared.smartdisplay) # draw the module
            # groupId = ""
            # if module.parent_group:
            #     groupId = module.parent_group.title

            # if module.selected or (module.parent_group and any(m.selected for m in selected_modules if m.parent_group == module.parent_group)):
            #     color = (0, 255, 0)
            #     # draw the module box
            #     pygame.draw.rect(pygamescreen, color, (module.x, module.y, module.width, module.height), 1)
            #     # draw the module title
            #     text = debug_font.render(module.title + " " + groupId, True, (255, 255, 255))
            #     pygamescreen.blit(text, (module.x + 5, module.y + 5))
            #     # draw a little resize handle in the bottom right corner
            #     pygame.draw.rect(pygamescreen, color, (module.x + module.width - 10, module.y + module.height - 10, 10, 10), 1)
            # else:
            #     if showAllBoxes:
            #         pygame.draw.rect(pygamescreen, (100, 100, 100), (module.x, module.y, module.width, module.height), 1)
            #         text = debug_font.render(module.title + " " + groupId, True, (255, 255, 255))
            #         pygamescreen.blit(text, (module.x + 5, module.y + 5))
            #         pygame.draw.rect(pygamescreen, color, (module.x + module.width - 10, module.y + module.height - 10, 10, 10), 1)


            # Last... Draw the dropdown menu if visible over the top of everything.
            if dropdown and dropdown.visible and selected_module == module:
                dropdown.draw(pygamescreen)

        # # Draw group outlines
        # for sObject in shared.CurrentScreen.ScreenObjects:
        #     if sObject.type == 'group' and any(module.selected for module in sObject.modules):
        #         min_x = min(module.x for module in sObject.modules)
        #         min_y = min(module.y for module in sObject.modules)
        #         max_x = max(module.x + module.width for module in sObject.modules)
        #         max_y = max(module.y + module.height for module in sObject.modules)
        #         pygame.draw.rect(pygamescreen, (255, 150, 0), (min_x-5, min_y-5, max_x-min_x+10, max_y-min_y+10), 2)

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
        
        if type == 'group':
            self.modules = []
            self.module = None
        else:
            self.module = module
            if module:
                self.module.initMod(self.pygamescreen, width, height)
        
        self.parent_group = None
    
    def isClickInside(self, mx, my):
        return self.x <= mx <= self.x + self.width and self.y <= my <= self.y + self.height

    def setShowBounds(self, show):
        self.showBounds = show
        if self.type == 'group':
            for module in self.modules:
                module.showBounds = self.showBounds

    def draw(self, aircraft, smartdisplay):
        if self.module is None and self.type == 'module':
            # draw a rect for the module with a x through it.
            pygame.draw.rect(self.pygamescreen, (255, 0, 0), (self.x, self.y, self.width, self.height), 1)
            text = pygame.font.SysFont("monospace", 25, bold=False).render("X", True, (255, 255, 255))
            self.pygamescreen.blit(text, (self.x + self.width/2 - 5, self.y + self.height/2 - 5))
            return
        
        if self.type == 'group':
            if len(self.modules) == 0:
                # draw a rect for the group with a gray background
                pygame.draw.rect(self.pygamescreen, (100, 100, 100), (self.x, self.y, self.width, self.height), 1)
                text = pygame.font.SysFont("monospace", 25, bold=False).render("Empty", True, (255, 255, 255))
                self.pygamescreen.blit(text, (self.x + self.width/2 - 5, self.y + self.height/2 - 5))
                return
            #print("Drawing group: %s" % self.title)
            # Draw group outline
            if self.showBounds:
                min_x = min(m.x for m in self.modules)
                min_y = min(m.y for m in self.modules)
                max_x = max(m.x + m.width for m in self.modules)
                max_y = max(m.y + m.height for m in self.modules)
                pygame.draw.rect(self.pygamescreen, (255, 150, 0), (min_x-5, min_y-5, max_x-min_x+10, max_y-min_y+10), 2)
                text = pygame.font.SysFont("monospace", 25, bold=False).render(self.title+" mods:"+str(len(self.modules)), True, (255, 255, 255))
                self.pygamescreen.blit(text, (min_x-5, min_y-5))

            # Draw contained modules
            for module in self.modules:
                module.draw(aircraft, smartdisplay)
        else:
            self.module.draw(aircraft, smartdisplay, (self.x, self.y))
        
        # Draw selection box and title
        if self.selected:
            color = (0, 255, 0)
            pygame.draw.rect(self.pygamescreen, color, (self.x, self.y, self.width, self.height), 1)
            text = pygame.font.SysFont("monospace", 25, bold=False).render(self.title, True, (255, 255, 255))
            self.pygamescreen.blit(text, (self.x + 5, self.y + 5))
            pygame.draw.rect(self.pygamescreen, color, (self.x + self.width - 10, self.y + self.height - 10, 10, 10), 1)
        
        if self.showBounds:
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
            for module in self.modules:
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
            for module in self.modules:
                module.move(module.x + dx, module.y + dy) # move the module
            self.generateBounds()

    def setModule(self, module):
        if self.type == 'group':
            raise ValueError("Cannot set module for a group type TVModule")
        self.module = module
        self.title = module.name
        self.module.initMod(self.pygamescreen, self.width, self.height)
        if hasattr(self.module, "setup"):
            self.module.setup()

    def addModule(self, module):
        if self.type != 'group':
            raise ValueError("Cannot add module to a non-group type TVModule")
        if module not in self.modules:
            self.modules.append(module)
            module.parent_group = self
        self.generateBounds()

    def removeModule(self, module):
        if self.type != 'group':
            raise ValueError("Cannot remove module from a non-group type TVModule")
        self.modules.remove(module)
        module.parent_group = None
        self.generateBounds()

    def generateBounds(self):
        if self.type != 'group':
            return
        # generate bounds for the group
        self.x = min(m.x for m in self.modules)
        self.y = min(m.y for m in self.modules)
        # find the module that is the furthest to the right and down
        modMostRight = None
        modMostDown = None
        for module in self.modules:
            if modMostRight is None or module.x + module.width > modMostRight.x + modMostRight.width:
                modMostRight = module
            if modMostDown is None or module.y + module.height > modMostDown.y + modMostDown.height:
                modMostDown = module
        self.width = modMostRight.x + modMostRight.width - self.x
        self.height = modMostDown.y + modMostDown.height - self.y
        #print("Generated bounds for group: %s x:%d y:%d w:%d h:%d" % (self.title, self.x, self.y, self.width, self.height))

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
    


# vi: modeline tabstop=8 expandtab shiftwidth=4 softtabstop=4 syntax=python
