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

    # if shared.CurrentScreen.Modules exists.. if it doesn't create it as array
    if not hasattr(shared.CurrentScreen, "Modules"):
        shared.CurrentScreen.Modules = []
        # create _class in Modules that has name,id, x,y, width, height, and color.
        shared.CurrentScreen.Modules.append(
            TVModule(
                pygamescreen,
                "Heading",
                "Heading",
                "heading",
                10,
                10,
                400,
                100,
            )
        )

    if not hasattr(shared.CurrentScreen, "ModuleGroups"):
        shared.CurrentScreen.ModuleGroups = []

    selected_module = None
    dragging = False # are we dragging a module?
    offset_x = 0 # x offset for dragging
    offset_y = 0 # y offset for dragging
    resizing = False  # are we resizing a module?
    dropdown = None # dropdown menu for module selection (if any)
    modulesFound, listModules = find_module()
    showAllBoxes = False

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
                    # look for cntl b
                    elif event.key == pygame.K_b:
                        showAllBoxes = not showAllBoxes
                        print("showAllBoxes: ", showAllBoxes)
                    # look for delete key
                    elif event.key == pygame.K_BACKSPACE or event.key == pygame.K_DELETE:
                        print("Delete key pressed")
                        # delete the selected module by going through the list of modules and removing the selected one.
                        for module in shared.CurrentScreen.Modules:
                            if module.selected:
                                shared.CurrentScreen.Modules.remove(module)
                                break

                    elif event.key == pygame.K_a:
                        # add a new module
                        mx, my = pygame.mouse.get_pos()
                        shared.CurrentScreen.Modules.append(
                            TVModule(
                                pygamescreen,
                                "New",
                                "New",
                                "new",
                                mx,
                                my,
                                100,
                                100,
                            )
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
                        for module in shared.CurrentScreen.Modules:
                            module.selected = False

                    # Check if the mouse click is inside any module (check from the top down)
                    for module in shared.CurrentScreen.Modules[::-1]:
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

                    # Create a group if multiple modules are selected
                    if len(selected_modules) > 1 and not current_group:
                        current_group = ModuleGroup()
                        for module in selected_modules:
                            current_group.addModule(module)
                        print(f"Created group: {current_group.name}")

                # Mouse up
                elif event.type == pygame.MOUSEBUTTONUP:
                    if event.button == 3:  # Right mouse button
                        for module in selected_modules:
                            if module.groupId:
                                group = next((g for g in shared.CurrentScreen.ModuleGroups if g.id == module.groupId), None)
                                if group:
                                    group.removeModule(module)
                                    if not group.modules:
                                        shared.CurrentScreen.ModuleGroups.remove(group)
                                    print(f"Removed module from group: {group.name}")
                        current_group = None

                    dragging = False
                    resizing = False
                    print("Mouse Up")
                    # selected_module = None
                    # for module in shared.CurrentScreen.Modules:
                    #     module.selected = False

                # Mouse move.. resize or move the module??
                elif event.type == pygame.MOUSEMOTION:
                    if dragging and len(selected_modules) == 1:  # if dragging a single module
                        mx, my = pygame.mouse.get_pos()
                        selected_modules[0].x = mx - offset_x
                        selected_modules[0].y = my - offset_y
                        # if the module is in a group, update the group offset
                        if selected_modules[0].groupId:
                            print("Module is in a group: %s" % selected_modules[0].groupId)
                            # go through all modules in the group and update their x and y
                            for module in shared.CurrentScreen.Modules:
                                if module.groupId == selected_modules[0].groupId:
                                    # first get position of where it is from the current mouse position
                                    temp_x = module.x - selected_modules[0].x
                                    temp_y = module.y - selected_modules[0].y
                                    module.x = mx - temp_x
                                    module.y = my - temp_y
                    elif dragging and len(selected_modules) > 1:  # if dragging multiple modules
                        mx, my = pygame.mouse.get_pos()
                        dx, dy = mx - offset_x, my - offset_y
                        for module in selected_modules:
                            module.x = mx - offset_x
                            module.y = my - offset_y
                        #offset_x, offset_y = mx, my
                        pygamescreen.fill((0, 0, 0))
                    elif resizing and selected_module: # resizing the module
                        mx, my = pygame.mouse.get_pos()
                        temp_width = mx - selected_module.x
                        temp_height = my - selected_module.y
                        if temp_width < 40: temp_width = 40  # limit minimum size
                        if temp_height < 40: temp_height = 40
                        selected_module.width = temp_width
                        selected_module.height = temp_height
                        selected_module.resize(selected_module.width, selected_module.height)
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
        for module in shared.CurrentScreen.Modules:
            module.draw(shared.aircraft, shared.smartdisplay) # draw the module
            groupId = ""
            if module.groupId:
                groupId = module.groupId

            if module.selected or (module.groupId and any(m.selected for m in selected_modules if m.groupId == module.groupId)):
                color = (0, 255, 0)
                # draw the module box
                pygame.draw.rect(pygamescreen, color, (module.x, module.y, module.width, module.height), 1)
                # draw the module title
                text = debug_font.render(module.title + " " + groupId, True, (255, 255, 255))
                pygamescreen.blit(text, (module.x + 5, module.y + 5))
                # draw a little resize handle in the bottom right corner
                pygame.draw.rect(pygamescreen, color, (module.x + module.width - 10, module.y + module.height - 10, 10, 10), 1)
            else:
                if showAllBoxes:
                    pygame.draw.rect(pygamescreen, (100, 100, 100), (module.x, module.y, module.width, module.height), 1)
                    text = debug_font.render(module.title + " " + groupId, True, (255, 255, 255))
                    pygamescreen.blit(text, (module.x + 5, module.y + 5))
                    pygame.draw.rect(pygamescreen, color, (module.x + module.width - 10, module.y + module.height - 10, 10, 10), 1)


            # Last... Draw the dropdown menu if visible over the top of everything.
            if dropdown and dropdown.visible and selected_module == module:
                dropdown.draw(pygamescreen)

        # Draw group outlines
        for group in shared.CurrentScreen.ModuleGroups:
            if any(module.selected for module in group.modules):
                min_x = min(module.x for module in group.modules)
                min_y = min(module.y for module in group.modules)
                max_x = max(module.x + module.width for module in group.modules)
                max_y = max(module.y + module.height for module in group.modules)
                pygame.draw.rect(pygamescreen, (255, 150, 0), (min_x-5, min_y-5, max_x-min_x+10, max_y-min_y+10), 2)

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
# TronViewModule
class TVModule(object):
    def __init__(self, pgscreen, type, title, module, x, y, width, height):
        self.pygamescreen = pgscreen
        self.type = type
        self.title = title
        self.module = module
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.selected = False
        self.trafficScope = trafficscope.trafficscope()
        self.trafficScope.initMod(self.pygamescreen, width, height)
        self.module = self.trafficScope
        self.groupId = None
    
    def draw(self, aircraft, smartdisplay):
        self.module.draw(aircraft, smartdisplay,(self.x,self.y))

    def resize(self, width, height):
        self.width = width
        self.height = height
        self.module.width = width
        self.module.height = height
        self.module.initMod(self.pygamescreen, width, height)
        if hasattr(self.module, "setup"):
            self.module.setup()
        if hasattr(self.module, "resize"):
            self.module.resize(width, height)
            print("Module "+self.module.name+" has resize")
    
    def setModule(self, module):
        self.module = module
        self.title = module.name
        # check if module has a setup function
        self.module.initMod(self.pygamescreen, self.width, self.height)

        if hasattr(self.module, "setup"):
            self.module.setup()
            print("Module "+self.module.name+" has setup function")

##############################################
# Module Group
class ModuleGroup(object):
    def __init__(self, id=None, name=None):
        if id == None:
            # random chars from a-z and 0-9
            id = 'G_'+''.join(random.choice(string.ascii_lowercase + string.digits) for _ in range(5))
        self.id = id
        self.modules = []
        if name == None:
            name = str(id)
        self.name = name
        self.offset_x = 0 
        self.offset_y = 0

    def addModule(self, module):
        # if this is the first module, set the group offset to the module offset
        if len(self.modules) == 0:
            self.offset_x = module.x
            self.offset_y = module.y

        # check if module is already in the group
        if module not in self.modules:
            self.modules.append(module)
            module.groupId = self.id

    def removeModule(self, module):
        self.modules.remove(module)
        module.groupId = None



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
