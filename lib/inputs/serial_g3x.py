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
import time

class serial_g3x(Input):
    def __init__(self):
        self.name = "g3x"
        self.version = 1.0
        self.inputtype = "serial"

    def initInput(self,aircraft):
        Input.initInput( self, aircraft )  # call parent init Input.

        if aircraft.demoMode:
            # if in demo mode then load example data file.
            self.ser = open("lib/inputs/_example_data/garmin_g3x_data1.txt", "r") 
        else:
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
        if aircraft.errorFoundNeedToExit:
            return aircraft;
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
                                if EWVelDir == "W":
                                    EWVelmag = int(EWVelmag) * -0.1
                                else:
                                    EWVelmag = int(EWVelmag) * 0.1
                                if NSVelDir == "S":
                                    NSVelmag = int(NSVelmag) * -0.1
                                else:
                                    NSVelmag = int(NSVelmag) * 0.1
                                aircraft.gndtrack = math.degrees(math.atan2(EWVelmag, NSVelmag))
                                if aircraft.gndtrack < 0:
                                    aircraft.gndtrack = aircraft.gndtrack + 360
                                if aircraft.tas > 30 and aircraft.gndspeed > 30:
                                    crs = math.radians(aircraft.gndtrack) #convert degrees to radians
                                    head = math.radians(aircraft.mag_head) #convert degrees to radians
                                    aircraft.wind_speed = math.sqrt(math.pow(aircraft.tas - aircraft.gndspeed, 2) + 4 * aircraft.tas * aircraft.gndspeed * math.pow(math.sin((head - crs) / 2), 2))
                                    aircraft.wind_dir = crs + math.atan2(aircraft.tas * math.sin(head-crs), aircraft.tas * math.cos(head-crs) - aircraft.gndspeed)
                                    if aircraft.wind_dir < 0:
                                        aircraft.wind_dir = aircraft.wind_dir + 2 * math.pi
                                    if aircraft.wind_dir > 2 * math.pi:
                                        aircraft.wind_dir = aircraft.wind_dir - 2 * math.pi
                                    aircraft.wind_dir = math.degrees(aircraft.wind_dir) #convert radians to degrees
                                    aircraft.norm_wind_dir = aircraft.wind_dir + aircraft.mag_head #normalize the wind direction to the airplane heading
                                    if aircraft.norm_wind_dir > 359:
                                        aircraft.norm_wind_dir = aircraft.norm_wind_dir - 360 
                                else:
                                    aircraft.wind_speed = None
                                    aircraft.wind_dir = None
                        
                            else:
                                aircraft.msg_bad += 1 
                else:
                    if aircraft.demoMode:  # if no bytes read and in demo mode.  then reset the file pointer to the start of the file.
                        self.ser.seek(0)
                    return aircraft

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
                        aircraft.ias = int(int(Airspeed) * 0.1)
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
                        aircraft.vert_G = int(VertAcc) * 0.1
                        aircraft.turn_rate = int(RateofTurn) * 0.1
                        aircraft.msg_count += 1
                    
                        if aircraft.demoMode:  #if demo mode then add a delay.  Else reading a file is way to fast.
                            time.sleep(.08)                    
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
                if aircraft.demoMode:  
                    time.sleep(.01)
                else:
                    self.ser.flushInput()  # flush the serial after every message else we see delays
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

