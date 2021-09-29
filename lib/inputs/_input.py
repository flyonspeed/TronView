#!/usr/bin/env python

# Input class.
# All input types should inherit from this class.

from lib import hud_text
from lib import hud_utils
from lib.util import rpi_hardware

class Input:
    def __init__(self):
        self.name = "Input Class"
        self.version = 1.0
        self.inputtype = ""
        self.path_datarecorder = ""

    def initInput(self, aircraft):
        self.path_datarecorder = hud_utils.readConfig("DataRecorder", "path", "/tmp/")
        return

    #############################################
    ## Method: openLogFile
    def openLogFile(self,filename,attribs):
        try:
            openFileName = self.path_datarecorder+filename
            logFile = open(openFileName, attribs)
            print("Opening log:"+openFileName)
            return logFile,openFileName
        except :
            pass

        try:
            openFileName = "lib/inputs/_example_data/"+filename
            print("Opening log:"+openFileName)
            logFile = open(openFileName, attribs)
            return logFile,openFileName
        except :
            pass



    #############################################
    ## Method: createLogFile
    ## Create a new log file.
    def createLogFile(self,fileExtension,isBinary):
        if rpi_hardware.mount_usb_drive() == True:
            openFileName = self.getNextLogFile("/mnt/usb/",fileExtension)
        else:
            openFileName = self.getNextLogFile(self.path_datarecorder,fileExtension)
        try:
            if isBinary == True:
                logFile = open(openFileName, "w+b")
            else:
                logFile = open(openFileName, "w")
            return logFile,openFileName
        except :
            print("Error createLogFile() %s"%(openFileName))
            return  "",""

    #############################################
    ## Method: closeLogFile
    ## Close current log file
    def closeLogFile(self,logfile):
        print("Closing Logfile\n")
        try:
            logfile.close()
            return None
        except :
            print("Error closeLogFile()")
        return None
        
    #############################################
    ## Method: addToLog
    ## save line of data to log file.
    def addToLog(self,logfile,dataline):
        #print ("write")
        try:
            logfile.write(dataline)
        except :
            print("Error addToLog()")

    #############################################
    ## Method: getNextLogFile
    ## get next log file to open.
    def getNextLogFile(self,dirname,fileExtension):
        from os.path import exists
        number = 1
        newFilename = dirname + self.name + "_" + str(number) + fileExtension
        while exists(newFilename) == True:
            number = number + 1
            newFilename = dirname + self.name + "_" + str(number) + fileExtension
        print("using filename %s"%(newFilename))
        return newFilename


# vi: modeline tabstop=8 expandtab shiftwidth=4 softtabstop=4 syntax=python
