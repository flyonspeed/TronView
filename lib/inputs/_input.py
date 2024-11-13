#!/usr/bin/env python

# Input class.
# All input types should inherit from this class.

from lib import hud_text
from lib import hud_utils
from lib.util import rpi_hardware
import re
import os
from lib.common import shared # global shared objects stored here.
from datetime import datetime

class Input:
    def __init__(self):
        self.name = "Input Class"
        self.version = 1.0
        self.inputtype = ""
        self.path_datarecorder = ""

    def initInput(self, num, aircraft):
        self.ser = None # is is the input source... File, serial device, network connection...

        self.path_datarecorder = hud_utils.readConfig("DataRecorder", "path", shared.DefaultFlightLogDir)
        self.datarecorder_check_usb = hud_utils.readConfigBool("DataRecorder", "check_usb_drive", True)

        self.shouldExit = False

        self.textMode_whatToShow = 0 # 0 means show all
        self.textMode_showRaw = False

        self.skipReadInput = False
        self.skipTextOutput = False
        self.output_logFile = None
        self.output_logFileName = ""
        self.input_logFileName = None
        self.input_logFileSize = 0
        self.input_logFilePercent = 0 # percentage of file that has been read.
        self.inputNum = num
        self.isPlaybackMode = False
        self.isPaused = False
        self.time_stamp_string = None # time from this input source.. if any..
        self.time_stamp_min = None  
        self.time_stamp_sec = None  

        return

    def cleanInt(self,v):
        return int(v)
        #return int(re.sub('[^\d]','',str(v)))

    #############################################
    ## Method: openLogFile
    # Open a log file for play back.
    def openLogFile(self,filename,attribs):
        #first try usb drive if exists?
        try:
            if rpi_hardware.mount_usb_drive() == True:
                openFileName = "/mnt/usb/"+filename
                logFile = open(openFileName, attribs)
                # get file size
                self.input_logFileSize = os.path.getsize(openFileName)
                self.input_logFilePercent = 0
                print("Opening USB Logfile: "+openFileName+" size="+str(self.input_logFileSize))
                return logFile,openFileName
        except :
            pass

        # then try location for flight data recorder...
        try:
            openFileName = self.path_datarecorder+filename
            logFile = open(openFileName, attribs)
            # get file size
            self.input_logFileSize = os.path.getsize(openFileName)
            self.input_logFilePercent = 0
            print("Opening Logfile: "+openFileName+" size="+str(self.input_logFileSize))
            return logFile,openFileName
        except :
            print("Error openLogFile() "+self.name)
            import traceback
            traceback.print_exc()
            pass

        # else try the example data last.
        try:
            openFileName = "lib/inputs/_example_data/"+filename
            print("Opening example Logfile: "+openFileName)
            logFile = open(openFileName, attribs)
            self.input_logFileSize = os.path.getsize(openFileName)
            self.input_logFilePercent = 0
            return logFile,openFileName
        except :
            pass

    #############################################
    ## Method: createLogFile
    ## Create a new log file. (for saving flight data to)
    def createLogFile(self,fileExtension,isBinary):
        # should we check if the usb drive is available to write to?
        try:
            if (rpi_hardware.mount_usb_drive() == True and self.datarecorder_check_usb == True):
                openFileName = self.getNextLogFile("/mnt/usb/",fileExtension)
            else:
                DataRecorderPath = hud_utils.getDataRecorderDir()
                log_path_format = hud_utils.readConfig("DataRecorder", "log_path_format", "%Y/%m/")
                # get todays year and month. create a folder YYYY/MM/
                today = datetime.now()
                # replace the %Y and %m in the log_path_format with the current year and month.
                log_path_format = log_path_format.replace("%Y",str(today.year)).replace("%m",str(today.month)).replace("%d",str(today.day))
                DataRecorderPath = DataRecorderPath + log_path_format
                # create the folder if it doesn't exist.
                if not os.path.exists(DataRecorderPath):
                    os.makedirs(DataRecorderPath)
                openFileName = self.getNextLogFile(DataRecorderPath,fileExtension)
            if isBinary == True:
                logFile = open(openFileName, "w+b")
            else:
                logFile = open(openFileName, "w")
            return logFile,openFileName
        except Exception as e: 
            print(e)
            print("Error createLogFile() %s"%(self.name))
            # print full stack trace
            import traceback
            traceback.print_exc()
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
        #print("getNextLogFile() "+dirname+" "+fileExtension)
        file_format = hud_utils.readConfig("DataRecorder", "log_file_format", "%Y_%m_%d_%INPUT")

        #fullpath = hud_utils.getDataRecorderDir()
        fullpath = dirname
        number = 1
        today = datetime.now()
        newFilename = fullpath + file_format.replace("%INPUT",self.name).replace("%Y",str(today.year)).replace("%m",str(today.month)).replace("%d",str(today.day)) + "_" + str(number) + fileExtension
        while exists(newFilename) == True: # keep trying until we find a free filename.
            number = number + 1
            newFilename = fullpath + file_format.replace("%INPUT",self.name).replace("%Y",str(today.year)).replace("%m",str(today.month)).replace("%d",str(today.day)) + "_" + str(number) + fileExtension
        #print("using filename %s"%(newFilename))
        return newFilename

    #############################################
    ## Function: printTextModeData
    def printTextModeData(self, aircraft):
        hud_text.print_header("Decoded data from Input Module: %s (Keys: space=cycle data, r=raw)"%(self.name))
        if self.PlayFile!=None:
            hud_text.print_header("Playing Log1: %s"%(self.PlayFile))
        if len(shared.Inputs) > 1 and shared.Inputs[1].PlayFile!=None:
            hud_text.print_header("Playing Log2: %s"%(shared.Inputs[1].PlayFile))
        if(self.isPaused==True):
            hud_text.print_header("PLAYBACK PAUSED!")

        if(self.textMode_whatToShow==0): showHowManyListItems = 1
        else: showHowManyListItems = -1

        if self.textMode_whatToShow==0 or self.textMode_whatToShow==1:
            hud_text.print_object(aircraft,showHowManyListItems=showHowManyListItems)

        if self.textMode_whatToShow==0 or self.textMode_whatToShow==2:
            if self.textMode_whatToShow==0: hud_text.changePos(2,34)
            hud_text.print_header("Nav Data")
            hud_text.print_object(aircraft.nav)

        if self.textMode_whatToShow==0 or self.textMode_whatToShow==3:
            hud_text.print_header("Traffic Data")
            hud_text.print_object(aircraft.traffic,showHowManyListItems=showHowManyListItems)

        if self.textMode_whatToShow==0 or self.textMode_whatToShow==3:
            hud_text.print_header("Analog")
            hud_text.print_object(aircraft.analog,showHowManyListItems=showHowManyListItems)

        if self.textMode_whatToShow==0 or self.textMode_whatToShow==4:
            hud_text.print_header("GPS Data")
            hud_text.print_object(aircraft.gps)

        if self.textMode_whatToShow==0 or self.textMode_whatToShow==5:
            if self.textMode_whatToShow==0: hud_text.changePos(2,62)
            hud_text.print_header("Engine Data")
            hud_text.print_object(aircraft.engine)

        if self.textMode_whatToShow==0 or self.textMode_whatToShow==6:
            hud_text.print_header("Fuel Data")
            hud_text.print_object(aircraft.fuel)
            hud_text.print_header("Input 1")
            hud_text.print_object(self)
            if(len(shared.Inputs) > 1):
                hud_text.print_header("Input 2")
                hud_text.print_object(shared.Inputs[1])                
            hud_text.print_header("Internal Data")
            hud_text.print_object(aircraft.internal)

        hud_text.print_DoneWithPage()

    #############################################
    ## Function: textModeKeyInput
    ## this is only called when in text mode. And is used to changed text mode options.
    def textModeKeyInput(self, key, aircraft):
        if key==ord(' '):
            self.textMode_whatToShow = self.textMode_whatToShow + 1
            if self.textMode_whatToShow > 6: self.textMode_whatToShow=0
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
            self.RecFile = self.output_logFile
        else:
            print("Already logging to: "+self.output_logFileName)

    #############################################
    ## Function: stopLog
    ## if currently ouputing to log file to stop and save it.
    def stopLog(self,aircraft):
        serverAvail = None
        if self.output_logFile != None:
            Input.closeLogFile(self,self.output_logFile)
            self.output_logFile = None
            self.RecFile = None
            return True, serverAvail

        return False,None

    #############################################
    # fast forward if reading from a file.
    def fastForward(self,aircraft,bytesToSkip):
            if self.PlayFile != None:
                current = self.ser.tell()
                moveTo = current - bytesToSkip
                try:
                    for _ in range(bytesToSkip):
                        next(self.ser) # have to use next...
                except:
                    # if error then just to start of file
                    self.ser.seek(0)
                #print("fastForward() before="+str(current)+" goto:"+str(moveTo)+" done="+str(self.ser.tell()))
                print("fastForward->"+self.name)

    #############################################
    # fast backwards if reading from a file.
    def fastBackwards(self,aircraft,bytesToSkip):
            if self.PlayFile != None:
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
                print("fastBackwards->"+self.name)


# vi: modeline tabstop=8 expandtab shiftwidth=4 softtabstop=4 syntax=python
