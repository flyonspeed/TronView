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
## Function: printDebug
## handle debug print out
def printDebug(debug, string, level=1):
    if debug >= level:
        print(string)


#############################################
## Function: show command Args
def showArgs():
    print("hud.py <options>")
    print(" -d mgl (MGL iEFIS)")
    print(" -d skyview (Dynon Skyview)")
    print(" -s <Screen Module Name>")
    if os.path.isfile("hud.cfg") == False:
        print(" hud.cfg not found (default values will be used)")
    else:
        inputsource = readConfig("DataInput", "inputsource", "none")
        print(" hud.cfg FOUND")
        print(" hud.cfg inputsource=", inputsource)

    listEfisScreens()
    listInputSources()
    sys.exit()


##############################################
## function: listEfisScreens()
## list python screens available to show in the lib/screens dir.
def listEfisScreens():
    lst = os.listdir("lib/screens")
    print("\nAvailable screens modules: (located in lib/screens folder)")
    for d in lst:
        if d.endswith(".py") and not d.startswith("_"):
            screenName = d[:-3]
            print(screenName)


##############################################
## function: doesEfisScreenExist()
def doesEfisScreenExist(name):
    lst = os.listdir("lib/screens")
    for d in lst:
        if d.endswith(".py") and not d.startswith("_"):
            screenName = d[:-3]
            if screenName == name:
                return True
    return False


##############################################
## function: listInputSources()
## list python input source classes available to show in the lib/inputs dir.
def listInputSources():
    lst = os.listdir("lib/inputs")
    print("\nAvailable input source modules: (located in lib/inputs folder)")
    for d in lst:
        if d.endswith(".py") and not d.startswith("_"):
            inputName = d[:-3]
            print(inputName)


##############################################
## function: doesInputSourceExist()
def doesInputSourceExist(name):
    lst = os.listdir("lib/inputs")
    for d in lst:
        if d.endswith(".py") and not d.startswith("_"):
            inputName = d[:-3]
            if inputName == name:
                return True
    return False


# vi: modeline tabstop=8 expandtab shiftwidth=4 softtabstop=4 syntax=python
