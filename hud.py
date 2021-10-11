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
import configparser
import importlib
import curses
import inspect
from lib import hud_graphics
from lib import hud_utils
from lib import hud_text
from lib import aircraft
from lib import smartdisplay
from lib.util.virtualKeyboard import VirtualKeyboard
from lib.util import drawTimer
from lib.util import rpi_hardware
from lib.util import mac_hardware
from lib.common.text import text_mode
from lib.common.graphic import graphic_mode
from lib.common import shared # global shared objects stored here.



#############################################
## Class: myThreadEfisInputReader
## Read input data on seperate thread.
class myThreadEfisInputReader(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)

    def run(self):
        #global CurrentInput, CurrentInput2, aircraft
        internalLoopCounter = 1
        while shared.aircraft.errorFoundNeedToExit == False:
            shared.aircraft = shared.CurrentInput.readMessage(shared.aircraft)
            internalLoopCounter = internalLoopCounter - 1
            if internalLoopCounter < 0:
                internalLoopCounter = 500
                checkInternals()

#############################################
## Function: checkInternals
# check internal values for this processor/machine..
def checkInternals():
    global isRunningOnPi, isRunningOnMac
    if isRunningOnPi == True:
        temp, msg = rpi_hardware.check_CPU_temp()
        shared.aircraft.internal.Temp = temp
    elif isRunningOnMac == True:
        shared.aircraft.internal.Temp = mac_hardware.check_CPU_temp()

#############################################
## Function: loadInput
# load input.
def loadInput(num,nameToLoad):
    #global aircraft
    print(("Input data module %d: %s"%(num,nameToLoad)))
    module = ".%s" % (nameToLoad)
    mod = importlib.import_module(module, "lib.inputs")  # dynamically load class
    class_ = getattr(mod, nameToLoad)
    newInput = class_()
    newInput.initInput(shared.aircraft)
    return newInput

#############################################
## Function: initAircraft
def initAircraft():
    #global aircraft
    speed = hud_utils.readConfig("Formats", "speed_distance", "Standard")
    if speed == "Standard" or speed == "MPH":
        shared.aircraft.data_format = shared.aircraft.MPH
        print("speed distance format: mph ")
    elif speed == "Knots":
        shared.aircraft.data_format = shared.aircraft.KNOTS
        print("speed distance format: Knots ")
    elif speed == "Metric":
        shared.aircraft.data_format = shared.aircraft.METERS
        print("speed distance format: Meters ")

    temp = hud_utils.readConfig("Formats", "temperature", "C")
    if temp == "F":
        shared.aircraft.data_format_temp = shared.aircraft.TEMP_F
        print("temperature format: F ")
    elif temp == "C":
        shared.aircraft.data_format_temp = shared.aircraft.TEMP_C
        print("temperature format: C ")
    else :
        print("Unknown temperature format:"+temp)

#############################################
#############################################
# Main function.
#

ScreenNameToLoad = hud_utils.readConfig("HUD", "screen", "Default")  # default screen to load
DataInputToLoad = hud_utils.readConfig("DataInput", "inputsource", "none")  # input method
DataInputToLoad2 = hud_utils.readConfig("DataInput2", "inputsource", "none")  # optional 2nd input

# check args passed in.
if __name__ == "__main__":
    #print 'ARGV      :', sys.argv[1:]
    try:
        opts, args = getopt.getopt(
            sys.argv[1:], "hs:i:tec:lr",
        )
    except getopt.GetoptError:
        print("unknown command line args given..")
        hud_utils.showArgs()
    for opt, arg in opts:
        #print("opt: %s  arg: %s"%(opt,arg))
        if opt == '-t':
            shared.aircraft.textMode = True
        if opt == '-e':
            shared.aircraft.demoMode = True
        if opt == '-c':  #custom example file name.
            shared.aircraft.demoMode = True
            shared.aircraft.demoFile = arg
        if opt == '-r':  # list example files
            hud_utils.listLogDataFiles()
            sys.exit()
        if opt in ("-h", "--help"):
            hud_utils.showArgs()
        if opt in ("-i"):
            DataInputToLoad = arg
        if opt == "-s":
            ScreenNameToLoad = arg
        if opt == "-l":
            rpi_hardware.list_serial_ports(True)
            sys.exit()
    isRunningOnPi = rpi_hardware.is_raspberrypi()
    if isRunningOnPi == True: print("Running on RaspberryPi")
    isRunningOnMac = mac_hardware.is_macosx()
    if isRunningOnMac == True: print("Running on Mac OSX")
    if DataInputToLoad == "none":
        print("No inputsource given")
        hud_utils.showArgs()
    # Check and load input source
    if hud_utils.findInput(DataInputToLoad) == False:
        print(("Input module not found: %s"%(DataInputToLoad)))
        hud_utils.findInput() # show available inputs
        sys.exit()
    shared.CurrentInput = loadInput(1,DataInputToLoad)
    if DataInputToLoad2 != "none":
        shared.CurrentInput2 = loadInput(2,DataInputToLoad2)
    # check and load screen module. (if not starting in text mode)
    initAircraft()
    if not shared.aircraft.textMode:
        if hud_utils.findScreen(ScreenNameToLoad) == False:
            print(("Screen module not found: %s"%(ScreenNameToLoad)))
            hud_utils.findScreen() # show available screens
            sys.exit()
        graphic_mode.loadScreen(ScreenNameToLoad) # load and init screen
        drawTimer.addGrowlNotice("Datasource: %s"%(DataInputToLoad),3000,drawTimer.green,drawTimer.TOP_RIGHT)

    thread1 = myThreadEfisInputReader()  # start thread for reading efis input.
    thread1.start()
    # start main loop.
    while not shared.aircraft.errorFoundNeedToExit:
        if shared.aircraft.textMode == True:
            text_mode.main_text_mode()  # start main text loop
        else:
            graphic_mode.main_graphical()  # start main graphical loop
    shared.CurrentInput.closeInput(shared.aircraft) # close the input source
    sys.exit()
# vi: modeline tabstop=8 expandtab shiftwidth=4 softtabstop=4 syntax=python
