#!/usr/bin/env python

# Input class.
# All input types should inherit from this class.

from lib import hud_text
from lib import hud_utils
from lib.util import rpi_hardware
import re
from lib.common import shared # global shared objects stored here.

class Input:
    def __init__(self):
        self.name = "Input Class"
        self.version = 1.0
        self.inputtype = ""
        self.path_datarecorder = ""


    def initInput(self, aircraft):
        self.ser = None # is is the input source... File, serial device, network connection...

        self.path_datarecorder = hud_utils.readConfig("DataRecorder", "path", shared.DefaultFlightLogDir)

        self.shouldExit = False

        self.textMode_showAir = True
        self.textMode_showNav = True
        self.textMode_showTraffic = True
        self.textMode_showEngine = True
        self.textMode_showFuel = True
        self.textMode_showGps = True
        self.textMode_showRaw = False

        self.skipReadInput = False
        self.skipTextOutput = False
        self.output_logFile = None
        self.output_logFileName = ""
        self.input_logFileName = ""

        return

    def cleanInt(self,v):
        return int(v)
        #return int(re.sub('[^\d]','',str(v)))

    #############################################
    ## Method: openLogFile
    def openLogFile(self,filename,attribs):
        try:
            openFileName = self.path_datarecorder+filename
            logFile = open(openFileName, attribs)
            print("Opening Logfile: "+openFileName)
            return logFile,openFileName
        except :
            pass

        try:
            openFileName = "lib/inputs/_example_data/"+filename
            print("Opening Logfile: "+openFileName)
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
        except Exception as e: 
            print(e)
            print("Error createLogFile() %s"%(openFileName))
            return  "",""

    #############################################
    ## Method: closeLogFile
    ## Close current log file
    def closeLogFile(self,logfile):
        print("Closing Logfile: "+self.output_logFileName)
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
        import os
        from pathlib import Path
        try:
            user_home = str(Path.home())
            fullpath = dirname.replace("~",user_home) # expand out full user dir if it's in the path.
            if(exists(fullpath)==False):
                print("Creating dir: "+fullpath)
                os.mkdir(fullpath) # make sure the dir exists..
        except Exception as e: 
            print(e)
            print("Error creating log dir: "+dirname)
            shared.aircraft.errorFoundNeedToExit = True
            return False
        number = 1
        if fullpath.endswith('/')==False: fullpath = fullpath + "/" # add a slash if needed.
        newFilename = fullpath + self.name + "_" + str(number) + fileExtension
        while exists(newFilename) == True:
            number = number + 1
            newFilename = fullpath + self.name + "_" + str(number) + fileExtension
        #print("using filename %s"%(newFilename))
        return newFilename

    #############################################
    ## Function: printTextModeData
    def printTextModeData(self, aircraft):
        hud_text.print_header("Decoded data from Input Module: %s (Keys: n=nav, a=all, r=raw)"%(self.name))
        if len(aircraft.demoFile):
            hud_text.print_header("Playing Log: %s"%(aircraft.demoFile))

        if self.textMode_showAir==True:
            hud_text.print_object(aircraft)

        if self.textMode_showNav==True:
            hud_text.changePos(2,34)
            hud_text.print_header("Nav Data")
            hud_text.print_object(aircraft.nav)

        if self.textMode_showTraffic==True:
            hud_text.print_header("Traffic Data")
            hud_text.print_object(aircraft.traffic)

        if self.textMode_showGps==True:
            hud_text.print_header("GPS Data")
            hud_text.print_object(aircraft.gps)

        if self.textMode_showEngine==True:
            hud_text.changePos(2,62)
            hud_text.print_header("Engine Data")
            hud_text.print_object(aircraft.engine)

        if self.textMode_showFuel==True:
            hud_text.print_header("Fuel Data")
            hud_text.print_object(aircraft.fuel)
            hud_text.print_header("Input Source")
            hud_text.print_object(aircraft.input1)
            hud_text.print_header("Internal Data")
            hud_text.print_object(aircraft.internal)

        hud_text.print_DoneWithPage()

    #############################################
    ## Function: textModeKeyInput
    ## this is only called when in text mode. And is used to changed text mode options.
    def textModeKeyInput(self, key, aircraft):
        if key==ord('n'):
            self.textMode_showNav = True
            self.textMode_showAir = False
            self.textMode_showTraffic = False
            self.textMode_showEngine = False
            self.textMode_showFuel = False
            hud_text.print_Clear()
            return 0,0
        elif key==ord('a'):
            self.textMode_showNav = True
            self.textMode_showAir = True
            self.textMode_showTraffic = True
            self.textMode_showEngine = True
            self.textMode_showFuel = True
            hud_text.print_Clear()
            return 0,0
        elif key==ord('r'):
            if self.textMode_showRaw == True: self.textMode_showRaw = False
            else: self.textMode_showRaw = True
            hud_text.print_Clear()
            return 0,0
        else:
            return 'quit',"%s Input: Key code not supported: %d ... Exiting \r\n"%(self.name,key)

    #############################################
    ## Function: startLog
    ## tell this input to create log file and start logging data
    def startLog(self,aircraft):
        if self.output_logFile == None:
            self.output_logFile,self.output_logFileName = Input.createLogFile(self,".dat",True)
            print("Creating log output: %s"%(self.output_logFileName))
        else:
            print("Already logging to: "+self.output_logFileName)

    #############################################
    ## Function: stopLog
    ## if currently ouputing to log file to stop and save it.
    def stopLog(self,aircraft):
        from lib.util import rpi_hardware
        serverAvail = None
        if self.output_logFile != None:
            Input.closeLogFile(self,self.output_logFile)
            self.output_logFile = None
            #if(rpi_hardware.is_raspberrypi()==True):
            #    if(rpi_hardware.is_server_available()==True):
            #        serverAvail = "FlyOnSpeed.org"
            return True, serverAvail

        return False,None

    #############################################
    # fast forward if reading from a file.
    def fastForward(self,aircraft,bytesToSkip):
            if aircraft.demoMode:
                current = self.ser.tell()
                moveTo = current - bytesToSkip
                try:
                    for _ in range(bytesToSkip):
                        next(self.ser) # have to use next...
                except:
                    # if error then just to start of file
                    self.ser.seek(0)
                #print("fastForward() before="+str(current)+" goto:"+str(moveTo)+" done="+str(self.ser.tell()))

    #############################################
    # fast backwards if reading from a file.
    def fastBackwards(self,aircraft,bytesToSkip):
            if aircraft.demoMode:
                self.skipReadInput = True  # lets pause reading from the file for second while we mess with the file pointer.
                current = self.ser.tell()
                moveTo = current - bytesToSkip
                if(moveTo<0): moveTo = 0
                self.ser.seek(0) # reset back to begining.
                try:
                    for _ in range(moveTo):
                        next(self.ser) # jump to that postion???  not really working right.
                except:
                    # if error then just to start of file
                    self.ser.seek(0)
                #print("fastForward() before="+str(current)+" goto:"+str(moveTo)+" done="+str(self.ser.tell()))
                self.skipReadInput = False


# vi: modeline tabstop=8 expandtab shiftwidth=4 softtabstop=4 syntax=python
