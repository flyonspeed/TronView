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
import pygame, pygame_gui
from lib.common import shared
from lib import hud_utils
from lib.common.graphic.edit_save_load import load_screen_from_json
from lib.common.graphic.growl_manager import GrowlManager
from lib.common.dataship.dataship import Interface
from lib import hud_graphics

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
                    load_screen_from_json("screen.json")
                    shared.GrowlManager.add_message("Loaded screen from JSON")

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


        # Draw Growl messages
        shared.GrowlManager.draw(pygamescreen)

        #now make pygame update display.
        pygame.display.update()


    
# vi: modeline tabstop=8 expandtab shiftwidth=4 softtabstop=4 syntax=python


