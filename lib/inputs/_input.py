#!/usr/bin/env python

# Input class.
# All input types should inherit from this class.

from lib import hud_text

class Input:
    def __init__(self):
        self.name = "Input Class"
        self.version = 1.0
        self.inputtype = ""
        self.log_line_prefix = None
        self.log_line_suffix = None

    def initInput(self, aircraft):
        pass

    def setLogLinePrefixSuffix(self,Start,EOL):
        self.log_line_prefix = Start
        self.log_line_suffix = EOL

    #############################################
    ## Method: openLogFile
    def openLogFile(self,filename,attribs):
        try:
            openFileName = "/tmp/"+filename
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
        openFileName = self.getNextLogFile("/tmp/",fileExtension)
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
