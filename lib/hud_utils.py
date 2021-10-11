#!/usr/bin/env python

import math, os, sys, random
import configparser
import importlib

#############################################
## Function: readConfig
# load hud.cfg file if it exists.
configParser = configparser.RawConfigParser()
configParser.read("hud.cfg")
def readConfig(section, name, defaultValue=0, show_error=False):
    global configParser
    try:
        value = configParser.get(section, name)
        return value
    except Exception as e:
        if show_error == True:
            print(("config value not set section: ", section, " key:", name, " -- not found"))
            print(e)
        return defaultValue
    else:
        return defaultValue


#############################################
## Function: readConfigInt
def readConfigInt(section, name, defaultValue=0):
    return int(readConfig(section, name, defaultValue=defaultValue))

# https://stackoverflow.com/questions/699866/python-int-to-binary#699891
def get_bin(x, n=8):
    """
    Get the binary representation of x.

    Parameters
    ----------
    x : int
    n : int
        Minimum number of digits. If x needs less digits in binary, the rest
        is filled with zeros.

    Returns
    -------
    str
    """
    return format(x, "b").zfill(n)

#############################################
## Function: show command Args
def showArgs():
    print("hud.py -i <inputmodule> - s <screenmodule> <more options>")
    print(" -i <Input Module Name> (Required)")
    print(" -s <Screen Module Name> (Required)")
    print(" -t Show text mode only")
    print(" -e demo mode. Use default example data for input module")
    print(" -c <custom data filename> use custom log data file to play back")
    print(" -r list log data files")
    print(" -l list serial ports")


    if os.path.isfile("hud.cfg") == False:
        print(" hud.cfg not found (default values will be used)")
    else:
        screen = readConfig("HUD", "screen", "Not Set")
        inputsource = readConfig("DataInput", "inputsource", "Not Set")
        print("-------------")
        print("hud.cfg FOUND")
        print(("hud.cfg inputsource=%s"%(inputsource)))
        print(("hud.cfg screen=%s"%(screen)))

    findScreen() # Show screen modules
    findInput()  # Show input sources
    sys.exit()


##############################################
## function: getScreens()
## return list of screens available in lib/screens dir.
def getScreens():
    screens = []
    lst = os.listdir("lib/screens")
    for d in lst:
        if d.endswith(".py") and not d.startswith("_"):
            screenName = d[:-3]
            screens.append(screenName)
    return screens

##############################################
## function: getLogDataFiles()
## return list of example files in standard dir and in user defined dir.
def getLogDataFiles():
    extraPath = readConfig("DataRecorder", "path", "/tmp/")
    files = []
    extrafiles = []
    lst = os.listdir("lib/inputs/_example_data")
    for d in lst:
        if not d.startswith("_"):
            files.append(d)
    lst = os.listdir(extraPath)
    for d in lst:
        if d.endswith(".dat") or d.endswith(".log") or d.endswith(".bin"):
            extrafiles.append(d)

    return files, extrafiles

##############################################
## function: listLogDataFiles()
def listLogDataFiles():
    files,extrafiles = getLogDataFiles()
    print("\nAvailable log demo files: (located in lib/inputs/_example_data folder)")
    for file in files:
        print(file)
    extraPath = readConfig("DataRecorder", "path", "/tmp/")
    print("\nYour Log output files: (located in "+extraPath+")")
    for file in extrafiles:
        print(file)
    return 

##############################################
## function: findScreen()
## list python screens available to show in the lib/screens dir.
## if you pass in "next" then it will try to load the next screen from the last loaded screen.
selectedScreenPos = 0
def findScreen(name=""):
    global selectedScreenPos
    lst = getScreens()
    if name == "current":  # re-load current screen
        return lst[selectedScreenPos]
    if name == "prev":  # load previous screen
        selectedScreenPos -= 1
        if selectedScreenPos < 0:
            selectedScreenPos = len(lst) -1
        return lst[selectedScreenPos]
    if name == "next":  # check if we should just load the next screen in the screen list.
        selectedScreenPos += 1
        if selectedScreenPos +1 > len(lst):
            selectedScreenPos = 0
        return lst[selectedScreenPos]
    if name == "":
        print("\nAvailable screens modules: (located in lib/screens folder)")
    count = -1
    for screenName in lst:
        count+=1
        if name == "": # if no name passed in then print out all screens.
            print(screenName)
        else:
            if screenName == name: # found screen name.
                selectedScreenPos = count
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

