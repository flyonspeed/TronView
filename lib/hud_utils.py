#!/usr/bin/env python

import math, os, sys, random
import ConfigParser
import importlib

#############################################
## Function: readConfig
def readConfig(section,name,defaultValue=0,show_error=False):
    global configParser
    try:
        value = configParser.get(section, name)
        return value
    except Exception as e:
        if show_error == True:
            print "config error section: ",section," key:",name," -- not found"
        return defaultValue
    else:
        return defaultValue

#############################################
## Function: readConfigInt
def readConfigInt(section,name,defaultValue=0):
    return int(readConfig(section,name,defaultValue=defaultValue))

#############################################
## Function: printDebug
## handle debug print out
def printDebug(debug, string, level=1):
    if debug >= level:
        print string

#############################################
## Function: show command Args
def showArgs(dataFormat):
  print 'hud.py <options>'
  print ' -d mgl (MGL iEFIS)'
  print ' -d skyview (Dynon Skyview)'
  print ' -s <Screen Module Name>'
  if os.path.isfile("hud.cfg") == False:
    print ' hud.cfg not found (default values will be used)'
  else:
    print ' hud.cfg FOUND'
    print ' hud.cfg efis_data_format=',dataFormat

  listEfisScreens()

  sys.exit()

##############################################
## function: listEfisScreens()
## list python screens available to show in the lib/screens dir.
def listEfisScreens():
    res = {}
    # check subfolders
    lst = os.listdir("lib/screens")
    dir = []
    print "\nAvailable screens modules: (located in lib/screens folder)"
    for d in lst:
        if d.endswith('.py') and not d.startswith('_') :
          screenName = d[:-3]
          print screenName
    # load the modules
    for d in dir:
        #res[d] = __import__("services." + d, fromlist = ["*"])
        print d
    #return res

##############################################
## function: doesEfisScreenExist()
def doesEfisScreenExist(name):
    res = {}
    # check subfolders
    lst = os.listdir("lib/screens")
    dir = []
    for d in lst:
        if d.endswith('.py') and not d.startswith('_') :
          screenName = d[:-3]
          if screenName == name:
            return True
    return False
    
# vi: modeline tabstop=8 expandtab shiftwidth=4 softtabstop=4 syntax=python
