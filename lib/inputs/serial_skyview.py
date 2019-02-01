#!/usr/bin/env python

# Serial input source
# Skyview
# 1/23/2019 Christopher Jones
from __future__ import print_function
from _input import Input
from lib import hud_utils
import serial
import struct
from lib import hud_text

class serial_skyview(Input):
    def __init__(self):
        self.name = "skyview"
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
            while x != 33:  # 33(!) is start of dynon skyview.
                t = self.ser.read(1)
                if len(t) != 0:
                    x = ord(t)
            msg = self.ser.read(73)  # 91 ?
            if len(msg) == 73:
                msg = (msg[:73]) if len(msg) > 73 else msg
                aircraft.msg_last = msg
                dataType, DataVer, SysTime, pitch, roll, HeadingMAG, IAS, PresAlt, TurnRate, LatAccel, VertAccel, AOA, VertSpd, OAT, TAS, Baro, DA, WD, WS, Checksum, CRLF = struct.unpack(
                    "cc8s4s5s3s4s6s4s3s3s2s4s3s4s3s6s3s2s2s2s", msg
                )
                # if ord(CRLF[0]) == 13:
                if dataType == "1" and ord(CRLF[0]) == 13:
                    aircraft.roll = int(roll) * 0.1
                    aircraft.pitch = int(pitch) * 0.1
                    aircraft.ias = int(IAS) * 0.1

                    aircraft.aoa = int(AOA)
                    aircraft.mag_head = int(HeadingMAG)
                    aircraft.baro = (int(Baro) + 2750.0) / 100
                    aircraft.baro_diff = aircraft.baro - 29.921
                    aircraft.alt = int(
                        int(PresAlt) + (aircraft.baro_diff / 0.00108)
                    )  # 0.00108 of inches of mercury change per foot.
                    aircraft.vsi = int(VertSpd) * 10
                    aircraft.msg_count += 1

                    self.ser.flushInput()
                    return aircraft
                else:
                    aircraft.msg_unkown += 1 # unkown message found.

            else:
                aircraft.msg_bad += 1 # count this as a bad message
                self.ser.flushInput()
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
