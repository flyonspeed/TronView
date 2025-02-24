#!/usr/bin/env python

# Serial input source
# Generic serial logger
# 10/14/2021 Topher
# 1/3/2025 Added dataship refacor

from ._input import Input
from lib import hud_utils
from . import _utils
import serial
import struct
from lib import hud_text
import binascii
import time
import datetime
from ..common.dataship.dataship import Dataship
from ..common.dataship.dataship_imu import IMUData
from ..common.dataship.dataship_gps import GPSData
from ..common.dataship.dataship_air import AirData
from ..common.dataship.dataship_targets import TargetData, Target
from ._input import Input
from ..common import shared
from . import _input_file_utils


class serial_logger(Input):
    def __init__(self):
        self.name = "serial_logger"
        self.version = 1.0
        self.inputtype = "serial"

    def initInput(self,num,dataship: Dataship):
        Input.initInput( self,num, dataship )  # call parent init Input.
        if(self.PlayFile!=None):
            print("serial_logger can not play back files. Only used to record data.")
            dataship.errorFoundNeedToExit = True
        else:
            self.efis_data_port = hud_utils.readConfig(self.name, "port", "/dev/ttyS0")
            self.efis_data_baudrate = hud_utils.readConfigInt(
                self.name, "baudrate", 115200
            )
            self.read_in_size = hud_utils.readConfigInt( self.name, "read_in_size", 100)

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

    def closeInput(self,dataship: Dataship):
        if self.isPlaybackMode == True:
            dataship.errorFoundNeedToExit = True
        else:
            self.ser.close()

    #############################################
    ## Function: readMessage
    def readMessage(self, dataship: Dataship):
        if self.shouldExit == True: dataship.errorFoundNeedToExit = True
        if dataship.errorFoundNeedToExit: return dataship
        if self.skipReadInput == True: return dataship
        try:
            Message = self.ser.read(self.read_in_size)

            if(len(Message)==0):
                dataship.msg_last = "No serial data recieved"
                return dataship

            #dataship.msg_count += 1
            #dataship.msg_last = binascii.hexlify(Message) # save last message.

            # make the aircraft look like it's doing something.
            #if(dataship.roll>180): dataship.roll = -180
            #dataship.roll = dataship.roll + .1  #

            #dataship.sys_time_string = datetime.datetime.now().time()

            if self.output_logFile != None:
                Input.addToLog(self,self.output_logFile,Message)

        except serial.serialutil.SerialException:
            print("serial_logger exception")
            dataship.errorFoundNeedToExit = True
        return dataship




# vi: modeline tabstop=8 expandtab shiftwidth=4 softtabstop=4 syntax=python
