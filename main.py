#!/usr/bin/env python

#######################################################################################################################################
#######################################################################################################################################
# main.py
#
# Read multiple formats of EFIS data, Engine Data, Flight data, or play back existing flight data 
# Display data on screen or HUD.
# All data is feed in and formated to a common data format (into aircraft object).  Then screens read data from aircarft object to display.
#
# 1/23/2019 Refactor to make pretty.
# 10/22/2021 Name Change.   
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
            if(shared.CurrentInput2 != None): # if there is a 2nd input then read message from that too.
                shared.aircraft = shared.CurrentInput2.readMessage(shared.aircraft)
            internalLoopCounter = internalLoopCounter - 1
            if internalLoopCounter < 0:
                internalLoopCounter = 1500
                checkInternals()
                shared.aircraft.traffic.cleanUp() # check if old traffic targets should be cleared up.
            if shared.aircraft.textMode == True: # if in text mode.. lets delay a bit.. this keeps the cpu from heating up on my mac.
                time.sleep(.01)


#############################################
## Function: checkInternals
# check internal values for this processor/machine..
def checkInternals():
    global isRunningOnPi, isRunningOnMac
    if isRunningOnPi == True:
        temp, msg = rpi_hardware.check_CPU_temp()
        shared.aircraft.internal.Temp = temp
        shared.aircraft.internal.LoadAvg = rpi_hardware.get_load_average()
        shared.aircraft.internal.MemFree = rpi_hardware.get_memory_usage()["free_memory"]
    elif isRunningOnMac == True:
        pass

#############################################
## Function: loadInput
# load input.
def loadInput(num,nameToLoad):
    print(("Input data module %d: %s"%(num,nameToLoad)))
    module = ".%s" % (nameToLoad)
    mod = importlib.import_module(module, "lib.inputs")  # dynamically load class
    class_ = getattr(mod, nameToLoad)
    newInput = class_()
    newInput.initInput(num,shared.aircraft)
    shared.aircraft.inputs[num].Name = newInput.name
    shared.aircraft.inputs[num].Ver = newInput.version
    shared.aircraft.inputs[num].InputType = newInput.inputtype
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

ScreenNameToLoad = hud_utils.readConfig("Main", "screen", "Default")  # default screen to load
DataInputToLoad = hud_utils.readConfig("DataInput", "inputsource", "none")  # input method
DataInputToLoad2 = hud_utils.readConfig("DataInput2", "inputsource", "none")  # optional 2nd input

# check args passed in.
if __name__ == "__main__":
    #print 'ARGV      :', sys.argv[1:]
    try:
        opts, args = getopt.getopt(
            sys.argv[1:], "hs:i:tec:lr",['i1=','i2=','pf1=','pf2=']
        )
    except getopt.GetoptError:
        print("unknown command line args given..")
        hud_utils.showArgs()
    for opt, arg in opts:
        #print("opt: %s  arg: %s"%(opt,arg))
        if opt == '-t':
            shared.aircraft.textMode = True
        if opt == '-e':
            shared.aircraft.inputs[0].PlayFile = True
        if opt == '-c':  #custom example file name.
            shared.aircraft.inputs[0].PlayFile = arg
        if opt == '-r':  # list example files
            hud_utils.listLogDataFiles()
            sys.exit()
        if opt in ("", "--i1"):
            DataInputToLoad = arg
        if opt in ("", "--i2"):
            DataInputToLoad2 = arg
        if opt in ("", "--pf1"):
            shared.aircraft.inputs[0].PlayFile = arg
            print("Input1 playing log file: "+arg)
        if opt in ("", "--pf2"):
            shared.aircraft.inputs[1].PlayFile = arg
            print("Input2 playing log file: "+arg)
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
    if isRunningOnPi == True: 
        print("Running on RaspberryPi")
        shared.aircraft.internal.Hardware = "RaspberryPi"
        shared.aircraft.internal.OS = rpi_hardware.get_full_os_name()
        shared.aircraft.internal.OSVer = rpi_hardware.get_kernel_release()
    isRunningOnMac = mac_hardware.is_macosx()
    if isRunningOnMac == True: 
        import platform
        import os
        print("Running on Mac OSX")
        shared.aircraft.internal.Hardware = "Mac"
        shared.aircraft.internal.OS = "OSx"
        shared.aircraft.internal.OSVer = os.name + " " + platform.system() + " " + str(platform.release())
    shared.aircraft.internal.PythonVer = str(sys.version_info[0])+"."+str(sys.version_info[1])+"."+str(sys.version_info[2])
    shared.aircraft.internal.PyGameVer = pygame.version.ver
    if DataInputToLoad == "none":
        print("No input source given")
        hud_utils.showArgs()
    # Check and load input source
    if hud_utils.findInput(DataInputToLoad) == False:
        print(("Input source not found: %s"%(DataInputToLoad)))
        hud_utils.findInput() # show available inputs
        sys.exit()
    shared.CurrentInput = loadInput(0,DataInputToLoad)
    if DataInputToLoad2 != "none":
        if(DataInputToLoad2==DataInputToLoad): print("Skipping 2nd Input source : same as input 1")
        else:
            if hud_utils.findInput(DataInputToLoad2) == False:
                print(("Input source 2 not found: %s"%(DataInputToLoad2)))
                hud_utils.findInput() # show available inputs
                sys.exit()
            shared.CurrentInput2 = loadInput(1,DataInputToLoad2)
    if(shared.aircraft.errorFoundNeedToExit==True): sys.exit()
    # check and load screen module. (if not starting in text mode)
    initAircraft()
    if(shared.aircraft.errorFoundNeedToExit==True): sys.exit()
    if not shared.aircraft.textMode:
        if hud_utils.findScreen(ScreenNameToLoad) == False:
            print(("Screen module not found: %s"%(ScreenNameToLoad)))
            hud_utils.findScreen() # show available screens
            sys.exit()
        graphic_mode.loadScreen(ScreenNameToLoad) # load and init screen
        drawTimer.addGrowlNotice("1: %s"%(DataInputToLoad),3000,drawTimer.green,drawTimer.TOP_RIGHT)

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
