#!/usr/bin/env python

# Serial Meshtastic input source
# 2/26/2025  Topher

from ._input import Input
from lib import hud_utils
import serial
import struct
from lib import hud_text
import time
import traceback
from lib.common.dataship.dataship import IMUData
from lib.common.dataship.dataship import Dataship
from lib.common.dataship.dataship_air import AirData
from ..common.dataship.dataship_targets import TargetData, Target
import meshtastic

class serial_d100(Input):
    def __init__(self):
        self.name = "meshtastic"
        self.version = 1.0
        self.inputtype = "serial"
        self.imuData = IMUData()
        self.airData = AirData()
        self.targetData = TargetData()

    def initInput(self,num,dataship: Dataship):
        Input.initInput( self,num, dataship )  # call parent init Input.
        self.msg_unknown = 0
        self.msg_bad = 0
        
        if(self.PlayFile!=None and self.PlayFile!=False):
            # load log file to playback.
            if self.PlayFile==True:
                defaultTo = "meshtastic_data1.txt"
                self.PlayFile = hud_utils.readConfig(self.name, "playback_file", defaultTo)
            self.ser,self.input_logFileName = Input.openLogFile(self,self.PlayFile,"r")
        else:
            self.efis_data_port = hud_utils.readConfig(self.name, "port", "/dev/ttyS0")
            self.efis_data_baudrate = hud_utils.readConfigInt( self.name, "baudrate", 115200 )


    # close this data input 
    def closeInput(self,dataship: Dataship):
        if self.isPlaybackMode:
            self.ser.close()
        else:
            self.ser.close()

    #############################################
    ## Function: readMessage
    def readMessage(self, dataship: Dataship):
        if dataship.errorFoundNeedToExit:
            return dataship;
        try:
            
                return dataship
        except ValueError as ex:
            print("conversion error")
            print(ex)
            traceback.print_exc()
            dataship.errorFoundNeedToExit = True
        except Exception as e:
            dataship.errorFoundNeedToExit = True
            print(e)
            print(traceback.format_exc())
        return dataship

# vi: modeline tabstop=8 expandtab shiftwidth=4 softtabstop=4 syntax=python
