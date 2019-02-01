#!/usr/bin/env python

# Serial input source
# Garmin G3X
# 01/30/2019 Brian Chesteen, credit to Christopher Jones for developing template for input modules.
from __future__ import print_function

from _input import Input
from lib import hud_utils
import serial
import struct
from lib import hud_text

class serial_g3x(Input):
    def __init__(self):
        self.name = "g3x"
        self.version = 1.0
        self.inputtype = "serial"

    def initInput(self):
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

    #############################################
    ## Function: readMessage
    def readMessage(self, aircraft):
        try:
            x = 0
            while x != 61:  # 61(=) is start of garmin g3x.
                t = self.ser.read(1)
                if len(t) != 0:
                    x = ord(t)
            msg = self.ser.read(58)  
            if len(msg) == 58:
                aircraft.msg_last = msg
                msg = (msg[:58]) if len(msg) > 58 else msg
                SentID, SentVer, UTCHour, UTCMin, UTCSec, UTCSecFrac, Pitch, Roll, Heading, Airspeed, PressAlt, RateofTurn, LatAcc, VertAcc, AOA, VertSpeed, OAT, AltSet, Checksum, CRLF = struct.unpack(
                "cc2s2s2s2s4s5s3s4s6s4s3s3s2s4s3s3s2s2s", msg
                )
                # if ord(CRLF[0]) == 13:
                if SentID == "1" and ord(CRLF[0]) == 13:
                    aircraft.roll = int(Roll) * 0.1
                    aircraft.pitch = int(Pitch) * 0.1
                    aircraft.ias = int(Airspeed) * 0.1
                    aircraft.PALT = int(PressAlt) 
                    aircraft.aoa = int(AOA)
                    aircraft.mag_head = int(Heading)
                    aircraft.baro = (int(AltSet) + 2750.0) / 100
                    aircraft.baro_diff = aircraft.baro - 29.921
                    aircraft.alt = int(
                        int(PressAlt) + (aircraft.baro_diff / 0.00108)
                    )  # 0.00108 of inches of mercury change per foot.
                    aircraft.BALT = aircraft.alt
                    aircraft.vsi = int(VertSpeed) * 10
                    aircraft.tas = ((aircraft.ias * 0.02) * (aircraft.BALT / 1000)) + aircraft.ias
                    aircraft.msg_count += 1

                    self.ser.flushInput()
                    return aircraft
                else
                    aircraft.msg_unkown += 1 # else unkown message.

            else:
                aircraft.msg_bad += 1  # count this as a bad message
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

