#!/usr/bin/env python

# Serial input source
# Generic serial logger
# 10/14/2021 Christopher Jones

from ._input import Input
from lib import hud_utils
from . import _utils
import serial
import struct
from lib import hud_text
import binascii
import time
import datetime

class serial_logger(Input):
    def __init__(self):
        self.name = "logger"
        self.version = 1.0
        self.inputtype = "serial"

    def initInput(self,num,aircraft):
        Input.initInput( self,num, aircraft )  # call parent init Input.
        if(aircraft.inputs[self.inputNum].PlayFile!=None):
            print("serial_logger can not play back files. Only used to record data.")
            aircraft.errorFoundNeedToExit = True
        else:
            self.efis_data_port = hud_utils.readConfig("DataInput", "port", "/dev/ttyS0")
            self.efis_data_baudrate = hud_utils.readConfigInt(
                "DataInput", "baudrate", 115200
            )
            self.read_in_size = hud_utils.readConfigInt( "DataInput", "read_in_size", 100)

            # open serial connection.
            self.ser = serial.Serial(
                port=self.efis_data_port,
                baudrate=self.efis_data_baudrate,
                parity=serial.PARITY_NONE,
                stopbits=serial.STOPBITS_ONE,
                bytesize=serial.EIGHTBITS,
                timeout=1,
            )

            self.textMode_whatToShow = 1 # default to only showing basic air info.
            self.textMode_showRaw = true

    def closeInput(self,aircraft):
        if self.isPlaybackMode = True:
            aircraft.errorFoundNeedToExit = True
        else:
            self.ser.close()

    #############################################
    ## Function: readMessage
    def readMessage(self, aircraft):
        if self.shouldExit == True: aircraft.errorFoundNeedToExit = True
        if aircraft.errorFoundNeedToExit: return aircraft
        if self.skipReadInput == True: return aircraft
        try:
            Message = self.ser.read(self.read_in_size)

            if(len(Message)==0):
                aircraft.msg_last = "No serial data recieved"
                return aircraft

            aircraft.msg_count += 1
            aircraft.msg_last = binascii.hexlify(Message) # save last message.

            # make the aircraft look like it's doing something.
            if(aircraft.roll>180): aircraft.roll = -180
            aircraft.roll = aircraft.roll + .1  #

            aircraft.sys_time_string = datetime.datetime.now().time()

            if self.output_logFile != None:
                Input.addToLog(self,self.output_logFile,Message)

        except serial.serialutil.SerialException:
            print("serial_logger exception")
            aircraft.errorFoundNeedToExit = True
        return aircraft




# vi: modeline tabstop=8 expandtab shiftwidth=4 softtabstop=4 syntax=python
