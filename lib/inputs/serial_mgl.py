#!/usr/bin/env python

# Serial input source
# Skyview
# 1/23/2019 Christopher Jones

from ._input import Input
from lib import hud_utils
import serial
import struct
from lib import hud_text
import binascii
import time

class serial_mgl(Input):
    def __init__(self):
        self.name = "mgl"
        self.version = 1.0
        self.inputtype = "serial"

    def initInput(self,aircraft):
        Input.initInput( self, aircraft )  # call parent init Input.

        if aircraft.demoMode:
            # if in demo mode then load example data file.
            # get demo file to read from config.  else default to..
            if not len(aircraft.demoFile):
                defaultTo = "mgl_data1.bin"
                #defaultTo = "mgl_G430_v6_HSI_Nedl_2degsRtt_Vert_2Degs_Up.bin"
                #defaultTo = "mgl_G430_v7_Horz_Vert_Nedl_come to center.bin"
                aircraft.demoFile = hud_utils.readConfig(self.name, "demofile", defaultTo)
            self.ser = open("lib/inputs/_example_data/%s"%(aircraft.demoFile), "rb")
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
            while x != 5:
                t = self.ser.read(1)
                if len(t) != 0:
                    x = ord(t)
                else:
                    if aircraft.demoMode:  # if no bytes read and in demo mode.  then reset the file pointer to the start of the file.
                        self.ser.seek(0)
                    return aircraft
            stx = ord(self.ser.read(1))

            if stx == 2:
                MessageHeader = self.ser.read(6)
                Message = ""
                if len(MessageHeader) == 6:
                    msgLength, msgLengthXOR, msgType, msgRate, msgCount, msgVerion = struct.unpack(
                        "!BBBBBB", MessageHeader
                    )

                    if msgType == 3:  # attitude information
                        Message = self.ser.read(25)
                        if len(Message) == 25:
                            # use struct to unpack binary data.  https://docs.python.org/2.7/library/struct.html
                            HeadingMag, PitchAngle, BankAngle, YawAngle, TurnRate, Slip, GForce, LRForce, FRForce, BankRate, PitchRate, YawRate, SensorFlags = struct.unpack(
                                "<HhhhhhhhhhhhB", Message
                            )
                            aircraft.pitch = PitchAngle * 0.1  #
                            aircraft.roll = BankAngle * 0.1  #
                            if HeadingMag != 0:
                                aircraft.mag_head = HeadingMag * 0.1
                            aircraft.msg_count += 1
                            aircraft.msg_last = binascii.hexlify(Message) # save last message.

                    elif msgType == 2:  # GPS Message
                        Message = self.ser.read(36)
                        if len(Message) == 36:
                            Latitude, Longitude, GPSAltitude, AGL, NorthV, EastV, DownV, GS, TrackTrue, Variation, GPS, SatsTracked = struct.unpack(
                                "<iiiiiiiHHhBB", Message
                            )
                            if GS > 0:
                                aircraft.gndspeed = GS * 0.05399565
                            aircraft.agl = AGL
                            aircraft.gndtrack = int(TrackTrue * 0.1)
                            if (
                                aircraft.mag_head == 0
                            ):  # if no mag heading use ground track
                                aircraft.mag_head = aircraft.gndtrack
                            aircraft.msg_count += 1
                            aircraft.msg_last = binascii.hexlify(Message) # save last message.

                    elif msgType == 1:  # Primary flight
                        Message = self.ser.read(20)
                        if len(Message) == 20:
                            PAltitude, BAltitude, ASI, TAS, AOA, VSI, Baro, LocalBaro = struct.unpack(
                                "<iiHHhhHH", Message
                            )
                            if ASI > 0:
                                aircraft.ias = ASI * 0.05399565
                            if TAS > 0:
                                aircraft.tas = TAS * 0.05399565
                            # efis_alt = BAltitude
                            aircraft.baro = (
                                LocalBaro * 0.0029529983071445
                            )  # convert from mbar to inches of mercury.
                            aircraft.aoa = AOA
                            aircraft.baro_diff = 29.921 - aircraft.baro
                            aircraft.PALT = PAltitude
                            aircraft.BALT = BAltitude
                            aircraft.alt = int(
                                PAltitude - (aircraft.baro_diff / 0.00108)
                            )  # 0.00108 of inches of mercury change per foot.
                            aircraft.vsi = VSI
                            aircraft.msg_count += 1
                            aircraft.msg_last = binascii.hexlify(Message) # save last message.

                    elif msgType == 6:  # Traffic message
                        Message = self.ser.read(4)
                        if len(Message) == 4:
                            TrafficMode, NumOfTraffic, NumMsg, MsgNum = struct.unpack(
                                "!BBBB", Message
                            )
                            aircraft.traffic.TrafficMode = TrafficMode
                            aircraft.traffic.TrafficCount = NumOfTraffic
                            aircraft.traffic.NumMsg = NumMsg
                            aircraft.traffic.MsgNum = ThisMsgNum

                            aircraft.traffic.msg_count += 1
                            aircraft.traffic.msg_last = binascii.hexlify(Message) # save last message.


                    elif msgType == 30:  # Navigation message
                        Message = self.ser.read(50)
                        if len(Message) == 50:
                            Flags, HSISource, VNAVSource, APMode, Padding, HSINeedleAngle, HSIRoseHeading, HSIDev, VDev, HeadBug, AltBug, WPDist, WPLat,WPLon,WPTrack,vor1r,vor2r,dme1,dme2,ILSDev,GSDev,GLSHoriz,GLSVert = struct.unpack(
                                "<HBBBBhHhhhiiiihhhHHhhhh", Message
                            )
                            aircraft.nav.NavStatus = hud_utils.get_bin(Flags)
                            aircraft.nav.HSISource = HSISource
                            aircraft.nav.VNAVSource = VNAVSource
                            aircraft.nav.AP = APMode
                            aircraft.nav.HSINeedle = HSINeedleAngle
                            aircraft.nav.HSIRoseHeading = HSIRoseHeading
                            aircraft.nav.HSIHorzDev = HSIDev
                            aircraft.nav.HSIVertDev = VDev

                            aircraft.nav.HeadBug = HeadBug
                            aircraft.nav.AltBug = AltBug

                            aircraft.nav.WPDist = WPDist
                            aircraft.nav.WPTrack = WPTrack

                            aircraft.nav.ILSDev = ILSDev
                            aircraft.nav.GSDev = GSDev
                            aircraft.nav.GLSHoriz = GLSHoriz
                            aircraft.nav.GLSVert = GLSVert

                            aircraft.nav.msg_count += 1
                            aircraft.nav.msg_last = binascii.hexlify(Message) # save nav message.

                    else:
                        aircraft.msg_unknown += 1 #else unknown message.
                    
                    if aircraft.demoMode:  #if demo mode then add a delay.  Else reading a file is way to fast.
                        time.sleep(.01)
                    else:
                        self.ser.flushInput()  # flush the serial after every message else we see delays
                    return aircraft

                else: # bad message header found.
                    aircraft.msg_bad += 1

            else:
                aircraft.msg_bad += 1 #bad message found.

                return aircraft
        except serial.serialutil.SerialException:
            print("serial exception")
            aircraft.errorFoundNeedToExit = True
        return aircraft


    #############################################
    ## Function: printTextModeData
    def printTextModeData(self, aircraft):
        hud_text.print_header("Decoded data from Input Module: %s"%(self.name))
        if len(aircraft.demoFile):
            hud_text.print_header("Demofile: %s"%(aircraft.demoFile))

        hud_text.print_object(aircraft)

        hud_text.print_header("Decoded Nav Data")
        hud_text.print_object(aircraft.nav)

        hud_text.changePos(1,100)
        hud_text.print_header("Decoded Traffic Data")
        hud_text.print_object(aircraft.traffic)

        hud_text.print_DoneWithPage()

# vi: modeline tabstop=8 expandtab shiftwidth=4 softtabstop=4 syntax=python
