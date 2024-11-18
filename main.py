#!/usr/bin/env python

#######################################################################################################################################
#######################################################################################################################################
# main.py
# 
# TronView main entry point.
# Configures and starts the main loop.
# Starts the input thread.
# Check which mode to run in (text, graphic, or edit)
#
# 1/23/2019 Refactor to make pretty.
# 10/22/2021 Name Change.
# 11/04/2024 Update for pygame-ce 2.5.1. (new editor mode)
#

import os, sys, time, threading, argparse, pygame, importlib
from lib import hud_utils
from lib.util import drawTimer
from lib.util import rpi_hardware
from lib.util import mac_hardware
from lib.common.text import text_mode
from lib.common.graphic import graphic_mode
from lib.common.graphic import edit_mode
from lib.common import shared # global shared objects stored here.
from lib.common.graphic import edit_save_load

#############################################
## Class: myThreadEfisInputReader
## Read input data on separate thread.
class myThreadEfisInputReader(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)

    def run(self):
        internalLoopCounter = 1
        input_count = len(shared.Inputs)
        while shared.Dataship.errorFoundNeedToExit == False:
            # loop through all inputs and read messages from them.
            for i in range(input_count):
                if(shared.Inputs[i].isPaused==True):
                    pass
                else:
                    shared.Inputs[i].readMessage(shared.Dataship)
                    shared.Inputs[i].time_stamp = shared.Inputs[i].time_stamp_string

            internalLoopCounter = internalLoopCounter - 1
            if internalLoopCounter < 1:
                internalLoopCounter = 1000
                checkInternals()
                shared.Dataship.traffic.cleanUp(shared.Dataship) # check if old traffic targets should be cleared up.

            if (shared.Inputs[0].PlayFile != None): # if playing back a file.. add a little delay so it's closer to real world time.
               time.sleep(.04)
            if shared.Dataship.textMode == True: # if in text mode.. lets delay a bit.. this keeps the cpu from heating up on my mac.
                time.sleep(.01)

#############################################
## Class: SingleInputReader
## Read input data on separate thread.
class SingleInputReader(threading.Thread):
    def __init__(self, input_index):
        threading.Thread.__init__(self)
        self.input_index = input_index
        
    def run(self):
        internalLoopCounter = 1
        print(f"Input Thread {self.input_index}: {shared.Inputs[self.input_index].name} started")
        while shared.Dataship.errorFoundNeedToExit == False:
            if shared.Inputs[self.input_index].isPaused == True:
                pass
            else:
                shared.Inputs[self.input_index].readMessage(shared.Dataship)
                shared.Inputs[self.input_index].time_stamp = shared.Inputs[self.input_index].time_stamp_string
                
                internalLoopCounter = internalLoopCounter - 1
                if self.input_index == 0:  # Only do cleanup on one thread
                    if internalLoopCounter < 1:
                        internalLoopCounter = 1000
                        checkInternals()
                        shared.Dataship.traffic.cleanUp(shared.Dataship)
                        #print(f"Input Thread: {self.input_index} {shared.Inputs[self.input_index].name} looped")

            if shared.Inputs[self.input_index].PlayFile != None: # if playing back a file.. add a little delay so it's closer to real world time.
                time.sleep(.04)
            if shared.Dataship.textMode == True:
                time.sleep(.01)

#############################################
## Function: checkInternals
# check internal values for this processor/machine..
def checkInternals():
    global isRunningOnPi, isRunningOnMac
    if isRunningOnPi == True:
        temp, msg = rpi_hardware.check_CPU_temp()
        shared.Dataship.internal.Temp = temp
        shared.Dataship.internal.LoadAvg = rpi_hardware.get_load_average()
        shared.Dataship.internal.MemFree = rpi_hardware.get_memory_usage()["free_memory"]
    elif isRunningOnMac == True:
        pass

#############################################
## Function: loadInput
# load input.
def loadInput(num,nameToLoad,playFile=None):
    print(("Input data module %d: %s"%(num,nameToLoad)))
    if hud_utils.findInput(nameToLoad) == False:
        print(("Input source %d not found: %s"%(num,nameToLoad)))
        hud_utils.findInput() # show available inputs
        sys.exit()
    module = ".%s" % (nameToLoad)
    mod = importlib.import_module(module, "lib.inputs")  # dynamically load class
    class_ = getattr(mod, nameToLoad)
    newInput = class_()
    newInput.PlayFile = playFile
    newInput.initInput(num,shared.Dataship)
    shared.Inputs[num] = newInput
    print(("Input %d loaded to shared.Inputs[%d]: %s"%(num,num,nameToLoad)))
    return newInput

#############################################
## Function: initDataShip
def initDataship():
    #global Dataship object.
    speed = hud_utils.readConfig("Formats", "speed_distance", "Standard")
    if speed == "Standard" or speed == "MPH":
        shared.Dataship.data_format = shared.Dataship.MPH
        print("speed distance format: mph ")
    elif speed == "Knots":
        shared.Dataship.data_format = shared.Dataship.KNOTS
        print("speed distance format: Knots ")
    elif speed == "Metric":
        shared.Dataship.data_format = shared.Dataship.METERS
        print("speed distance format: Meters ")

    temp = hud_utils.readConfig("Formats", "temperature", "C")
    if temp == "F":
        shared.Dataship.data_format_temp = shared.Dataship.TEMP_F
        print("temperature format: F ")
    elif temp == "C":
        shared.Dataship.data_format_temp = shared.Dataship.TEMP_C
        print("temperature format: C ")
    else :
        print("Unknown temperature format:"+temp)

#############################################
#############################################
# Main function.
#

ScreenNameToLoad = hud_utils.readConfig("Main", "screen", "Default")  # default screen to load
#DataInputToLoad = hud_utils.readConfig("DataInput", "inputsource", "none")  # input method
#DataInputToLoad2 = hud_utils.readConfig("DataInput2", "inputsource", "none")  # optional 2nd input
#DataInputToLoad3 = hud_utils.readConfig("DataInput3", "inputsource", "none")  # optional 3rd input

# check args passed in.
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="TronView")
    parser.add_argument('-t', action='store_true', help='Text mode')
    parser.add_argument('-e', action='store_true', help='Playback mode')
    parser.add_argument('-c', type=str, help='Custom example file name')
    parser.add_argument('--listlogs', action='store_true', help='List log data files')
    parser.add_argument('--listexamplelogs', action='store_true', help='List example log files')
    parser.add_argument('--listusblogs', action='store_true', help='List USB log data files')
    parser.add_argument('--in1', type=str, help='Input source 1')
    parser.add_argument('--in2', type=str, help='Input source 2')
    parser.add_argument('--in3', type=str, help='Input source 3')
    parser.add_argument('--playfile1', type=str, help='Playback file for input 1')
    parser.add_argument('--playfile2', type=str, help='Playback file for input 2')
    parser.add_argument('--playfile3', type=str, help='Playback file for input 3')
    parser.add_argument('-i', type=str, help='Input source')
    parser.add_argument('-s', '--screen', type=str, help='Screen to load')
    parser.add_argument('-l', action='store_true', help='List serial ports')
    parser.add_argument('--load-screen', type=str, help='Load screen from JSON file')
    parser.add_argument('--input-threads', action='store_true', help='Run each input on a separate thread (default is all on one input thread)')
    args = parser.parse_args()

    if args.t:
        print("Text mode")
        shared.Dataship.textMode = True
    if args.listlogs:
        hud_utils.listLogDataFiles()
        sys.exit()
    if args.listexamplelogs:
        hud_utils.listExampleLogs()
        sys.exit()
    if args.listusblogs:
        hud_utils.listUSBLogDataFiles()
        sys.exit()
    if args.e:
        # set all the inputs to playback mode.
        allPlayback = True
    else:
        allPlayback = False
    if args.c:  # this is the same as --playfile1        
        args.playfile1 = args.c
    if args.i:
        # this is the same as --in1
        loadInput(0,args.i,args.playfile1 if args.playfile1 else allPlayback)
    if args.in1:
        loadInput(0,args.in1,args.playfile1 if args.playfile1 else allPlayback)
    if args.in2:
        loadInput(1,args.in2,args.playfile2 if args.playfile2 else allPlayback)
    if args.in3:
        loadInput(2,args.in3,args.playfile3 if args.playfile3 else allPlayback)

    if args.screen:
        ScreenNameToLoad = args.screen
    if args.l:
        rpi_hardware.list_serial_ports(True)
        sys.exit()
    if args.load_screen:
        edit_mode.load_screen_from_json(args.load_screen)

    hud_utils.getDataRecorderDir(exitOnFail=True)
    hud_utils.setupDirs()
    isRunningOnPi = rpi_hardware.is_raspberrypi()
    if isRunningOnPi == True: 
        print("Running on RaspberryPi")
        shared.Dataship.internal.Hardware = "RaspberryPi"
        shared.Dataship.internal.OS = rpi_hardware.get_full_os_name()
        shared.Dataship.internal.OSVer = rpi_hardware.get_kernel_release()
    isRunningOnMac = mac_hardware.is_macosx()
    if isRunningOnMac == True: 
        import platform
        import os
        print("Running on Mac OSX")
        shared.Dataship.internal.Hardware = "Mac"
        shared.Dataship.internal.OS = "OSx"
        shared.Dataship.internal.OSVer = os.name + " " + platform.system() + " " + str(platform.release())
    shared.Dataship.internal.PythonVer = str(sys.version_info[0])+"."+str(sys.version_info[1])+"."+str(sys.version_info[2])
    shared.Dataship.internal.PyGameVer = pygame.version.ver
    

    if(shared.Dataship.errorFoundNeedToExit==True): sys.exit()
    # check and load screen module. (if not starting in text mode)

    initDataship()
    if(shared.Dataship.errorFoundNeedToExit==True): sys.exit()
    if not shared.Dataship.textMode:
        if hud_utils.findScreen(ScreenNameToLoad) == False:
            print(("Screen module not found: %s"%(ScreenNameToLoad)))
            hud_utils.findScreen() # show available screens
            sys.exit()
        graphic_mode.loadScreen(ScreenNameToLoad) # load and init screen
        #drawTimer.addGrowlNotice("1: %s"%(DataInputToLoad),3000,drawTimer.green,drawTimer.TOP_RIGHT)

    if args.input_threads:
        input_threads = []
        print("Starting input threads")
        for i in range(len(shared.Inputs)):
            if shared.Inputs[i] is not None:
                thread = SingleInputReader(i)
                thread.start()
                input_threads.append(thread)
    else:
        print("Running all inputs on single thread")
        thread1 = myThreadEfisInputReader()  # start thread for reading efis input.
        thread1.start()

    # testing.. start in edit mode.
    if shared.Dataship.textMode == False:
        shared.Dataship.editMode = True
        # check if /data/screens/screen.json exists.. if so load edit_save_load.load_screen_from_json()
        if os.path.exists("data/screens/screen.json"):
            edit_save_load.load_screen_from_json("screen.json")
        else:
            edit_save_load.load_screen_from_json("default.json",from_templates=True)

    # start main loop.
    while not shared.Dataship.errorFoundNeedToExit:
        if shared.Dataship.editMode == True:
            edit_mode.main_edit_loop()
        elif shared.Dataship.textMode == True:
            text_mode.main_text_mode()  # start main text loop
        else:
            graphic_mode.main_graphical()  # start main graphical loop
    
    # check if pygame is still running.
    if pygame.display.get_init() == True:
        pygame.quit()
        pygame.display.quit()

    for i in range(len(shared.Inputs)):
        if shared.Inputs[i] != None:
            shared.Inputs[i].closeInput(shared.Dataship)
    sys.exit()

# vi: modeline tabstop=8 expandtab shiftwidth=4 softtabstop=4 syntax=python
