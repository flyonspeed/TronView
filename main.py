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
## Class: InputReader
## Read input data on seperate thread.
class InputReader(threading.Thread):
    def __init__(self, input_source, input_index):
        threading.Thread.__init__(self)
        self.input_source = input_source
        self.input_index = input_index
        
    def run(self):
        internal_loop_counter = 1
        while not shared.Dataship.errorFoundNeedToExit:
            if not self.input_source.isPaused:
                shared.Dataship = self.input_source.readMessage(shared.Dataship)
                shared.Dataship.inputs[self.input_index].time_stamp = self.input_source.time_stamp_string
                
                internal_loop_counter -= 1
                if internal_loop_counter < 0:
                    internal_loop_counter = 100
                    if self.input_index == 0:  # Only check internals on primary input thread
                        checkInternals()
                        shared.Dataship.traffic.cleanUp(shared.Dataship)

            if self.input_source.input_logFileName != None:
                time.sleep(.04)
            if shared.Dataship.textMode:
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
def loadInput(num,nameToLoad):
    print(("Input data module %d: %s"%(num,nameToLoad)))
    module = ".%s" % (nameToLoad)
    mod = importlib.import_module(module, "lib.inputs")  # dynamically load class
    class_ = getattr(mod, nameToLoad)
    newInput = class_()
    newInput.initInput(num,shared.Dataship)
    shared.Dataship.inputs[num].Name = newInput.name
    shared.Dataship.inputs[num].Ver = newInput.version
    shared.Dataship.inputs[num].InputType = newInput.inputtype
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
DataInputToLoad = hud_utils.readConfig("DataInput", "inputsource", "none")  # input method
DataInputToLoad2 = hud_utils.readConfig("DataInput2", "inputsource", "none")  # optional 2nd input
DataInputToLoad3 = hud_utils.readConfig("DataInput3", "inputsource", "none")  # optional 3rd input

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
    args = parser.parse_args()

    if args.t:
        print("Text mode")
        shared.Dataship.textMode = True
    if args.e:
        shared.Dataship.inputs[0].PlayFile = True
    if args.c:
        shared.Dataship.inputs[0].PlayFile = args.c
    if args.listlogs:
        hud_utils.listLogDataFiles()
        sys.exit()
    if args.listexamplelogs:
        hud_utils.listExampleLogs()
        sys.exit()
    if args.listusblogs:
        hud_utils.listUSBLogDataFiles()
        sys.exit()
    if args.in1:
        DataInputToLoad = args.in1
    if args.in2:
        DataInputToLoad2 = args.in2
    if args.in3:
        DataInputToLoad3 = args.in3
    if args.playfile1:
        shared.Dataship.inputs[0].PlayFile = args.playfile1
        print("Input1 playing log file: "+args.playfile1)
    if args.playfile2:
        shared.Dataship.inputs[1].PlayFile = args.playfile2
        print("Input2 playing log file: "+args.playfile2)
    if args.playfile3:
        shared.Dataship.inputs[2].PlayFile = args.playfile3
        print("Input3 playing log file: "+args.playfile3)
    if args.i:
        DataInputToLoad = args.i
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
        #if(DataInputToLoad2==DataInputToLoad): print("Skipping 2nd Input source : same as input 1")
        #else:
            if hud_utils.findInput(DataInputToLoad2) == False:
                print(("Input source 2 not found: %s"%(DataInputToLoad2)))
                hud_utils.findInput() # show available inputs
                sys.exit()
            shared.CurrentInput2 = loadInput(1,DataInputToLoad2)
    if DataInputToLoad3 != "none":
        #if(DataInputToLoad3==DataInputToLoad): print("Skipping 3rd Input source : same as input 1")
        #else:
            if hud_utils.findInput(DataInputToLoad3) == False:
                print(("Input source 3 not found: %s"%(DataInputToLoad2)))
                hud_utils.findInput() # show available inputs
                sys.exit()
            shared.CurrentInput3 = loadInput(2,DataInputToLoad3)
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
        drawTimer.addGrowlNotice("1: %s"%(DataInputToLoad),3000,drawTimer.green,drawTimer.TOP_RIGHT)

    threads = []
    if shared.CurrentInput:
        thread1 = InputReader(shared.CurrentInput, 0)
        thread1.start()
        threads.append(thread1)

    if shared.CurrentInput2:
        thread2 = InputReader(shared.CurrentInput2, 1) 
        thread2.start()
        threads.append(thread2)

    if shared.CurrentInput3:
        thread3 = InputReader(shared.CurrentInput3, 2)
        thread3.start()
        threads.append(thread3)

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

    shared.CurrentInput.closeInput(shared.Dataship) # close the input source
    if DataInputToLoad2 != "none" and shared.CurrentInput2 != None: shared.CurrentInput2.closeInput(shared.Dataship)
    if DataInputToLoad3 != "none" and shared.CurrentInput3 != None: shared.CurrentInput3.closeInput(shared.Dataship)
    sys.exit()

# vi: modeline tabstop=8 expandtab shiftwidth=4 softtabstop=4 syntax=python
