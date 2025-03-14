#!/usr/bin/env python

#######################################################################################################################################
#######################################################################################################################################
# Graphic mode
# Topher 2024
#######################################################################################################################################
####################################################################################################################################### 
import os
import threading
import math, os, sys, random
import argparse, pygame
import time
import configparser
import importlib
import curses
import pygame
from lib.common import shared
from lib import hud_utils
from lib.common.graphic.edit_save_load import load_screen_from_json
from lib.common.graphic.growl_manager import GrowlManager
from lib.common.dataship.dataship import Interface
from lib import hud_graphics
from lib.common.graphic.edit_dropdown import DropDown


#############################################
## Function: main loop
def main_graphical():
    pygamescreen, size = hud_graphics.initDisplay()

    # init common things.
    maxframerate = hud_utils.readConfigInt("Main", "maxframerate", 40)
    clock = pygame.time.Clock()

    exit_graphic_mode = False
    pygame.mouse.set_visible(True)
    print("Entering Graphic Mode")
    shared.GrowlManager.initScreen()
    # clear screen using pygame
    pygamescreen.fill((0, 0, 0))
    pygame.display.update()

    # create a dropdown menu
    active_dropdown = None

    # if shared.CurrentScreen.ScreenObjects exists.. if it doesn't create it as array
    if not hasattr(shared.CurrentScreen, "ScreenObjects"):
        shared.CurrentScreen.ScreenObjects = []

    ############################################################################################
    ############################################################################################
    # Main draw loop
    while not shared.Dataship.errorFoundNeedToExit and not exit_graphic_mode:
        pygamescreen.fill((0, 0, 0)) # clear screen
        event_list = pygame.event.get() # get all events
        time_delta = clock.tick(maxframerate) / 1000.0 # get the time delta and limit the framerate.

        ## loop through events and process them
        for event in event_list:

            # check dropdown menu if visible
            # we use a global dropdown menu for some dropdown needs.
            if active_dropdown and active_dropdown.visible:
                # send the event to the dropdown menu (not using the return values because we use the callback functions)
                active_dropdown.update(event_list)
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    active_dropdown = None
                continue

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

            ############################################################################################
            # KEY MAPPINGS
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_q:
                    shared.Dataship.errorFoundNeedToExit = True
                elif event.key == pygame.K_d:
                    shared.Dataship.debug_mode += 1
                    if shared.Dataship.debug_mode > 2:
                        shared.Dataship.debug_mode = 0
                    print("Debug mode: %d" % shared.Dataship.debug_mode)
                    shared.GrowlManager.add_message("Debug mode set : %d" % shared.Dataship.debug_mode)
                # Exit View Mode, enter Edit Mode
                elif event.key == pygame.K_e:
                    shared.Dataship.interface = Interface.EDITOR  # enter edit mode
                    exit_graphic_mode = True
                # LOAD SCREEN FROM JSON
                elif event.key == pygame.K_l:
                    mx, my = pygame.mouse.get_pos()
                    print("Load screen key pressed at %d x %d" % (mx, my))
                    def load_template_callback(dropdown,id, index_path, text):
                        print("Load template callback: %s" % text)
                        if index_path[0] == 0:
                            shared.CurrentScreen.clear()
                            shared.GrowlManager.add_message("Cleared screen")
                        elif index_path[0] == 1:
                            print("Loading template: %s" % text)
                            load_screen_from_json(text, from_templates=True)
                            shared.GrowlManager.add_message("Loaded template: %s" % text)
                        else:
                            load_screen_from_json(text, from_templates=False)
                            shared.GrowlManager.add_message("Loaded user screen: %s" % text)
                        # hide the dropdown menu
                        active_dropdown = None
                    active_dropdown = DropDown(
                        id="dropdown_load_screen",
                        x=mx, y=my, w=140, h=30,
                        menuTitle="Load Screen",
                        callback=load_template_callback)
                    root_dir = os.path.dirname(os.path.abspath(__file__))
                    active_dropdown.load_file_dir_as_options(os.path.join(root_dir+"/../../../data/screens", ""))
                    active_dropdown.insert_option("CLEAR SCREEN", 0)
                    active_dropdown.insert_option("TEMPLATES", 1)
                    active_dropdown.load_file_dir_as_options(os.path.join(root_dir+"/../../screens", "templates"), index_path=[1])
                    active_dropdown.visible = True
                    active_dropdown.draw_menu = True

            # check for Mouse events - just for clicking screen objects
            if event.type == pygame.MOUSEBUTTONDOWN or event.type == pygame.FINGERDOWN:
                if event.type == pygame.FINGERDOWN:
                    mx, my = event.x, event.y
                else:
                    mx, my = pygame.mouse.get_pos()
                if shared.Dataship.debug_mode > 0:
                    print("Click %d x %d" % (mx, my))

                # Check if the mouse click is inside any screenObject
                for sObject in shared.CurrentScreen.ScreenObjects[::-1]:
                    if sObject.x <= mx <= sObject.x + sObject.width and sObject.y <= my <= sObject.y + sObject.height:
                        selected_screen_object = sObject
                        # Send click to the screen object
                        sObject.click(shared.Dataship, mx - sObject.x, my - sObject.y)
                        break

        # Draw the modules
        for sObject in shared.CurrentScreen.ScreenObjects:
            sObject.draw(shared.Dataship, shared.smartdisplay, False)  # Never draw toolbar in view mode

        if active_dropdown and active_dropdown.visible:
            # Create a semi-transparent overlay
            screen_width = shared.smartdisplay.x_end
            screen_height = shared.smartdisplay.y_end
            overlay = pygame.Surface((screen_width, screen_height))
            overlay.fill((0, 0, 0))  # Black background
            overlay.set_alpha(200)    # 50% transparency (0-255)
            pygamescreen.blit(overlay, (0, 0))            
            active_dropdown.draw(pygamescreen)


        # Draw Growl messages
        shared.GrowlManager.draw(pygamescreen)

        #now make pygame update display.
        pygame.display.update()


    
# vi: modeline tabstop=8 expandtab shiftwidth=4 softtabstop=4 syntax=python


