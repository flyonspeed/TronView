#!/usr/bin/env python

# ads1115 input source


from ._input import Input
from lib import hud_utils
from . import _utils
import struct
import time
import Adafruit_ADS1x15
import statistics
import traceback
from lib.common.dataship.dataship import Dataship
from lib.common.dataship.dataship_analog import AnalogData
from lib.common.dataship.dataship_nav import NavData

class adc_ads1115(Input):
    def __init__(self):
        self.name = "ads1115"
        self.version = 1.0
        self.inputtype = "adc"
        self.values = []
        self.ApplySmoothing = 1
        self.SmoothingAVGMaxCount = 10
        self.smoothingA = []
        self.smoothingB = []
        self.analogData = AnalogData()

    def initInput(self,num,dataship: Dataship):
        Input.initInput( self,num, dataship )  # call parent init Input.
        if(self.PlayFile!=None):
            self.isPlaybackMode = True
        else:
            self.isPlaybackMode = False

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
        self.GAIN = 2/3 
        dataship.analog.Name = "ads1115"
        self.Amplify = 6.144/32767
        self.values = [0,0,0,0,0,0,0,0]

        # create analog data object.
        self.analogData = AnalogData()
        self.analogData.name = self.name
        self.index = len(dataship.analogData)
        self.analogData.id = self.name + "_" + str(self.index)
        dataship.analogData.append(self.analogData)

        # create nav data object.
        self.navData = NavData()
        self.navData.name = self.name
        self.index = len(dataship.navData)
        self.navData.id = self.name + "_" + str(self.index)
        dataship.navData.append(self.navData)

    def closeInput(self,dataship: Dataship):
        print("ads1115 close")


    #############################################
    ## Function: readMessage
    def readMessage(self, dataship: Dataship):
        if self.shouldExit == True: dataship.errorFoundNeedToExit = True
        if dataship.errorFoundNeedToExit: return dataship
        if self.skipReadInput == True: return dataship

        try:
            time.sleep(0.025) # delay because of i2c read.
            self.values[1] = self.adc.read_adc_difference(0, gain=self.GAIN) * self.Amplify
            time.sleep(0.025)
            self.values[0] = self.adc.read_adc_difference(3, gain=self.GAIN) * self.Amplify

            # apply smoothing avg of adc values?
            if(self.ApplySmoothing):
                self.smoothingA.append(self.values[0])
                if(len(self.smoothingA)>self.SmoothingAVGMaxCount): self.smoothingA.pop(0)
                self.analogData.Data[0] = statistics.mean(self.smoothingA)

                self.smoothingB.append(self.values[1])
                if(len(self.smoothingB)>self.SmoothingAVGMaxCount): self.smoothingB.pop(0)
                self.analogData.Data[1] = statistics.mean(self.smoothingB)
            else:
                #else don't apply smoothing.
                self.analogData.Data = self.values

            # TODO: have config file define what this analog input is for.

            # if analog input is for nav needles.. .then.
            # limit the output voltages to be within +/- 0.25V
            # format value to +/- 4095 for needle left/right up/down.
            self.navData.GSDev = round (16380 * (max(min(self.analogData.Data[0], 0.25), -0.25)))
            self.navData.ILSDev = round (16380 * (max(min(self.analogData.Data[1], 0.25), -0.25)))

        except Exception as e:
            dataship.errorFoundNeedToExit = True
            print(e)
            print(traceback.format_exc())
        return dataship




# vi: modeline tabstop=8 expandtab shiftwidth=4 softtabstop=4 syntax=python
