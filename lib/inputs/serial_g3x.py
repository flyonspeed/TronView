#!/usr/bin/env python

# Serial input source
# Garmin G3X
# 01/30/2019 Brian Chesteen, credit to Christopher Jones for developing template for input modules.
# 06/18/2023 C.Jones fix for live serial data input.
# 07/28/2024 A.O. grab DA and TAS from G3X Sentence ID 2 versus calculating from SID 1

from ._input import Input
from lib import hud_utils
from lib import hud_text
from lib import geomag
from . import _utils
import serial
import struct
import math, sys
import time


class serial_g3x(Input):
    def __init__(self):
        self.name = "g3x"
        self.version = 1.1
        self.inputtype = "serial"

        # Setup moving averages to smooth a bit
        self.readings = []
        self.max_samples = 10
        self.readings1 = []
        self.max_samples1 = 20
        self.EOL = 10

    def initInput(self,num, aircraft):
        Input.initInput(self,num, aircraft)  # call parent init Input.
        if(aircraft.inputs[self.inputNum].PlayFile!=None):
            # play a log file?
            if aircraft.inputs[self.inputNum].PlayFile==True:
                defaultTo = "garmin_g3x_data1.txt"
                aircraft.inputs[self.inputNum].PlayFile = hud_utils.readConfig(self.name, "playback_file", defaultTo)
            self.ser,self.input_logFileName = Input.openLogFile(self,aircraft.inputs[self.inputNum].PlayFile,"r")
            self.isPlaybackMode = True
        else:
            self.efis_data_format = hud_utils.readConfig("DataInput", "format", "none")
            self.efis_data_port = hud_utils.readConfig(
                "DataInput", "port", "/dev/ttyS0"
            )
            self.efis_data_baudrate = hud_utils.readConfigInt(
                "DataInput", "baudrate", 115200
            )
            # open serial connection.
            self.ser = serial.Serial(
                port=self.efis_data_port,
                baudrate=self.efis_data_baudrate,
                parity=serial.PARITY_NONE,
                stopbits=serial.STOPBITS_ONE,
                bytesize=serial.EIGHTBITS,
                timeout=1,
            )

        # check for system platform??
        #if sys.platform.startswith('win'):
        #    self.EOL = 10
        #else:
        #    self.EOL = 13
        self.EOL = 13

    # close this input source
    def closeInput(self, aircraft):
        if self.isPlaybackMode:
            self.ser.close()
        else:
            self.ser.close()

    #############################################
    ## Function: readMessage
    def readMessage(self, aircraft):
        def mean(nums):
            return float(sum(nums)) / max(len(nums), 1)

        if aircraft.errorFoundNeedToExit:
            return aircraft
        try:
            x = 0
            while x != 61:  # 61(=) is start of garmin g3x sentence.
                t = self.ser.read(1)
                if len(t) != 0:
                    x = ord(t)
                    if x == 64:  # 64(@) is start of garmin g3x GPS sentence.
                        msg = self.ser.read(56)
                        if(isinstance(msg,str)): msg = msg.encode() # if read from file then convert to bytes
                        aircraft.msg_last = msg
                        if len(msg) == 56:
                            UTCYear, UTCMonth, UTCDay, UTCHour, UTCMin, UTCSec, LatHemi, LatDeg, LatMin, LonHemi, LonDeg, LonMin, PosStat, HPE, GPSAlt, EWVelDir, EWVelmag, NSVelDir, NSVelmag, VVelDir, VVelmag, CRLF = struct.unpack(
                                "2s2s2s2s2s2sc2s5sc3s5sc3s6sc4sc4sc4s2s", msg
                            )
                            if CRLF[0] == self.EOL:
                                aircraft.msg_count += 1
                                aircraft.sys_time_string = "%d:%d:%d"%(int(UTCHour),int(UTCMin),int(UTCSec))
                                self.time_stamp_string = aircraft.sys_time_string
                                self.time_stamp_min = int(UTCMin)
                                self.time_stamp_sec = int(UTCSec)
                                aircraft.gps.LatHemi = LatHemi  # North or South
                                aircraft.gps.LatDeg = int(LatDeg)
                                aircraft.gps.LatMin = int(LatMin) * 0.001  # x.xxx
                                aircraft.gps.LonHemi = LonHemi  # East or West
                                aircraft.gps.LonDeg = int(LonDeg)
                                aircraft.gps.LonMin = int(LonMin) * 0.001  # x.xxx
                                aircraft.gps.GPSAlt = int(GPSAlt) * 3.28084
                                aircraft.gps.EWVelDir = EWVelDir  # E or W
                                aircraft.gps.EWVelmag = int(EWVelmag) * 0.1
                                aircraft.gps.NSVelDir = NSVelDir  # N or S
                                aircraft.gps.NSVelmag = int(NSVelmag) * 0.1
                                aircraft.gps.VVelDir = VVelDir  # U or D
                                aircraft.gps.VVelmag = int(VVelmag) * 0.1
                                aircraft.mag_decl = _utils.geomag(
                                    aircraft.gps.LatHemi,
                                    aircraft.gps.LatDeg,
                                    aircraft.gps.LatMin,
                                    aircraft.gps.LonHemi,
                                    aircraft.gps.LonDeg,
                                    aircraft.gps.LonMin,
                                )
                                aircraft.gndspeed = _utils.gndspeed(EWVelmag, NSVelmag) * 1.15078 # convert back to mph
                                aircraft.gndtrack = _utils.gndtrack(
                                    EWVelDir, EWVelmag, NSVelDir, NSVelmag
                                )
                                aircraft.gps.Source = "G3X"
                                aircraft.wind_speed, aircraft.wind_dir, aircraft.norm_wind_dir = _utils.windSpdDir(
                                    aircraft.tas * 0.8689758, # back to knots.
                                    aircraft.gndspeed * 0.8689758, # convert back to knots
                                    aircraft.gndtrack,
                                    aircraft.mag_head,
                                    aircraft.mag_decl,
                                )
                                if self.output_logFile != None:
                                    Input.addToLog(self,self.output_logFile,bytes([64]))
                                    Input.addToLog(self,self.output_logFile,msg)

                                aircraft.gps.msg_count += 1
                            else:
                                aircraft.gps.msg_bad += 1

                else:
                    if (self.isPlaybackMode ):  # if no bytes read and in playback mode.  then reset the file pointer to the start of the file.
                        self.ser.seek(0)
                    return aircraft

            SentID = int(self.ser.read(1)) # get message id

            if SentID == 1:  # atittude/air data message
                msg = self.ser.read(57)
                aircraft.msg_last = msg
                if len(msg) == 57:
                    if(isinstance(msg,str)): msg = msg.encode() # if read from file then convert to bytes
                    SentVer, UTCHour, UTCMin, UTCSec, UTCSecFrac, Pitch, Roll, Heading, Airspeed, PressAlt, RateofTurn, LatAcc, VertAcc, AOA, VertSpeed, OAT, AltSet, Checksum, CRLF = struct.unpack(
                        "c2s2s2s2s4s5s3s4s6s4s3s3s2s4s3s3s2s2s", msg
                    )
                    if int(SentVer) == 1 and CRLF[0] == self.EOL:
                        aircraft.roll = int(Roll) * 0.1
                        aircraft.pitch = int(Pitch) * 0.1
                        aircraft.ias = int(Airspeed) * 0.115078 # convert knots to mph * 0.1
                        aircraft.PALT = int(PressAlt)
                        aircraft.oat = (int(OAT) * 1.8) + 32 # c to f
                        if _utils.is_number(AOA) == True:
                            aircraft.aoa = int(AOA)
                            self.readings1.append(aircraft.aoa)
                            aircraft.aoa = mean(
                                self.readings1
                            )  # Moving average to smooth a bit
                        else:
                            aircraft.aoa = 0
                        if len(self.readings1) == self.max_samples1:
                            self.readings1.pop(0)
                        aircraft.mag_head = int(Heading)
                        aircraft.baro = (int(AltSet) + 2750.0) / 100.0
                        aircraft.baro_diff = aircraft.baro - 29.9213
                        aircraft.alt = int(
                            int(PressAlt) + (aircraft.baro_diff / 0.00108)
                        )  # 0.00108 of inches of mercury change per foot.
                        aircraft.BALT = aircraft.alt
                        aircraft.vsi = int(VertSpeed) * 10 # vertical speed in fpm
                        aircraft.turn_rate = int(RateofTurn) * 0.1
                        aircraft.vert_G = int(VertAcc) * 0.1
                        aircraft.slip_skid = int(LatAcc) * 0.01
                        self.readings.append(aircraft.slip_skid)
                        aircraft.slip_skid = mean(
                            self.readings
                        )  # Moving average to smooth a bit
                        if len(self.readings) == self.max_samples:
                            self.readings.pop(0)
                        aircraft.msg_count += 1
                        if (self.isPlaybackMode):  # if playback mode then add a delay.  Else reading a file is way to fast.
                            time.sleep(0.08)

                        if self.output_logFile != None:
                            #Input.addToLog(self,self.output_logFile,bytes([61,ord(SentID)]))
                            Input.addToLog(self,self.output_logFile,msg)


                    else:
                        aircraft.msg_bad += 1

                else:
                    aircraft.msg_bad += 1
            elif SentID == 2:
                msg = self.ser.read(40)
                aircraft.msg_last = msg
                if len(msg) == 40:
                    if(isinstance(msg,str)): msg = msg.encode() # if read from file then convert to bytes
                    SentVer, UTCHour, UTCMin, UTCSec, UTCSecFrac, TAS, DAlt, HeadingSel, AltSel, AirspeedSel, VSSel, Checksum, CRLF = struct.unpack(
                        "c2s2s2s2s4s6s3s6s4s4s2s2s", msg
                    )
                    if int(SentVer) == 1 and CRLF[0] == self.EOL:
                        aircraft.DA = int(DAlt)
                        aircraft.tas = int(TAS) * 0.115078 # convert knots to mph * 0.1
                        aircraft.nav.HeadBug = int(HeadingSel)
                        aircraft.nav.AltBug = int(AltSel)
                        aircraft.nav.ASIBug = int(AirspeedSel) * 0.115078 # convert knots to mph * 0.1
                        aircraft.nav.VSIBug = int(VSSel) * 10 # multiply up to hundreds of feet
                        aircraft.msg_count += 1
                        if (self.isPlaybackMode):  # if playback mode then add a delay.  Else reading a file is way to fast.
                            time.sleep(0.08)

                        if self.output_logFile != None:
                            #Input.addToLog(self,self.output_logFile,bytes([61,ord(SentID)]))
                            Input.addToLog(self,self.output_logFile,msg)


                    else:
                        aircraft.msg_bad += 1

                else:
                    aircraft.msg_bad += 1
            elif SentID == 7:  # GPS AGL data message
                msg = self.ser.read(16)
                if(isinstance(msg,str)): msg = msg.encode() # if read from file then convert to bytes
                aircraft.msg_last = msg
                if len(msg) == 16:
                    msg = (msg[:16]) if len(msg) > 16 else msg
                    SentVer, UTCHour, UTCMin, UTCSec, UTCSecFrac, HeightAGL, Checksum, CRLF = struct.unpack(
                        "c2s2s2s2s3s2s2s", msg
                    )
                    if int(SentVer) == 1 and CRLF[0] == self.EOL:
                        aircraft.agl = int(HeightAGL) * 100
                        aircraft.msg_count += 1
                        if self.output_logFile != None:
                            #Input.addToLog(self,self.output_logFile,bytes([61,ord(SentID)]))
                            Input.addToLog(self,self.output_logFile,msg)

                    else:
                        aircraft.msg_bad += 1
                        aircraft.debug1 = "bad GPS AGL data - unkown ver"

                else:
                    aircraft.msg_bad += 1
                    aircraft.debug1 = "bad GPS AGL data - wrong length"

            else:
                aircraft.debug2 = SentID
                aircraft.msg_unknown += 1  # else unknown message.
                if self.isPlaybackMode:
                    time.sleep(0.01)
                else:
                    self.ser.flushInput()  # flush the serial after every message else we see delays
                return aircraft

        except serial.serialutil.SerialException as e:
            print(e)
            print("G3X serial exception")
            aircraft.errorFoundNeedToExit = True

        return aircraft




# vi: modeline tabstop=8 expandtab shiftwidth=4 softtabstop=4 syntax=python
