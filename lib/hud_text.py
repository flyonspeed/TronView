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
startTextY = 0


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
    global lastTextX, lastTextY, startTextY
    lastTextX = 1
    lastTextY = 0
    startTextY = 0
    sys.stdout.flush()

#############################################
## Function print header at next location
def print_header(header):
    global lastTextX, lastTextY
    sys.stdout.write("\x1b7\x1b[%d;%df%s\x1b8" % (lastTextX, lastTextY, bcolors.HEADER + header + bcolors.ENDC))
    lastTextX = lastTextX + 1

#############################################
## Function print at next location
def print_data(label,value,forceIfObject=False,sameLine=False,indent=False,showHowManyListItems=-1):
    global lastTextX, lastTextY, startTextY
    theType = type(value)
    if( theType is str):
        showValue = value
    elif( theType is int):
        showValue = str(value)
    elif( theType is float):
        showValue = "%0.4f" %(value)
    elif( theType is bool):
        showValue = str(value)
    elif( theType is bytes):
        showValue = str(value)
    elif( theType is bytearray):
        showValue = str(value)
    elif( isinstance(value, list)):
        # if its a list check what type of values this list holds
        if(len(value)>1):
            # if list of str,int,floats.. then print it out.
            if(isCustomObject(value[0])==False):
                showValue = str(value)
            else:
                # else it's a list of objects.. print out each obj.
                objCount = 0
                for v in value:
                    objCount += 1
                    print_data(str(objCount)+":","",sameLine=True)
                    print_data("",v,forceIfObject=True, showHowManyListItems=showHowManyListItems)
                return
        else:
            showValue = "[]"
    else :
        if(forceIfObject==True):
            print_object(value,sameLine=True,indent=True,showHowManyItems=showHowManyListItems)
            lastTextY = startTextY
            lastTextX = lastTextX + 1
        # else its a object or something else so don't show it.
        return
    if(indent!=False):
        spacer = "  "
    else:
        spacer = ""

    if(sameLine==True):
        sys.stdout.write("\x1b7\x1b[%d;%df%s : %s  \x1b8" % (lastTextX, lastTextY, bcolors.UNDERLINE + label + bcolors.ENDC, bcolors.OKGREEN + showValue + bcolors.ENDC))
        lastTextY = lastTextY + len("%s : %s  "%(label,showValue)) #increment Y pos.
    else:
        sys.stdout.write("\x1b7\x1b[%d;%df%s%s : %s  \x1b8" % (lastTextX, startTextY, spacer, bcolors.UNDERLINE + label + bcolors.ENDC, bcolors.OKGREEN + showValue + bcolors.ENDC))
        lastTextX = lastTextX + 1 #increment the text postion to next location for next time this is called.
    #sys.stdout.write("\x1b7\x1b[%d;%df%s : %s  \x1b8" % (lastTextX, lastTextY, bcolors.UNDERLINE + label + bcolors.ENDC, bcolors.OKGREEN + str(theType) + bcolors.ENDC))

#############################################
## Function to print all object values.
## if showHowManyItems = -1 then show all items in object.. else its a count of how many to show.
def print_object(obj,sameLine=False,indent=False,showHowManyItems=-1,showHowManyListItems=-1):
    count = 0
    for attr, value in list(vars(obj).items()):
        count += 1
        print_data(attr,value,forceIfObject=False,sameLine=sameLine,indent=indent,showHowManyListItems=showHowManyListItems)
        if(showHowManyItems != -1 and showHowManyItems == count): return

#############################################
## Function change the x,y postions to start printing from.
def changePos(x,y):
    global lastTextX, lastTextY,startTextY
    lastTextX = x
    lastTextY = y
    startTextY = y

#############################################
## old school function for printing value at x,y
def print_xy(x, y, text):
    sys.stdout.write("\x1b7\x1b[%d;%df%s\x1b8" % (x, y, text))
    sys.stdout.flush()

def isCustomObject(v):
    theType = type(v)
    if( theType is str):
        return False
    elif( theType is int):
        return False
    elif( theType is float):
        return False
    elif( theType is bool):
        return False
    elif( theType is bytes):
        return False
    elif( theType is bytearray):
        return False
    elif( isinstance(v, list)):
        return False
    else :
        return True

# vi: modeline tabstop=8 expandtab shiftwidth=4 softtabstop=4 syntax=python

