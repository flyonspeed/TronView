#!/usr/bin/env python

# Serial input source
# Garmin G3X
# 01/30/2019 Brian Chesteen, credit to Christopher Jones for developing template for input modules.

from __future__ import print_function
from _input import Input
from lib import hud_utils
import serial
import struct
import math
from lib import hud_text

class serial_g3x(Input):
    def __init__(self):
        self.name = "g3x"
        self.version = 1.0
        self.inputtype = "serial"

    def initInput(self,aircraft):
        Input.initInput( self, aircraft )  # call parent init Input.

        # TODO: if aircraft.demoMode then load example demo data instead of opening serial data.

        self.efis_data_format = hud_utils.readConfig("DataInput", "format", "none")
        self.efis_data_port = hud_utils.readConfig("DataInput", "port", "/dev/ttyS0")
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

    # close this input source
    def closeInput(self,aircraft):
        if aircraft.demoMode:
            self.ser.close()
        else:
            self.ser.close()

    #############################################
    ## Function: readMessage
    def readMessage(self, aircraft):
        try:
            x = 0
            while x != 61:  # 61(=) is start of garmin g3x sentence.
                t = self.ser.read(1)
                if len(t) != 0:
                    x = ord(t)
                    if x == 64:   # 64(@) is start of garmin g3x GPS sentence.
                        msg = self.ser.read(56)  
                        aircraft.msg_last = msg
                        if len(msg) == 56:
                            msg = (msg[:56]) if len(msg) > 56 else msg
                            UTCYear, UTCMonth, UTCDay, UTCHour, UTCMin, UTCSec, LatHemi, LatDeg, LatMin, LonHemi, LonDeg, LonMin, PosStat, HPE, GPSAlt, EWVelDir, EWVelmag, NSVelDir, NSVelmag, VVelDir, VVelmag, CRLF = struct.unpack(
                            "2s2s2s2s2s2sc2s5sc3s5sc3s6sc4sc4sc4s2s", msg
                            )                    
                            if ord(CRLF[0]) ==13:
                                aircraft.msg_count += 1
                                aircraft.gndspeed = (math.sqrt(((int(EWVelmag) * 0.1)**2) + ((int(NSVelmag) * 0.1)**2))) * 1.94384
                            else:
                                aircraft.msg_bad += 1 

            SentID = self.ser.read(1)
            
            if SentID == "1": #atittude/air data message
                msg = self.ser.read(57)
                aircraft.msg_last = msg
                if len(msg) == 57:
                    msg = (msg[:57]) if len(msg) > 57 else msg
                    SentVer, UTCHour, UTCMin, UTCSec, UTCSecFrac, Pitch, Roll, Heading, Airspeed, PressAlt, RateofTurn, LatAcc, VertAcc, AOA, VertSpeed, OAT, AltSet, Checksum, CRLF = struct.unpack(
                    "c2s2s2s2s4s5s3s4s6s4s3s3s2s4s3s3s2s2s", msg
                    )
                    if SentVer == "1" and ord(CRLF[0]) == 13:
                        aircraft.roll = int(Roll) * 0.1
                        aircraft.pitch = int(Pitch) * 0.1
                        aircraft.ias = int(Airspeed) * 0.1
                        aircraft.PALT = int(PressAlt)
                        aircraft.oat = int(OAT)
                        aircraft.aoa = int(AOA)
                        aircraft.mag_head = int(Heading)
                        aircraft.baro = (int(AltSet) + 2750.0) / 100.0
                        aircraft.baro_diff = aircraft.baro - 29.9213
                        aircraft.alt = int(
                            int(PressAlt) + (aircraft.baro_diff / 0.00108)
                        )  # 0.00108 of inches of mercury change per foot.
                        aircraft.BALT = aircraft.alt
                        aircraft.vsi = int(VertSpeed) * 10
                        aircraft.tas = aircraft.ias * (math.sqrt((273.0 + aircraft.oat) / 288.0)) * ((1.0 - aircraft.PALT / 144000.0) ** -2.75)
                        aircraft.msg_count += 1
                    else:
                        aircraft.msg_bad += 1
                        
                else:
                    aircraft.msg_bad += 1

            elif SentID == "7": #GPS AGL data message
                msg = self.ser.read(16)  
                aircraft.msg_last = msg
                if len(msg) == 16:
                    msg = (msg[:16]) if len(msg) > 16 else msg
                    SentVer, UTCHour, UTCMin, UTCSec, UTCSecFrac, HeightAGL, Checksum, CRLF = struct.unpack(
                    "c2s2s2s2s3s2s2s", msg
                    )
                    if SentVer == "1" and ord(CRLF[0]) == 13:
                        aircraft.agl = int(HeightAGL) * 100
                        aircraft.msg_count += 1
                    else:
                        aircraft.msg_bad += 1
                        
                else:
                    aircraft.msg_bad += 1                        

            else:
                aircraft.msg_unknown += 1 #else unknown message.
                self.ser.flushInput()
                return aircraft
            
        except serial.serialutil.SerialException:
            print("G3X serial exception")
            aircraft.errorFoundNeedToExit = True
        
        return aircraft


    #############################################
    ## Function: printTextModeData
    def printTextModeData(self, aircraft):
        hud_text.print_header("Decoded data from Input Module: %s"%(self.name))
        hud_text.print_object(aircraft)
        hud_text.print_DoneWithPage()

# vi: modeline tabstop=8 expandtab shiftwidth=4 softtabstop=4 syntax=python

