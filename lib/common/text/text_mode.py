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
from lib import aircraft


#############################################
# Text mode Main loop
def main_text_mode():
    hud_text.print_Clear()
    threadKey = threadReadKeyboard() # read keyboard input for text mode using curses
    threadKey.start()
    print(shared.aircraft.textMode)
    while not shared.aircraft.errorFoundNeedToExit and shared.aircraft.textMode:
        shared.CurrentInput.printTextModeData(shared.aircraft)

#############################################
## Class: threadReadKeyboard (FOR TEXT MODE ONLY...)
# thread for reading in data.  used during text mode.  curses module used for keyboard input.
class threadReadKeyboard(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.stdscr = curses.initscr()
        self.stdscr.keypad(1)    

    def run(self):
        while not shared.aircraft.errorFoundNeedToExit and shared.aircraft.textMode:
            key = self.stdscr.getch()
            #curses.endwin()
            if key==ord('q'):
                curses.endwin()
                shared.aircraft.errorFoundNeedToExit = True
            elif key==curses.KEY_RIGHT:
                shared.CurrentInput.fastForward(shared.aircraft,500)
            elif key==curses.KEY_LEFT:
                shared.CurrentInput.fastBackwards(shared.aircraft,500)
            elif key==27:  # escape key.
                curses.endwin()
                shared.aircraft.textMode = False
                loadScreen(hud_utils.findScreen("current")) # load current screen
            #elif key==339: #page up
            #elif key==338: #page up
            elif key==23:  #cntrl w
                try:
                    shared.CurrentInput.startLog(shared.aircraft)
                except :
                    pass
            elif key==5: #cnrtl e
                try:
                    shared.CurrentInput.stopLog(shared.aircraft)
                except :
                    pass
            else: #else send this key to the input (if it has the ability)
                try:
                    retrn,returnMsg = shared.CurrentInput.textModeKeyInput(key,hud.aircraft)
                    if retrn == 'quit':
                        curses.endwin()
                        shared.aircraft.errorFoundNeedToExit = True
                        hud_text.print_Clear()
                        print(returnMsg)
                except AttributeError:
                    print(("Key: %d \r\n"%(key)))


# vi: modeline tabstop=8 expandtab shiftwidth=4 softtabstop=4 syntax=python
