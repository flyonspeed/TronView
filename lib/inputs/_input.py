#!/usr/bin/env python

# Input class.
# All input types should inherit from this class.

from . import _input_file_utils
import re
import os
from datetime import datetime
import platform
from lib.common import shared # global shared objects stored here.


class Input:
    def __init__(self):
        self.name = "Input Class"
        self.id = ""
        self.version = 1.0
        self.inputtype = ""
        self.path_datarecorder = ""
        self.PlayFile = None

    def initInput(self, num, aircraft):
        self.ser = None # is is the input source... File, serial device, network connection...
        self.onMessagePriority = 0 # 0 is default high priority, None means onMessage is never called.

        self.path_datarecorder = "../data/"
        self.datarecorder_check_usb = _input_file_utils.readConfigBool("DataRecorder", "check_usb_drive", True)

        self.shouldExit = False

        self.textMode_whatToShow = 0 # 0 means show all
        self.textMode_showRaw = False

        self.skipReadInput = False
        self.skipTextOutput = False
        self.output_logFile = None
        self.output_logFileName = ""
        self.output_logBinary = False
        self.input_logFileName = None
        self.input_logFileSize = 0
        self.input_logFilePercent = 0 # percentage of file that has been read.
        self.inputNum = num
        self.isPlaybackMode = False
        self.isPaused = False
        self.time_stamp_string = None # time from this input source.. if any..
        self.time_stamp_min = None  
        self.time_stamp_sec = None  

        # Check if running on a Raspberry Pi
        self.is_raspberry_pi = platform.system() == 'Linux' and 'arm' in platform.machine()

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
            # Check if running on a Raspberry Pi
            if self.is_raspberry_pi:
                import util.rpi_hardware as rpi_hardware
                if rpi_hardware.mount_usb_drive() == True:
                    openFileName = "/mnt/usb/"+filename
                logFile = open(openFileName, attribs)
                # get file size
                self.input_logFileSize = os.path.getsize(openFileName)
                self.input_logFilePercent = 0
                print("Opening USB Logfile: "+openFileName+" size="+str(self.input_logFileSize))
                return logFile,openFileName
            else:
                pass
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
            shared.GrowlManager.add_message(self.id + ": Playing " + openFileName)
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
        
        return None,None

    #############################################
    ## Method: createLogFile
    ## Create a new log file. (for saving flight data to)
    def createLogFile(self,fileExtension):
        # should we check if the usb drive is available to write to?
        try:
            # if pi then check if the usb drive is mounted
            save_to_usb = _input_file_utils.readConfigBool("DataRecorder", "save_to_usb", False)
            DataRecorderPath = None
            if(self.is_raspberry_pi and save_to_usb):
                import util.rpi_hardware as rpi_hardware
                if (rpi_hardware.mount_usb_drive() == True and self.datarecorder_check_usb == True):
                    DataRecorderPath = "/mnt/usb/"

            if(DataRecorderPath == None):
                DataRecorderPath = _input_file_utils.getDataRecorderDir()
                log_path_format = _input_file_utils.readConfig("DataRecorder", "log_path_format", "%Y/%m/")
                # get todays year and month. create a folder YYYY/MM/
                today = datetime.now()
                # replace the %Y and %m in the log_path_format with the current year and month.
            log_path_format = log_path_format.replace("%Y",str(today.year)).replace("%m",str(today.month)).replace("%d",str(today.day))
            DataRecorderPath = DataRecorderPath + log_path_format
            # create the folder if it doesn't exist.
            if not os.path.exists(DataRecorderPath):
                os.makedirs(DataRecorderPath)

            openFileName = self.getNextLogFile(DataRecorderPath,fileExtension)
            if self.output_logBinary == True:
                logFile = open(openFileName, "w+b")
            else:
                logFile = open(openFileName, "w")
            
            # growl message
            shared.GrowlManager.add_message(self.name + ": Created log : " + openFileName)
            return logFile,openFileName
        except Exception as e: 
            print(e)
            print("Error createLogFile() %s"%(self.name))
            # print full stack trace
            import traceback
            traceback.print_exc()
            return None,None

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
            if self.output_logBinary == True:
                # Ensure dataline is a bytes object before writing
                if isinstance(dataline, str):
                    dataline = dataline.encode('utf-8')
                elif isinstance(dataline, int):
                    dataline = str(dataline).encode('utf-8')
                self.output_logFile.write(dataline)
            else:
                if isinstance(dataline, (bytes, bytearray)):
                    dataline = dataline.decode('utf-8', errors='ignore')
                self.output_logFile.write(dataline)
        except Exception as e:
            print("Error addToLog()")
            print(e)
            import traceback
            traceback.print_exc()

    #############################################
    ## Method: getNextLogFile
    ## get next log file to open.
    def getNextLogFile(self,dirname,fileExtension):
        from os.path import exists
        #print("getNextLogFile() "+dirname+" "+fileExtension)
        file_format = _input_file_utils.readConfig("DataRecorder", "log_file_format", "%Y_%m_%d_%INPUT")

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
    ## Function: startLog
    ## tell this input to create log file and start logging data
    def startLog(self,aircraft):
        if self.output_logFile == None:
            self.output_logFile,self.output_logFileName = Input.createLogFile(self,".dat")
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
            try:
                if self.PlayFile != None:
                    current = self.ser.tell()
                    moveTo = current - bytesToSkip
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
