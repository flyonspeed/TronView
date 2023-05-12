#!/usr/bin/env python

# ads1115 input source


from ._input import Input
from lib import hud_utils
from . import _utils
import struct
import time
import Adafruit_ADS1x15

class adc_ads1115(Input):
    def __init__(self):
        self.name = "ads1115"
        self.version = 1.0
        self.inputtype = "adc"

    def initInput(self,num,aircraft):
        Input.initInput( self,num, aircraft )  # call parent init Input.
        if(aircraft.inputs[self.inputNum].PlayFile!=None):
            # Get playback file.
            #if aircraft.inputs[self.inputNum].PlayFile==True:
            #    defaultTo = "ads1115_Flight1.bin"
            #    aircraft.inputs[self.inputNum].PlayFile = hud_utils.readConfig(self.name, "playback_file", defaultTo)
            #self.ser,self.input_logFileName = Input.openLogFile(self,aircraft.inputs[self.inputNum].PlayFile,"rb")
            self.isPlaybackMode = True
        else:
            self.isPlaybackMode = False
            #self.efis_data_format = hud_utils.readConfig("DataInput", "format", "none")
            #self.efis_data_port = hud_utils.readConfig("DataInput", "port", "/dev/ttyS0")
            #self.efis_data_baudrate = hud_utils.readConfigInt(
            #    "DataInput", "baudrate", 115200
            #)

        # setup comm i2c to chipset.
        self.adc = Adafruit_ADS1x15.ADS1115()
        # Choose a gain of 1 for reading voltages from 0 to 4.09V.
        # Or pick a different gain to change the range of voltages that are read:
        #  - 2/3 = +/-6.144V
        #  -   1 = +/-4.096V
        #  -   2 = +/-2.048V
        #  -   4 = +/-1.024V
        #  -   8 = +/-0.512V
        #  -  16 = +/-0.256V
        # See table 3 in the ADS1015/ADS1115 datasheet for more info on gain.
        self.GAIN = 16



    def closeInput(self,aircraft):
        print("ads1115 close")


    #############################################
    ## Function: readMessage
    def readMessage(self, aircraft):
        if self.shouldExit == True: aircraft.errorFoundNeedToExit = True
        if aircraft.errorFoundNeedToExit: return aircraft
        if self.skipReadInput == True: return aircraft


        self.values = [0]*4
        for self.i in range(4):
            time.sleep(0.05)
            # Read the specified ADC channel using the previously set gain value.
            self.values[i] = self.adc.read_adc(self.i, gain=self.GAIN)



        aircraft.nav.ILSDev = self.values[0]
        aircraft.nav.GSDev = self.values[1]

        #aircraft.nav.GLSHoriz = GLSHoriz
        #aircraft.nav.GLSVert = GLSVert

        #aircraft.nav.msg_count += 1
        #if(self.textMode_showRaw==True): aircraft.nav.msg_last = binascii.hexlify(Message) # save last message.
        #else: aircraft.nav.msg_last = None



        return aircraft




# vi: modeline tabstop=8 expandtab shiftwidth=4 softtabstop=4 syntax=python
