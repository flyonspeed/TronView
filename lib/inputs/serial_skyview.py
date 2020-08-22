#!/usr/bin/env python

# Serial input source
# Skyview
# 1/23/2019 Christopher Jones
from __future__ import print_function
from _input import Input
from lib import hud_utils
import math, sys
import serial
import struct
from lib import hud_text
import time

class serial_skyview(Input):
    def __init__(self):
        self.name = "skyview"
        self.version = 1.0
        self.inputtype = "serial"

    def initInput(self,aircraft):
        Input.initInput( self, aircraft )  # call parent init Input.
        
        if aircraft.demoMode:
            # if in demo mode then load example data file.
            self.ser = open("lib/inputs/_example_data/dynon_skyview_data1.txt", "r") 
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

    # close this data input 
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
            while x != 33:  # 33(!) is start of dynon skyview.
                t = self.ser.read(1)
                if len(t) != 0:
                    x = ord(t)
                else:
                    if aircraft.demoMode:  # if no bytes read and in demo mode.  then reset the file pointer to the start of the file.
                        self.ser.seek(0)
                    return aircraft
            msg = self.ser.read(73)  # 91 ?
            if len(msg) == 73:
                msg = (msg[:73]) if len(msg) > 73 else msg
                aircraft.msg_last = msg
                dataType, DataVer, SysTime, pitch, roll, HeadingMAG, IAS, PresAlt, TurnRate, LatAccel, VertAccel, AOA, VertSpd, OAT, TAS, Baro, DA, WD, WS, Checksum, CRLF = struct.unpack(
                    "cc8s4s5s3s4s6s4s3s3s2s4s3s4s3s6s3s2s2s2s", msg
                )
                EOL = 0
                if sys.platform.startswith('win'):
                    EOL = 10
                else:
                    EOL = 13
                if dataType == "1" and ord(CRLF[0]) == EOL:  # AHRS message
                    aircraft.sys_time_string = SysTime
                    aircraft.roll = int(roll) * 0.1
                    aircraft.pitch = int(pitch) * 0.1
                    aircraft.ias = int(IAS) * 0.1
                    aircraft.PALT = int(PresAlt)
                    aircraft.OAT = int(OAT)
                    aircraft.tas = int(TAS) * 0.1
                    if AOA == "XX":
                        aircraft.aoa = 0
                    else:
                        aircraft.aoa = int(AOA)
                    aircraft.mag_head = int(HeadingMAG)

                    aircraft.baro = (int(Baro) + 2750.0) / 100
                    aircraft.baro_diff = aircraft.baro - 29.921
                    aircraft.DA = int(DA)
                    aircraft.alt = int( int(PresAlt) + (aircraft.baro_diff / 0.00108) )  # 0.00108 of inches of mercury change per foot.
                    aircraft.BALT = aircraft.alt
                    aircraft.turn_rate = int(TurnRate) * 0.1
                    aircraft.vsi = int(VertSpd) * 10
                    aircraft.vert_G = int(VertAccel) * 0.1
                    try:
                        aircraft.wind_dir = int(WD)
                        aircraft.wind_speed = int(WS)
                        aircraft.norm_wind_dir = (aircraft.mag_head - aircraft.wind_dir) % 360 #normalize the wind direction to the airplane heading
                        # compute Gnd Speed when Gnd Speed is unknown (not provided in data)
                        aircraft.gndspeed = math.sqrt(math.pow(aircraft.tas,2) + math.pow(aircraft.wind_speed,2) + (2 * aircraft.tas * aircraft.wind_speed * math.cos(math.radians(180 - (aircraft.wind_dir - aircraft.mag_head)))))
                        aircraft.gndtrack = aircraft.mag_head 
                    except ValueError as ex:
                        # if error trying to parse wind then must not have that info.
                        aircraft.wind_dir = 0
                        aircraft.wind_speed = 0
                        aircraft.norm_wind_dir = 0 #normalize the wind direction to the airplane heading
                        aircraft.gndspeed = 0


                    aircraft.msg_count += 1

                    if aircraft.demoMode:  #if demo mode then add a delay.  Else reading a file is way to fast.
                        time.sleep(.05)
                    else:
                        self.ser.flushInput()  # flush the serial after every message else we see delays
                    return aircraft

                elif dataType == "2" and ord(CRLF[0]) == EOL: #Dynon System message (nav,AP, etc)

                    if aircraft.demoMode:  #if demo mode then add a delay.  Else reading a file is way to fast.
                        time.sleep(.05)
                    else:
                        self.ser.flushInput()  # flush the serial after every message else we see delays
                    return aircraft

                elif dataType == "3" and ord(CRLF[0]) == EOL: #Engine data message

                    if aircraft.demoMode:  #if demo mode then add a delay.  Else reading a file is way to fast.
                        time.sleep(.05)
                    else:
                        self.ser.flushInput()  # flush the serial after every message else we see delays
                    return aircraft
                else:
                    aircraft.msg_unknown += 1 # unknown message found.

            else:
                aircraft.msg_bad += 1 # count this as a bad message
                if aircraft.demoMode:  #if demo mode then add a delay.  Else reading a file is way to fast.
                    time.sleep(.01)
                else:
                    self.ser.flushInput()  # flush the serial after every message else we see delays
                return aircraft
        except serial.serialutil.SerialException:
            print("skyview serial exception")
            aircraft.errorFoundNeedToExit = True
        return aircraft



    #############################################
    ## Function: printTextModeData
    def printTextModeData(self, aircraft):
        hud_text.print_header("Decoded data from Input Module: %s"%(self.name))
        hud_text.print_object(aircraft)
        hud_text.print_DoneWithPage()

# vi: modeline tabstop=8 expandtab shiftwidth=4 softtabstop=4 syntax=python
