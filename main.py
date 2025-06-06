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
from lib import hud_graphics
from lib.util import drawTimer
from lib.util import rpi_hardware
from lib.util import mac_hardware
from lib.common.text import text_mode
from lib.common.graphic import graphic_mode
from lib.common.graphic import edit_mode
from lib.common import shared # global shared objects stored here.
from lib.common.graphic import edit_save_load
from lib.common.graphic.growl_manager import GrowlPosition
from lib.version import __version__, __build_date__, __build__, __build_time__
from lib.common.dataship.dataship import Interface
from lib.inputs import _input

#############################################
## Class: myThreadEfisInputReader
## Read input data on separate thread.
class myThreadEfisInputReader(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)

    def run(self):
        internalLoopCounter = 1
        input_count = len(shared.Inputs)
        # make sure at least one input is not onMessagePriority None
        for i in range(input_count):
            if shared.Inputs[i].onMessagePriority is not None:
                break
        else:
            print("No inputs with onMessagePriority set, exiting input thread")
            return
        while shared.Dataship.errorFoundNeedToExit == False:
            # loop through all inputs and read messages from them.
            for i in range(input_count):
                if(shared.Inputs[i].isPaused==True):
                    pass
                else:
                    if shared.Inputs[i].onMessagePriority == 0:
                        shared.Inputs[i].readMessage(shared.Dataship)
                        shared.Inputs[i].time_stamp = shared.Inputs[i].time_stamp_string
                    elif shared.Inputs[i].onMessagePriority is not None:
                        # mod the internalLoopCounter by the priority and if it's 0, read messages.
                        if internalLoopCounter % shared.Inputs[i].onMessagePriority == 0:
                            shared.Inputs[i].readMessage(shared.Dataship)
                            shared.Inputs[i].time_stamp = shared.Inputs[i].time_stamp_string

            internalLoopCounter = internalLoopCounter - 1
            #print(f"{internalLoopCounter}", end=" ")
            if internalLoopCounter < 1:
                internalLoopCounter = 100
                checkInternals()
                if len(shared.Dataship.targetData) > 0:
                    shared.Dataship.targetData[0].cleanUp(shared.Dataship) # check if old traffic targets should be cleared up.
                #print(f"Input Thread: {shared.Inputs[0].name} looped")

            if (shared.Inputs[0].PlayFile != None): # if playing back a file.. add a little delay so it's closer to real world time.
               #print(f"sleep")
               time.sleep(.04)
            # if shared.Dataship.textMode == True: # if in text mode.. lets delay a bit.. this keeps the cpu from heating up on my mac.
            #     time.sleep(.01)

#############################################
## Class: SingleInputReader
## Read input data on separate thread.
class SingleInputReader(threading.Thread):
    def __init__(self, input_index):
        threading.Thread.__init__(self)
        self.input_index = input_index
        
    def run(self):
        # Set this thread to run on a specific core
        # Distribute threads across available cores using modulo
        try:
            import os
            cpu_count = os.cpu_count()
            if cpu_count:
                target_cpu = self.input_index % cpu_count
                os.sched_setaffinity(0, {target_cpu})
                print(f"Input Thread {self.input_index} assigned to CPU core {target_cpu}")
        except AttributeError:
            print("os.sched_setaffinity not available on this platform")
        except Exception as e:
            print(f"Could not set CPU affinity: {e}")

        # check if onMessagePriority is None.. is so then this thread can exit.
        if shared.Inputs[self.input_index].onMessagePriority is None:
            print(f"Input Thread {self.input_index}: {shared.Inputs[self.input_index].name} has no onMessagePriority, exiting")
            return

        internalLoopCounter = 1
        print(f"Input Thread {self.input_index}: {shared.Inputs[self.input_index].name} started")
        while shared.Dataship.errorFoundNeedToExit == False:
            if shared.Inputs[self.input_index].isPaused == True:
                pass
            else:
                # if priority is 0, read messages every cycle of the loop.
                if shared.Inputs[self.input_index].onMessagePriority == 0:
                    shared.Inputs[self.input_index].readMessage(shared.Dataship)
                    shared.Inputs[self.input_index].time_stamp = shared.Inputs[self.input_index].time_stamp_string
                elif shared.Inputs[self.input_index].onMessagePriority is not None:
                    # mod the internalLoopCounter by the priority and if it's 0, read messages.
                    if internalLoopCounter % shared.Inputs[self.input_index].onMessagePriority == 0:
                        shared.Inputs[self.input_index].readMessage(shared.Dataship)
                        shared.Inputs[self.input_index].time_stamp = shared.Inputs[self.input_index].time_stamp_string

                internalLoopCounter = internalLoopCounter - 1
                #print(f"{internalLoopCounter}", end=" ")
                if self.input_index == 0:  # Only do cleanup on one thread
                    if internalLoopCounter < 1:
                        internalLoopCounter = 1000
                        checkInternals()
                        if len(shared.Dataship.targetData) > 0:
                            shared.Dataship.targetData[0].cleanUp(shared.Dataship) # check if old traffic targets should be cleared up.
                        #print(f"Input Thread: {self.input_index} {shared.Inputs[self.input_index].name} looped")

            if shared.Inputs[self.input_index].PlayFile != None: # if playing back a file.. add a little delay so it's closer to real world time.
                #print(f"sleep")
                time.sleep(.04)
            # if shared.Dataship.textMode == True:
            #     time.sleep(.01)

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
def loadInput(num, nameToLoad, playFile=None):
    print(f"Input data module {num}: {nameToLoad}")
    if hud_utils.findInput(nameToLoad) == False:
        print(f"Input source {num} not found: {nameToLoad}")
        hud_utils.findInput()  # show available inputs
        sys.exit()
    module = f".{nameToLoad}"
    mod = importlib.import_module(module, "lib.inputs")
    class_ = getattr(mod, nameToLoad)
    newInput = class_()
    newInput.PlayFile = playFile
    newInput.initInput(num, shared.Dataship)
    if not hasattr(newInput, 'id'):
        newInput.id = newInput.name
    shared.Inputs[num] = newInput
    print(f"Input {num} loaded to shared.Inputs[{num}]: {nameToLoad}")
    shared.GrowlManager.add_message(f"Input{num}: {newInput.id} Loaded {nameToLoad}", 
                                  position=GrowlPosition.BOTTOM_LEFT, duration=8)
    return newInput

#############################################
#############################################
# Main function.
#

# check args passed in.
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="TronView")
    parser.add_argument('-t', action='store_true', help='Text mode')
    parser.add_argument('-e', action='store_true', help='Playback mode')
    parser.add_argument('-c', type=str, help='Custom example file name')
    parser.add_argument('--listlogs', action='store_true', help='List log data files')
    parser.add_argument('--listexamplelogs', action='store_true', help='List example log files')
    parser.add_argument('--listusblogs', action='store_true', help='List USB log data files')
    parser.add_argument('-i', type=str, help='Input source')
    parser.add_argument('-s', '--screen', type=str, help='Screen to load')
    parser.add_argument('-l', action='store_true', help='List serial ports')
    parser.add_argument('--load-screen', type=str, help='Load screen from JSON file')
    parser.add_argument('--input-threads', action='store_true', help='Run each input on a separate thread (default is all on one input thread)')
    
    # Replace individual input arguments with dynamic argument handling
    input_args = {}
    parser.add_argument(f'--in1', type=str, help="--in1-100 input to use")
    parser.add_argument(f'--playfile1', type=str, help="--playfile1-100 playback file to use for this input")
    for i in range(2, 100):  # Support up to 99 inputs
        parser.add_argument(f'--in{i}', type=str, help=argparse.SUPPRESS)
        parser.add_argument(f'--playfile{i}', type=str, help=argparse.SUPPRESS)
    
    args = parser.parse_args()
    
    if args.t:
        print("Text mode")
        # shared.Dataship.textMode = True
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
        allPlayback = None # None means no playback
    if args.c:  # this is the same as --playfile1        
        args.playfile1 = args.c
    if args.i:
        # this is the same as --in1
        loadInput(0,args.i,args.playfile1 if args.playfile1 else allPlayback)

    # dynamicly load inputs based on args
    for i in range(1, 100):
        if getattr(args, f'in{i}'):
            loadInput(i-1, getattr(args, f'in{i}'), getattr(args, f'playfile{i}') if getattr(args, f'playfile{i}') else allPlayback)

    if args.screen:
        ScreenNameToLoad = args.screen
    else:
        ScreenNameToLoad = hud_utils.readConfig("Main", "screen", "template:default")
    if args.l:
        rpi_hardware.list_serial_ports(True)
        sys.exit()
    # if args.load_screen:
    #     hud_graphics.initDisplay(0)
    #     edit_mode.load_screen_from_json(args.load_screen)

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
        shared.Dataship.internalData.Hardware = "Mac"
        shared.Dataship.internalData.OS = "OSx"
        shared.Dataship.internalData.OSVer = os.name + " " + platform.system() + " " + str(platform.release())
    shared.Dataship.internalData.PythonVer = str(sys.version_info[0])+"."+str(sys.version_info[1])+"."+str(sys.version_info[2])
    shared.Dataship.internalData.GraphicEngine2 = pygame.version.vernum
    shared.Dataship.internalData.GraphicEngine3dVer = pygame.version.ver

    if(shared.Dataship.errorFoundNeedToExit==True): sys.exit()
    # check and load screen module. (if not starting in text mode)

    shared.Dataship.interface = Interface.GRAPHIC_2D

    if(shared.Dataship.errorFoundNeedToExit==True): sys.exit()
    # TODO: support text mode.

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
    if shared.Dataship.interface == Interface.EDITOR or shared.Dataship.interface == Interface.GRAPHIC_2D:
        hud_graphics.initDisplay(0)
        # check if /data/screens/screen.json exists.. if so load edit_save_load.load_screen_from_json()
        edit_save_load.load_screen_from_json(ScreenNameToLoad)

    shared.GrowlManager.add_message("TronView " + __version__, position=GrowlPosition.CENTER, duration=8)
    shared.GrowlManager.add_message("Build: " + __build__ + " " + __build_date__ + " " + __build_time__, position=GrowlPosition.CENTER, duration=8)
    shared.GrowlManager.add_message("By running this software you agree to the terms of the license.", position=GrowlPosition.CENTER, duration=8)
    shared.GrowlManager.add_message("Use at own risk!", position=GrowlPosition.CENTER, duration=8)
    shared.GrowlManager.add_message("TronView.org", position=GrowlPosition.CENTER, duration=8)

    shared.GrowlManager.add_message("Press E to enter edit mode", position=GrowlPosition.BOTTOM_MIDDLE, duration=12)
    shared.GrowlManager.add_message("Press L to load screen", position=GrowlPosition.BOTTOM_MIDDLE, duration=12)
    shared.GrowlManager.add_message("Press Q to quit", position=GrowlPosition.BOTTOM_MIDDLE, duration=12)

    shared.GrowlManager.add_message("USE AT YOUR OWN RISK!", position=GrowlPosition.BOTTOM_LEFT, duration=8)
    shared.GrowlManager.add_message("USE AT YOUR OWN RISK!", position=GrowlPosition.BOTTOM_RIGHT, duration=8)
    shared.GrowlManager.add_message("USE AT YOUR OWN RISK!", position=GrowlPosition.TOP_LEFT, duration=8)
    shared.GrowlManager.add_message("USE AT YOUR OWN RISK!", position=GrowlPosition.TOP_RIGHT, duration=8)

    # start main loop.
    while not shared.Dataship.errorFoundNeedToExit:
        if shared.Dataship.interface == Interface.EDITOR:
            edit_mode.main_edit_loop()
        # TODO: support text mode.
        # elif shared.Dataship.interface == Interface.TEXT:
        #     text_mode.main_text_mode()  # start main text loop
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
