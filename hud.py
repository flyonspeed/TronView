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
from lib import hud_graphics
from lib import hud_utils

#############################################
## Class: Aircraft
class Aircraft(object):
    def __init__(self):
        self.pitch = 0.0
        self.roll = 0.0
        self.ias = 0
        self.tas = 0
        self.alt = 0
        self.agl = 0
        self.PALT = 0
        self.BALT = 0
        self.aoa = 0
        self.mag_head = 0
        self.gndtrack = 0
        self.baro = 0
        self.baro_diff = 0
        self.vsi = 0
        self.gndspeed = 0

        self.msg_count = 0
        self.errorFoundNeedToExit = False


#############################################
## Function: main
## Main loop.  read global var data of efis data and display graphicaly
def main():
    global aircraft
    # init common things.
    maxframerate = hud_utils.readConfigInt("HUD", "maxframerate", 15)
    pygamescreen, screen_size = hud_graphics.initDisplay(0)
    width, height = screen_size
    pygame.mouse.set_visible(False)  # hide the mouse
    CurrentScreen.initDisplay(
        pygamescreen, width, height
    )  # tell the screen we are about to start.
    clock = pygame.time.Clock()

    ##########################################
    # Main graphics draw loop
    while not aircraft.errorFoundNeedToExit:
        clock.tick(maxframerate)
        for event in pygame.event.get():  # check for event like keyboard input.
            if event.type == pygame.QUIT:
                thread1.stop()
                aircraft.errorFoundNeedToExit = True
            # KEY MAPPINGS
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_q:
                    aircraft.errorFoundNeedToExit = True
                else:
                    CurrentScreen.processEvent(
                        event
                    )  # send this key command to the hud screen object

        # main draw loop.. clear screen then draw frame from current screen object.
        CurrentScreen.clearScreen()
        CurrentScreen.draw(aircraft)  # draw method for current screen object

    # once exists main loop, close down pygame. and exit.
    pygame.quit()
    pygame.display.quit()
    os.system("killall python")


#############################################
## Class: myThreadSerialReader
## Read serial input data on seperate thread.
class myThreadSerialReader(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)

    def run(self):
        global CurrentInput, aircraft
        while not aircraft.errorFoundNeedToExit:
            aircraft = CurrentInput.readMessage(aircraft)

        pygame.display.quit()
        pygame.quit()
        # sys.stdout.flush()
        # sys.stderr.flush()
        sys.exit()


#############################################
#############################################
# Hud start code.
#
#

# redirct output to output.log
# sys.stdout = open('output.log', 'w')
# sys.stderr = open('output_error.log', 'w')


# load hud.cfg file if it exists.
configParser = ConfigParser.RawConfigParser()
configParser.read("hud.cfg")
aircraft = Aircraft()
ScreenNameToLoad = hud_utils.readConfig("Hud", "screen", "DefaultScreen")  # default screen to load
DataInputToLoad = hud_utils.readConfig("DataInput", "inputsource", "none")  # input method

# check args passed in.
if __name__ == "__main__":
    # print 'ARGV      :', sys.argv[1:]
    try:
        opts, args = getopt.getopt(
            sys.argv[1:], "h:s:i:z", ["help=", "screen=", "inputsource=", "zdummy="]
        )
    except getopt.GetoptError:
        hud_utils.showArgs()
    for opt, arg in opts:
        # print arg
        if opt in ("-h", "--help"):
            hud_utils.showArgs()
        elif opt in ("-i"):
            DataInputToLoad = arg
        if opt == "-s":
            ScreenNameToLoad = arg
    if DataInputToLoad == "none":
        hud_utils.showArgs()

    # Check and load input source
    if hud_utils.findInput(DataInputToLoad) == False:
        print("Input module not found: %s"%(DataInputToLoad))
        hud_utils.findInput()
        sys.exit()
    print("Input data module: %s"%(DataInputToLoad))
    module = ".%s" % (DataInputToLoad)
    mod = importlib.import_module(module, "lib.inputs")  # dynamically load class
    class_ = getattr(mod, DataInputToLoad)
    CurrentInput = class_()
    CurrentInput.initInput()

    # check and load screen module.
    if hud_utils.findScreen(ScreenNameToLoad) == False:
        print("Screen module not found: %s"%(ScreenNameToLoad))
        hud_utils.findScreen()
        sys.exit()
    print("Loading screen module: %s"%(ScreenNameToLoad))
    module = ".%s" % (ScreenNameToLoad)
    mod = importlib.import_module(
        module, "lib.screens"
    )  # dynamically load screen class
    class_ = getattr(mod, ScreenNameToLoad)
    CurrentScreen = class_()

    thread1 = myThreadSerialReader()  # start thread for reading input.
    thread1.start()
    sys.exit(main())  # start main loop

# vi: modeline tabstop=8 expandtab shiftwidth=4 softtabstop=4 syntax=python
