#!/usr/bin/env python

import math, os, sys, random
import ConfigParser
import importlib

#############################################
## Function: readConfig
def readConfig(section, name, defaultValue=0, show_error=False):
    global configParser
    try:
        value = configParser.get(section, name)
        return value
    except Exception as e:
        if show_error == True:
            print("config error section: ", section, " key:", name, " -- not found")
        return defaultValue
    else:
        return defaultValue


#############################################
## Function: readConfigInt
def readConfigInt(section, name, defaultValue=0):
    return int(readConfig(section, name, defaultValue=defaultValue))


#############################################
## Function: show command Args
def showArgs():
    print("hud.py <options>")
    print(" -i <Input Module Name")
    print(" -s <Screen Module Name>")
    if os.path.isfile("hud.cfg") == False:
        print(" hud.cfg not found (default values will be used)")
    else:
        screen = readConfig("Hud", "screen", "Not Set")
        inputsource = readConfig("DataInput", "inputsource", "Not Set")
        print(" hud.cfg FOUND")
        print(" hud.cfg inputsource=%s"%(inputsource))
        print(" hud.cfg screen=%s"%(screen))

    findScreen() # Show screen modules
    findInput()  # Show input sources
    sys.exit()


##############################################
## function: findScreen()
## list python screens available to show in the lib/screens dir.
def findScreen(name=""):
    lst = os.listdir("lib/screens")
    if name == "":
        print("\nAvailable screens modules: (located in lib/screens folder)")
    for d in lst:
        if d.endswith(".py") and not d.startswith("_"):
            screenName = d[:-3]
            if name == "": # if no name passed in then print out all screens.
                print(screenName)
            else:
                if screenName == name: # found screen name.
                    return True
    if name != "":
        return False   

##############################################
## function: findInput()
## list python input source classes available to show in the lib/inputs dir.
def findInput(name=""):
    lst = os.listdir("lib/inputs")
    if name == "":
        print("\nAvailable input source modules: (located in lib/inputs folder)")
    for d in lst:
        if d.endswith(".py") and not d.startswith("_"):
            inputName = d[:-3]
            if name == "": # if no name passed in then print out all input sources.
                print(inputName)
            else:
                if inputName == name: # found input
                    return True
    if name != "":
        return False


# vi: modeline tabstop=8 expandtab shiftwidth=4 softtabstop=4 syntax=python

