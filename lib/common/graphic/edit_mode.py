#!/usr/bin/env python

#######################################################################################################################################
#######################################################################################################################################
# edit mode
#
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


# TronViewModule
class TVModule(object):
    def __init__(self, type, title, module, x, y, width, height):
        self.type = type
        self.title = title
        self.module = module
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.selected = False

COLOR_INACTIVE = (30, 30, 30)
COLOR_ACTIVE = (100, 200, 255)
COLOR_LIST_INACTIVE = (100, 100, 100)
COLOR_LIST_ACTIVE = (100, 150, 100) # green

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
        if not self.visible:
            return
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
                self.value = self.options[i]
                break

        if not self.menu_active and self.active_option == -1:
            self.draw_menu = False

        for event in event_list:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if self.menu_active:
                    self.draw_menu = not self.draw_menu
                elif self.draw_menu and self.active_option >= 0:
                    self.draw_menu = False
                    return self.active_option
        
        return -1

    def toggle(self):
        self.visible = not self.visible
    


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

    # if shared.CurrentScreen.Modules exists.. if it doesn't create it as array
    if not hasattr(shared.CurrentScreen, "Modules"):
        shared.CurrentScreen.Modules = []
        # create _class in Modules that has name,id, x,y, width, height, and color.
        shared.CurrentScreen.Modules.append(
            TVModule(
                "Heading",
                "Heading",
                "heading",
                10,
                10,
                100,
                100,
            )
        )

    # list of modules
    listModules = ["Heading", "Roll", "Horizon", "AOA", "SlipSkid", "Wind", "TrafficScope", "CDI", "GCross", "Calibration", "Test"]

    # clear screen using pygame
    pygamescreen = pygame.display.set_mode((shared.smartdisplay.x_end, shared.smartdisplay.y_end))
    pygamescreen.fill((0, 0, 0))
    pygame.display.update()

    selected_module = None
    dragging = False # are we dragging a module?
    offset_x = 0 # x offset for dragging
    offset_y = 0 # y offset for dragging
    resizing = False  # are we resizing a module?
    dropdown = None # dropdown menu for module selection (if any)

    ##########################################
    # Main edit draw loop
    while not shared.aircraft.errorFoundNeedToExit and not exit_edit_mode:
        clock.tick(maxframerate)
        event_list = pygame.event.get()
        for event in event_list:  # check for event like keyboard input.
            if event.type == pygame.QUIT:
                shared.aircraft.errorFoundNeedToExit = True
            # KEY MAPPINGS
            if event.type == pygame.KEYDOWN:
                mods = pygame.key.get_mods()
                #### Press 3 - Cycle traffic modes.
                if event.key == pygame.K_3 or event.key == pygame.K_KP3:
                    # do nothing
                    pass
                elif event.key == pygame.K_q or event.key == pygame.K_ESCAPE:
                    shared.aircraft.errorFoundNeedToExit = True
                elif event.key == pygame.K_e:
                    shared.aircraft.editMode = False  # exit edit mode
                    exit_edit_mode = True
                elif event.key == pygame.K_a:
                    # add a new module
                    mx, my = pygame.mouse.get_pos()
                    shared.CurrentScreen.Modules.append(
                        TVModule(
                            "New",
                            "New",
                            "new",
                            mx,
                            my,
                            100,
                            100,
                        )
                    )

            if event.type == pygame.MOUSEBUTTONDOWN:
                mx, my = pygame.mouse.get_pos()
                print("Mouse Click %d x %d" % (mx, my))

                # Check if the mouse click is inside any module
                for module in shared.CurrentScreen.Modules:
                    if module.x <= mx <= module.x + module.width and module.y <= my <= module.y + module.height:
                        #################
                        # RESIZE MODULE
                        if mx >= module.x + module.width - 10 and my >= module.y + module.height - 10:
                            # Click is in the bottom right corner, start resizing
                            selected_module = module
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
            # Mouse up
            elif event.type == pygame.MOUSEBUTTONUP:
                dragging = False
                resizing = False
                selected_module = None
                for module in shared.CurrentScreen.Modules:
                    module.selected = False

            # Mouse move.. resize or move the module??
            elif event.type == pygame.MOUSEMOTION:
                if dragging and selected_module:
                    mx, my = pygame.mouse.get_pos()
                    selected_module.x = mx - offset_x
                    selected_module.y = my - offset_y
                    # clear screen using pygame
                    pygamescreen.fill((0, 0, 0))
                elif resizing and selected_module:
                    mx, my = pygame.mouse.get_pos()
                    selected_module.width = mx - selected_module.x
                    selected_module.height = my - selected_module.y
                    # clear screen using pygame
                    pygamescreen.fill((0, 0, 0))

        if dropdown:
            selection = dropdown.update(event_list)

        pygamescreen.fill((0, 0, 0)) # clear screen
        # draw the modules
        for module in shared.CurrentScreen.Modules:
            color = (255, 0, 0)
            if module.selected:
                color = (0, 255, 0)
            # draw the module
            pygame.draw.rect(pygamescreen, color, (module.x, module.y, module.width, module.height), 1)
            # draw the module title
            text = debug_font.render(module.title, True, (255, 255, 255))
            pygamescreen.blit(text, (module.x + 5, module.y + 5))
            # draw a little resize handle in the bottom right corner
            pygame.draw.rect(pygamescreen, color, (module.x + module.width - 10, module.y + module.height - 10, 10, 10), 1)

            # Draw the dropdown menu if visible
            if dropdown and dropdown.visible and selected_module == module:
                if dropdown.value is not None:
                    module.title = dropdown.value  # Update the module title
                else:
                    module.title = "none"
                dropdown.draw(pygamescreen)

        
        #now make pygame update display.
        pygame.display.update()


# vi: modeline tabstop=8 expandtab shiftwidth=4 softtabstop=4 syntax=python
