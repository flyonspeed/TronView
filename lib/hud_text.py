#!/usr/bin/env python

import os, sys

#######################################################################################################################################
#######################################################################################################################################
# Text function for helping to print hud data
#
# 1/31/2019 Christopher Jones
#


class bcolors:
    HEADER = "\033[95m"
    OKBLUE = "\033[94m"
    OKGREEN = "\033[92m"
    WARNING = "\033[93m"
    FAIL = "\033[91m"
    ENDC = "\033[0m"
    BOLD = "\033[1m"
    UNDERLINE = "\033[4m"

lastTextX = 1  # global x,y for storing last postion used.
lastTextY = 0


#############################################
## Function to clear text screen.
def print_Clear():
    if sys.platform.startswith('win'):
        os.system('cls')  # on windows
    else:
        os.system("clear")  # on Linux / os X

#############################################
## Function for letting print now you are done with printing everything on the page.
def print_DoneWithPage():
    global lastTextX, lastTextY
    lastTextX = 1
    lastTextY = 0
    sys.stdout.flush()

#############################################
## Function print header at next location
def print_header(header):
    global lastTextX, lastTextY
    sys.stdout.write("\x1b7\x1b[%d;%df%s\x1b8" % (lastTextX, lastTextY, bcolors.HEADER + header + bcolors.ENDC))
    lastTextX = lastTextX + 1

#############################################
## Function print at next location
def print_data(label,value):
    global lastTextX, lastTextY
    sys.stdout.write("\x1b7\x1b[%d;%df%s : %s        \x1b8" % (lastTextX, lastTextY, bcolors.UNDERLINE + label + bcolors.ENDC, bcolors.OKGREEN + str(value) + bcolors.ENDC))
    lastTextX = lastTextX + 1 #increment the text postion to next location for next time this is called.

#############################################
## Function to print all object values.
def print_object(obj):
    for attr, value in vars(obj).items():
        print_data(attr,value)

#############################################
## Function change the x,y postions to start printing from.
def changePos(x,y):
    global lastTextX, lastTextY
    lastTextX = x
    lastTextY = y

#############################################
## old school function for printing value at x,y
def print_xy(x, y, text):
    sys.stdout.write("\x1b7\x1b[%d;%df%s\x1b8" % (x, y, text))
    sys.stdout.flush()

# vi: modeline tabstop=8 expandtab shiftwidth=4 softtabstop=4 syntax=python

