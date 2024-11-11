#!/usr/bin/env python

#######################################################################################################################################
#######################################################################################################################################
# text mode related
#
#
#
from lib.common import shared

import threading
import math, os, sys, random
import argparse, pygame
import time
import configparser
import importlib
import curses
from lib import hud_utils
from lib import hud_text
from lib.common.dataship import dataship


#############################################
# Text mode Main loop
def main_text_mode():
    hud_text.print_Clear()
    threadKey = threadReadKeyboard() # read keyboard input for text mode using curses
    threadKey.start()
    print(shared.Dataship.textMode)
    clearTimer = 0
    while not shared.Dataship.errorFoundNeedToExit and shared.Dataship.textMode:
        clearTimer += 1
        if(clearTimer>20): 
            hud_text.print_Clear()
            clearTimer = 0
        if(shared.Dataship.errorFoundNeedToExit==False):
            shared.Inputs[0].printTextModeData(shared.Dataship)
        time.sleep(.05)

#############################################
## Class: threadReadKeyboard (FOR TEXT MODE ONLY...)
# thread for reading in data.  used during text mode.  curses module used for keyboard input.
class threadReadKeyboard(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.stdscr = curses.initscr()
        self.stdscr.keypad(1)    

    def run(self):
        while not shared.Dataship.errorFoundNeedToExit and shared.Dataship.textMode:
            key = self.stdscr.getch()
            if key==ord('q'):
                curses.endwin()
                shared.Dataship.errorFoundNeedToExit = True
            if key==ord('p'):
                if(shared.Inputs[0].isPlaybackMode==True):
                    if(shared.Inputs[0].isPaused==False):
                        shared.Inputs[0].isPaused = True
                    else:
                        shared.Inputs[0].isPaused = False
            elif key==curses.KEY_RIGHT:
                shared.Inputs[0].fastForward(shared.Dataship,500)
                if len(shared.Inputs) > 1:
                    shared.Inputs[1].fastForward(shared.Dataship,500)
            elif key==curses.KEY_LEFT:
                shared.Inputs[0].fastBackwards(shared.Dataship,500)
                if len(shared.Inputs) > 1:
                    shared.Inputs[1].fastBackwards(shared.Dataship,500)
            elif key==27:  # escape key.
                curses.endwin()
                shared.Dataship.textMode = False
                loadScreen(hud_utils.findScreen("current"))
            elif key==23 or key==ord('1'):  #cntrl w
                try:
                    shared.Inputs[0].startLog(shared.Dataship)
                    if len(shared.Inputs) > 1:
                        shared.Inputs[1].startLog(shared.Dataship)
                except:
                    pass
            elif key==5 or key==ord('2'): #cnrtl e
                try:
                    shared.Inputs[0].stopLog(shared.Dataship)
                    if len(shared.Inputs) > 1:
                        shared.Inputs[1].stopLog(shared.Dataship)
                except:
                    pass
            else:
                try:
                    retrn,returnMsg = shared.Inputs[0].textModeKeyInput(key,shared.Dataship)
                    if retrn == 'quit':
                        curses.endwin()
                        shared.Dataship.errorFoundNeedToExit = True
                        hud_text.print_Clear()
                        print(returnMsg)
                except AttributeError:
                    print(("Key: %d \r\n"%(key)))


# vi: modeline tabstop=8 expandtab shiftwidth=4 softtabstop=4 syntax=python
