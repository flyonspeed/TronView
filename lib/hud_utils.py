#!/usr/bin/env python

import math, os, sys, random
import configparser
import importlib


#############################################
## Function: readConfig
# load config.cfg file if it exists.
configParser = configparser.RawConfigParser()
configParser.read("config.cfg")
def readConfig(section, name, defaultValue=0, show_error=False,hideoutput=False):
    global configParser
    try:
        value = configParser.get(section, name)
        if(hideoutput==False): print("Config.cfg: ["+section+"] "+name+": "+value)
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

#############################################
## Function: readConfigBool
def readConfigBool(section, name, defaultValue=False):
    theValue = readConfig(section, name, defaultValue=defaultValue)
    if(type(theValue) == type(True)): return theValue
    if(isinstance(theValue, str)): 
        if(theValue.upper()=="TRUE"): return True
        if(theValue.upper()=="FALSE"): return False
    # else return default value.
    return defaultValue

#############################################
## Function: readConfigXY
def readConfigXY(section, name, defaultValue=False):
    theValue = readConfig(section,name,defaultValue=defaultValue)
    if type(theValue) is tuple:  # possible that it returned a default type of tuple.. if so just return it.
        return theValue
    if len(theValue)>0:
        xy = theValue.split(",")
        try:
            size = int(xy[0]),int(xy[1])
            return size
        except:
            raise Exception("Config error: ",sys.exc_info()[0]," . [",section,"] ",name," is not a valid x,y")
    return defaultValue

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
    from lib.common import shared 

    extraPath = readConfig("DataRecorder", "path", shared.DefaultFlightLogDir,hideoutput=True)
    print("main.py -i <inputsource> - s <screenmodule> <more options>")
    print(" -i  <Input 1 Source> Main input source (Required unless defined in config.cfg)")
    print(" --in1 <Input 1 Source> same as using -i")
    print(" --in2 <Input 2 Source> optional 2nd input source")

    print(" -s <Screen Name> (Required unless defined in config.cfg, or in text mode)")
    print(" -t Start in text mode")

    print(" -e demo mode. Use default example data for main input module")
    print(" -c <custom data filename> use custom log data file to play back")
    print(" --playfile1 playback logfile for input 1 (main input source)")
    print(" --playfile2 playback logfile for input 2")

    print(" --listlogs list log data files ("+extraPath+")")
    print(" --listusblogs list log data files found on usb drive (if plugged in)")
    print(" --listexamplelogs list example log data files (lib/inputs/_example_data)")
    print(" -l list serial ports")


    if os.path.isfile("config.cfg") == False:
        print(" config.cfg not found (default values will be used)")
    else:
        screen = readConfig("Main", "screen", "Not Set")
        inputsource = readConfig("DataInput", "inputsource", "Not Set")
        print("-------------")
        print("config.cfg FOUND")
        print(("config.cfg inputsource=%s"%(inputsource)))
        print(("config.cfg screen=%s"%(screen)))

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
## return list of log files in standard dir and in user defined dir.
def getLogDataFiles(showErrorIfNoUSB=False):
    from lib.common import shared
    from lib.util import rpi_hardware

    extraPath = readConfig("DataRecorder", "path", shared.DefaultFlightLogDir)
    files = []
    extrafiles = []
    usbfiles = []
    # list files in inputs example folder.
    lst = os.listdir("lib/inputs/_example_data")
    for d in lst:
        if not d.startswith("_"):
            files.append(d)
    # list datarecorder path.
    lst = os.listdir(extraPath)
    for d in lst:
        if d.endswith(".dat") or d.endswith(".log") or d.endswith(".bin"):
            extrafiles.append(d)
    # list files found on usb drive if any.
    try:
        if rpi_hardware.mount_usb_drive() == True:
            usbpath = "/mnt/usb/"
            lst = os.listdir(usbpath)
            for d in lst:
                if d.endswith(".dat") or d.endswith(".log") or d.endswith(".bin"):
                    usbfiles.append(d)
        else:
            if(showErrorIfNoUSB==True): print("Not USB drive found.")
    except Exception as e: 
        if(showErrorIfNoUSB==True): 
            print(e)
            print("Error: finding USB drive.")
        pass

    return files, extrafiles, usbfiles

##############################################
## function: listLogDataFiles()
def listLogDataFiles():
    from lib.common import shared 

    files,extrafiles,usbfiles = getLogDataFiles()
    extraPath = readConfig("DataRecorder", "path", shared.DefaultFlightLogDir)
    print("\nYour Log output files: (located in "+extraPath+")")
    for file in extrafiles:
        print(file)
    return 

##############################################
## function: listExampleLogs()
def listExampleLogs():
    files,extrafiles,usbfiles = getLogDataFiles()
    print("\nAvailable log demo files: (located in lib/inputs/_example_data folder)")
    for file in files:
        print(file)
    return 

##############################################
## function: listUSBLogDataFiles()
def listUSBLogDataFiles():
    files,extrafiles,usbfiles = getLogDataFiles(showErrorIfNoUSB=True)
    if(len(usbfiles)>0):
        print("\nUSB Log files found:")
        for file in usbfiles:
            print(file)
    return 

##############################################
## function: getDataRecorderDir()
## creates the data dir if it doesn't already exist..
## return fullpath if succes or already exists.
def getDataRecorderDir(exitOnFail=False):
    from os.path import exists
    import os
    from pathlib import Path
    from lib.common import shared 

    path_datarecorder = readConfig("DataRecorder", "path", shared.DefaultFlightLogDir)
    fullpath = ""
    try:
        user_home = str(Path.home())
        fullpath = path_datarecorder.replace("~",user_home) # expand out full user dir if it's in the path.
        if(exists(fullpath)==False):
            print("Creating DataRecorder dir: "+fullpath)
            os.mkdir(fullpath) # make sure the dir exists..
    except Exception as e: 
        print(e)
        print("Error DataRecorder dir: "+dirname)
        shared.aircraft.errorFoundNeedToExit = True
        if(exitOnFail==True): sys.exit()
        return False
    if fullpath.endswith('/')==False: fullpath = fullpath + "/" # add a slash if needed.
    return fullpath

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
            print(screenName, end=", ")
        else:
            if screenName == name: # found screen name.
                selectedScreenPos = count
                return True
    if name != "":
        return False
    else:
        print("") # print on new line.

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
                print(inputName, end=", ")
            else:
                if inputName == name: # found input
                    return True
    if name != "":
        return False
    else:
        print("") # print on new line.


# vi: modeline tabstop=8 expandtab shiftwidth=4 softtabstop=4 syntax=python

