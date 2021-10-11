#!/usr/bin/env python

# Serial input source
# Garmin G3X
# 01/30/2019 Brian Chesteen, credit to Christopher Jones for developing template for input modules.


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
        self.version = 1.0
        self.inputtype = "serial"

        # Setup moving averages to smooth a bit
        self.readings = []
        self.max_samples = 10
        self.readings1 = []
        self.max_samples1 = 20
        self.EOL = 10

    def initInput(self, aircraft):
        Input.initInput(self, aircraft)  # call parent init Input.

        if aircraft.demoMode:
            # if in demo mode then load example data file.
            self.ser = open("lib/inputs/_example_data/garmin_g3x_data1.txt", "r")
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


    # close this input source
    def closeInput(self, aircraft):
        if aircraft.demoMode:
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
                        aircraft.msg_last = msg
                        if len(msg) == 56:
                            msg = (msg[:56]) if len(msg) > 56 else msg
                            UTCYear, UTCMonth, UTCDay, UTCHour, UTCMin, UTCSec, LatHemi, LatDeg, LatMin, LonHemi, LonDeg, LonMin, PosStat, HPE, GPSAlt, EWVelDir, EWVelmag, NSVelDir, NSVelmag, VVelDir, VVelmag, CRLF = struct.unpack(
                                "2s2s2s2s2s2sc2s5sc3s5sc3s6sc4sc4sc4s2s", str.encode(msg)
                            )
                            if CRLF[0] == self.EOL:
                                aircraft.msg_count += 1
                                aircraft.sys_time_string = "%d:%d:%d"%(int(UTCHour),int(UTCMin),int(UTCSec))
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
                                aircraft.wind_speed, aircraft.wind_dir, aircraft.norm_wind_dir = _utils.windSpdDir(
                                    aircraft.tas * 0.8689758, # back to knots.
                                    aircraft.gndspeed * 0.8689758, # convert back to knots
                                    aircraft.gndtrack,
                                    aircraft.mag_head,
                                    aircraft.mag_decl,
                                )

                            else:
                                aircraft.msg_bad += 1

                else:
                    if (
                        aircraft.demoMode
                    ):  # if no bytes read and in demo mode.  then reset the file pointer to the start of the file.
                        self.ser.seek(0)
                    return aircraft

            SentID = self.ser.read(1)

            if SentID == "1":  # atittude/air data message
                msg = self.ser.read(57)
                aircraft.msg_last = msg
                if len(msg) == 57:
                    msg = (msg[:57]) if len(msg) > 57 else msg
                    SentVer, UTCHour, UTCMin, UTCSec, UTCSecFrac, Pitch, Roll, Heading, Airspeed, PressAlt, RateofTurn, LatAcc, VertAcc, AOA, VertSpeed, OAT, AltSet, Checksum, CRLF = struct.unpack(
                        "c2s2s2s2s4s5s3s4s6s4s3s3s2s4s3s3s2s2s", str.encode(msg)
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
                        aircraft.DA = None  # TODO
                        aircraft.alt = int(
                            int(PressAlt) + (aircraft.baro_diff / 0.00108)
                        )  # 0.00108 of inches of mercury change per foot.
                        aircraft.BALT = aircraft.alt
                        aircraft.vsi = int(VertSpeed) * 10 # vertical speed in fpm
                        aircraft.tas = _utils.ias2tas(
                            int(Airspeed)*0.1, int(OAT), aircraft.PALT
                        ) * 1.15078 # convert back to mph
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
                        if (
                            aircraft.demoMode
                        ):  # if demo mode then add a delay.  Else reading a file is way to fast.
                            time.sleep(0.08)

                    else:
                        aircraft.msg_bad += 1

                else:
                    aircraft.msg_bad += 1

            elif int(SentID) == 7:  # GPS AGL data message
                msg = self.ser.read(16)
                aircraft.msg_last = msg
                if len(msg) == 16:
                    msg = (msg[:16]) if len(msg) > 16 else msg
                    SentVer, UTCHour, UTCMin, UTCSec, UTCSecFrac, HeightAGL, Checksum, CRLF = struct.unpack(
                        "c2s2s2s2s3s2s2s", str.encode(msg)
                    )
                    if int(SentVer) == 1 and CRLF[0] == self.EOL:
                        aircraft.agl = int(HeightAGL) * 100
                        aircraft.msg_count += 1
                    else:
                        aircraft.msg_bad += 1

                else:
                    aircraft.msg_bad += 1

            else:
                aircraft.msg_unknown += 1  # else unknown message.
                if aircraft.demoMode:
                    time.sleep(0.01)
                # else:
                #    self.ser.flushInput()  # flush the serial after every message else we see delays
                return aircraft

        except serial.serialutil.SerialException:
            print("G3X serial exception")
            aircraft.errorFoundNeedToExit = True

        return aircraft




# vi: modeline tabstop=8 expandtab shiftwidth=4 softtabstop=4 syntax=python
