#!/usr/bin/env python

#######################################################################################################################################
#######################################################################################################################################
# hud.py
#
# Python hud script for taking in efis data and displaying it in a custom HUD style format.
# Have Fun.
#
# 1/23/2019 Refactor to make pretty.  Christopher Jones
#
#


import math, os, sys, random
import argparse, pygame
import time
import threading, getopt
import ConfigParser
import importlib
import curses
from lib import hud_graphics
from lib import hud_utils
from lib import hud_text
from lib import aircraft

#############################################
## Function: main
## Main loop.  read global var data of efis data and display graphicaly
def main_graphical():
    global aircraft
    # init common things.
    maxframerate = hud_utils.readConfigInt("HUD", "maxframerate", 15)
    clock = pygame.time.Clock()

    ##########################################
    # Main graphics draw loop
    while not aircraft.errorFoundNeedToExit and not aircraft.textMode:
        clock.tick(maxframerate)
        for event in pygame.event.get():  # check for event like keyboard input.
            if event.type == pygame.QUIT:
                aircraft.errorFoundNeedToExit = True
            # KEY MAPPINGS
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_q:
                    aircraft.errorFoundNeedToExit = True
                elif event.key == pygame.K_PAGEUP:
                    loadScreen(hud_utils.findScreen("prev"))
                elif event.key == pygame.K_PAGEDOWN:
                    loadScreen(hud_utils.findScreen("next"))
                elif event.key == pygame.K_HOME:
                    loadScreen(hud_utils.findScreen("current"))
                elif event.key == pygame.K_t:
                    aircraft.textMode = True # switch to text mode?
                else:
                    CurrentScreen.processEvent(event)  # send this key command to the hud screen object

        # main draw loop.. clear screen then draw frame from current screen object.
        CurrentScreen.clearScreen()
        CurrentScreen.draw(aircraft)  # draw method for current screen object

    # once exists main loop, close down pygame. and exit.
    pygame.quit()
    pygame.display.quit()

#############################################
# Text mode Main loop
def main_text_mode():
    global aircraft
    threadKey = threadReadKeyboard() # read keyboard input for text mode using curses
    threadKey.start()

    hud_text.print_Clear()
    while not aircraft.errorFoundNeedToExit and aircraft.textMode:
        CurrentInput.printTextModeData(aircraft)

#############################################
## Class: myThreadEfisInputReader
## Read input data on seperate thread.
class myThreadEfisInputReader(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)

    def run(self):
        global CurrentInput, aircraft
        while aircraft.errorFoundNeedToExit == False:
            aircraft = CurrentInput.readMessage(aircraft)

#############################################
## Class: threadReadKeyboard
# thread for reading in data.  used during text mode.  curses module used for keyboard input.
class threadReadKeyboard(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.stdscr = curses.initscr()
        self.stdscr.keypad(1)    

    def run(self):
        global aircraft
        while not aircraft.errorFoundNeedToExit and aircraft.textMode:
            key = self.stdscr.getch()
            if key==ord('q'):
                curses.endwin()
                aircraft.errorFoundNeedToExit = True
            elif key==27:  # escape key.
                curses.endwin()
                aircraft.textMode = False
                loadScreen(hud_utils.findScreen("current")) # load current screen
            #elif key==339: #page up
            #elif key==338: #page up
            else:
                print("Key: %d \r\n"%(key))

#############################################
## Function: loadScreen
# load screen module name.  And init screen with screen size.
def loadScreen(ScreenNameToLoad):
    global CurrentScreen
    print("Loading screen module: %s"%(ScreenNameToLoad))
    module = ".%s" % (ScreenNameToLoad)
    mod = importlib.import_module(
        module, "lib.screens"
    )  # dynamically load screen class
    class_ = getattr(mod, ScreenNameToLoad)
    CurrentScreen = class_()
    pygamescreen, screen_size = hud_graphics.initDisplay(0)
    width, height = screen_size
    pygame.mouse.set_visible(False)  # hide the mouse
    CurrentScreen.initDisplay(
        pygamescreen, width, height
    )  # tell the screen we are about to start.    

#############################################
#############################################
# Hud start code.
#

# load hud.cfg file if it exists.
configParser = ConfigParser.RawConfigParser()
configParser.read("hud.cfg")
aircraft = aircraft.Aircraft()
ScreenNameToLoad = hud_utils.readConfig("Hud", "screen", "DefaultScreen")  # default screen to load
DataInputToLoad = hud_utils.readConfig("DataInput", "inputsource", "none")  # input method

# check args passed in.
if __name__ == "__main__":
    #print 'ARGV      :', sys.argv[1:]
    try:
        opts, args = getopt.getopt(
            sys.argv[1:], "hs:i:tec:"
        )
    except getopt.GetoptError:
        print("unknown command line args given..")
        hud_utils.showArgs()
    for opt, arg in opts:
        #print("opt: %s  arg: %s"%(opt,arg))
        if opt == '-t':
            aircraft.textMode = True
        if opt == '-e':
            aircraft.demoMode = True
        if opt == '-c':  #custom example file name.
            aircraft.demoMode = True
            aircraft.demoFile = arg
        if opt in ("-h", "--help"):
            hud_utils.showArgs()
        if opt in ("-i"):
            DataInputToLoad = arg
        if opt == "-s":
            ScreenNameToLoad = arg
    if DataInputToLoad == "none":
        hud_utils.showArgs()

    # Check and load input source
    if hud_utils.findInput(DataInputToLoad) == False:
        print("Input module not found: %s"%(DataInputToLoad))
        hud_utils.findInput() # show available inputs
        sys.exit()
    print("Input data module: %s"%(DataInputToLoad))
    module = ".%s" % (DataInputToLoad)
    mod = importlib.import_module(module, "lib.inputs")  # dynamically load class
    class_ = getattr(mod, DataInputToLoad)
    CurrentInput = class_()
    CurrentInput.initInput(aircraft)

    # check and load screen module. (if not starting in text mode)
    if not aircraft.textMode:
        if hud_utils.findScreen(ScreenNameToLoad) == False:
            print("Screen module not found: %s"%(ScreenNameToLoad))
            hud_utils.findScreen() # show available screens
            sys.exit()
        loadScreen(ScreenNameToLoad) # load and init screen

    thread1 = myThreadEfisInputReader()  # start thread for reading efis input.
    thread1.start()
    while not aircraft.errorFoundNeedToExit:
        if aircraft.textMode == True:
            main_text_mode()  # start main text loop
        else:
            main_graphical()  # start main graphical loop
    CurrentInput.closeInput(aircraft) # close the input source
    sys.exit()
# vi: modeline tabstop=8 expandtab shiftwidth=4 softtabstop=4 syntax=python
