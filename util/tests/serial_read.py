#!/usr/bin/env python
# Expanded Dynon Skyview test   Zap 12/28/2024


import time
import serial
import struct
import sys
import os, getopt
import subprocess, platform

version = "0.2"

ser = None
port = "/dev/ttyS0"  # default serial port
backup_port = "/dev/ttyUSB0"
counter = 0
badmessageheaderCount = 0
goodmessageheaderCount = 0
sinceLastGoodMessage = 0
unknownMsgCount = 0


class bcolors:
    HEADER = "\033[95m"
    OKBLUE = "\033[94m"
    OKGREEN = "\033[92m"
    WARNING = "\033[93m"
    FAIL = "\033[91m"
    ENDC = "\033[0m"
    BOLD = "\033[1m"
    UNDERLINE = "\033[4m"


# MGL data formats to Python.
# Longint (32 bit signed int) = i
# Smallint (16 bit signed int) = h  (signed short)
# Word (16 unsigned int) = H  (unsigned short)

#print at location
def print_xy(x, y, text):
    sys.stdout.write("\x1b7\x1b[%d;%df%s\x1b8" % (x, y, text))
    sys.stdout.flush()


# https://stackoverflow.com/questions/699866/python-int-to-binary#699891
def get_bin(x, n=8):
    """
    Get the binary representation of x.

    Parameters
    ----------
    x : int
    n : int
        Minimum number of digits. If x needs less digits in binary, the rest
        is filled with zeros.

    Returns
    -------
    str
    """
    return format(x, "b").zfill(n)


def read_all(port, chunk_size=200):
    """Read all characters on the serial port and return them."""
    if not port.timeout:
        raise TypeError("Port needs to have a timeout set!")

    read_buffer = b""

    while True:
        # Read in chunks. Each chunk will wait as long as specified by
        # timeout. Increase chunk_size to fail quicker
        byte_chunk = port.read(size=chunk_size)
        read_buffer += byte_chunk
        if not len(byte_chunk) == chunk_size:
            break
    return read_buffer


def readSerial(num):
    global ser
    if ser.inWaiting() > num:
        ser.read(ser.inWaiting())


def readMGLMessage():
    global ser
    global badmessageheaderCount, sinceLastGoodMessage, goodmessageheaderCount, unknownMsgCount
    try:
        stx = int(ser.read(1))
        if stx == 2:
            MessageHeader = ser.read(6)
            if len(MessageHeader) == 6:
                msgLength, msgLengthXOR, msgType, msgRate, msgCount, msgVerion = struct.unpack(
                    "!BBBBBB", MessageHeader
                )
                sinceLastGoodMessage = 0
                goodmessageheaderCount += 1
                print_xy(3, 0, "SinceGood: %d" % (sinceLastGoodMessage))
                print_xy(3, 24, "Bad msgHead: %d" % (badmessageheaderCount))
                print_xy(3, 49, "Good msgHead: %d " % (goodmessageheaderCount))
                print_xy(3, 74, "Unknown Msg: %d " % (unknownMsgCount))

                if msgType == 3:  # attitude information
                    Message = ser.read(25)
                    if len(Message) == 25:
                        # use struct to unpack binary data.  https://docs.python.org/2.7/library/struct.html
                        HeadingMag, PitchAngle, BankAngle, YawAngle, TurnRate, Slip, GForce, LRForce, FRForce, BankRate, PitchRate, YawRate, SensorFlags = struct.unpack(
                            "<HhhhhhhhhhhhB", Message
                        )
                        print_xy(4, 0, bcolors.OKGREEN + "Attitude(3)" + bcolors.ENDC)
                        print_xy(5, 0, "HeadingMAG:%d  " % (HeadingMag * 0.1))
                        print_xy(6, 0, "Pitch:     %d  " % (PitchAngle * 0.1))
                        print_xy(7, 0, "Bank:      %d  " % (BankAngle * 0.1))
                        print_xy(8, 0, "Yaw:       %d  " % (YawAngle * 0.1))
                        print_xy(9, 0, "TurnRate:  %d  " % (TurnRate * 0.1))
                        print_xy(10, 0, "Slip:      %d  " % (Slip))
                        print_xy(11, 0, "GForce:    %d  " % (GForce))
                        print_xy(12, 0, "SensorFlag:%s  " % (get_bin(SensorFlags)))

                elif msgType == 1:  # Primary flight
                    Message = ser.read(18)
                    if len(Message) == 18:
                        PAltitude, BAltitude, ASI, TAS, AOA, VSI, Baro = struct.unpack(
                            "<iiHHhhH", Message
                        )
                        print_xy(4, 21, bcolors.OKGREEN + "Primary flight(1)")
                        print_xy(5, 21, "Pat Alt: %d  " % (PAltitude))
                        print_xy(6, 21, "Bao Alt: %d  " % (BAltitude))
                        print_xy(7, 21, "ASI:     %dkts  " % (ASI * 0.05399565))
                        print_xy(8, 21, "TAS:     %d  " % (TAS ** 0.05399565))
                        print_xy(9, 21, "AOA:     %d  " % (AOA))
                        print_xy(10, 21, "VSI:     %d  " % (VSI))
                        print_xy(11, 21, "Baro:    %d  " % (Baro))

                elif msgType == 6:  # Traffic message
                    Message = ser.read(4)
                    if len(Message) == 4:
                        TrafficMode, NumOfTraffic, NumMsg, MsgNum = struct.unpack(
                            "!BBBB", Message
                        )
                        print_xy(9, 40, bcolors.OKGREEN + "Traffic(6)" + bcolors.ENDC)
                        print_xy(10, 40, "Mode:  %d  " % (TrafficMode))
                        print_xy(11, 40, "Count: %d  " % (NumOfTraffic))
                        print_xy(12, 40, "NumMsg:%d  " % (NumMsg))

                elif msgType == 30:  # Navigation message
                    Message = ser.read(24)
                    if len(Message) == 24:
                        Flags, HSISource, VNAVSource, APMode, Padding, HSINeedleAngle, HSIRoseHeading, HSIDeviation, VerticalDeviation, HeadingBug, AltimeterBug, WPDistance = struct.unpack(
                            "<HBBBBhHhhhii", Message
                        )
                        print_xy(
                            15, 0, bcolors.OKGREEN + "Navigation(30)" + bcolors.ENDC
                        )
                        print_xy(16, 0, "HSISource:  %d  " % (HSISource))
                        print_xy(17, 0, "VNAVSource: %d  " % (VNAVSource))
                        print_xy(18, 0, "HSI >:      %d  " % (HSINeedleAngle))
                        print_xy(19, 0, "HSI Head:   %d  " % (HSIRoseHeading))
                        print_xy(20, 0, "HSI Dev:    %d  " % (HSIDeviation))
                        print_xy(21, 0, "Vert Dev:   %d  " % (VerticalDeviation))
                        print_xy(22, 0, "Head Bug:   %d  " % (HeadingBug))
                        print_xy(23, 0, "Alt Bug:    %d  " % (AltimeterBug))
                        print_xy(24, 0, "WP Dist:    %d  " % (WPDistance))
                        print_xy(25, 0, "Flags:      %s " % (get_bin(Flags)))

                elif msgType == 2:  # GPS Message
                    Message = ser.read(36)
                    if len(Message) == 36:
                        Latitude, Longitude, GPSAltitude, AGL, NorthV, EastV, DownV, GS, TrackTrue, Variation, GPS, SatsTracked = struct.unpack(
                            "<iiiiiiiHHhBB", Message
                        )
                        print_xy(15, 24, bcolors.OKGREEN + "GPS(2)" + bcolors.ENDC)
                        print_xy(16, 24, "Latitude:  %f  " % (Latitude))
                        print_xy(17, 24, "Longitude: %f  " % (Longitude))
                        print_xy(18, 24, "GPSAlt:    %d  " % (GPSAltitude))
                        print_xy(19, 24, "AGL:       %d  " % (AGL))
                        print_xy(
                            20, 24, "GS:        %dkts " % (GS * 0.05399565)
                        )  # convert to knots.
                        print_xy(21, 24, "TrackTrue: %d  " % (TrackTrue))
                        print_xy(22, 24, "Variation: %d  " % (Variation))
                        print_xy(23, 24, "Status:    %s " % (get_bin(GPS)))
                        print_xy(24, 24, "SatsTracke:%d  " % (SatsTracked))

                else:
                    unknownMsgCount += 1
                    print_xy(
                        4,
                        40,
                        bcolors.OKGREEN
                        + "Last unknw msgtype: %d " % (msgType)
                        + bcolors.ENDC,
                    )

        else:
            badmessageheaderCount += 1
            ser.flushInput()
            return
    except serial.serialutil.SerialException:
        print("exception")


def readSkyviewMessage():
    global ser
    global badmessageheaderCount, sinceLastGoodMessage, goodmessageheaderCount, unknownMsgCount
    try:
        x = 0
        while x != 33:  # 33(!) is start of dynon skyview.
            t = ser.read(1)
            sinceLastGoodMessage += 1
            print_xy(2, 0,  "SinceGood: %d" % (sinceLastGoodMessage))
            print_xy(2, 24, "Bad msgHead: %d" % (badmessageheaderCount))
            print_xy(2, 49, "Good msgHead: %d " % (goodmessageheaderCount))
            print_xy(2, 74, "Unknown Msg: %d " % (unknownMsgCount))

            if len(t) != 0:
                x = ord(t)

        dataType = ser.read(1)
        if dataType.decode() == "1":        # ADHARS Data Message
            goodmessageheaderCount += 1
            msg = ser.read(72)
            #skyview_data.write("!1" + msg.decode())
            if len(msg) == 72:
                sinceLastGoodMessage = 0
                msg = (msg[:72]) if len(msg) > 72 else msg
                DataVer, SysTime, pitch, roll, HeadingMAG, IAS, PresAlt, TurnRate, LatAccel, VertAccel, AOA, VertSpd, OAT, TAS, Baro, DA, WD, WS, Checksum, CRLF = struct.unpack(
                    "c8s4s5s3s4s6s4s3s3s2s4s3s4s3s6s3s2s2s2s", msg
                )
            # DataVer,SysTime = struct.unpack("c8s", msg)

                if (CRLF[0]) == 13 or (CRLF[0]) == "\r":
                    intCheckSum = int("0x%s" % (Checksum.decode()), 0)
                    #print_xy(4, 0, msg.decode())
                    calcChecksum = 33 + (sum(map(ord, msg[:68].decode())) % 256)
                    calcChecksumHex = "0x{:02x}".format(calcChecksum)
                    print_xy(3, 0, bcolors.OKGREEN + "  ADHRS (Type:" + (dataType.decode()) + ")" + bcolors.ENDC)
                    #print_xy(4, 0, "DataType:  %s" % (dataType.decode()))
                    print_xy(4, 0, "Ver:       %s" % (DataVer.decode()))
                    print_xy(5, 0, "SysTime:   %s" % (SysTime.decode()))
                    print_xy(6, 0, "Pitch:     %s" % (pitch.decode()))
                    print_xy(7, 0, "Roll:      %s" % (roll.decode()))
                    print_xy(8, 0, "HeadMag:   %s" % (HeadingMAG.decode()))
                    print_xy(9, 0, "IAS:       %s" % (IAS.decode()))
                    print_xy(10, 0, "PresAlt:   %s" % (PresAlt.decode()))
                    print_xy(11, 0, "TurnRate:  %s" % (TurnRate.decode()))
                    print_xy(12, 0, "LatAccel:  %s" % (LatAccel.decode()))
                    print_xy(13, 0, "VertAccel: %s" % (VertAccel.decode()))
                    print_xy(14, 0, "AOA:       %s" % (AOA.decode()))
                    print_xy(15, 0, "VertSpd:   %s" % (VertSpd.decode()))
                    print_xy(16, 0, "OAT:       %s" % (OAT.decode()))
                    print_xy(17, 0, "TAS:       %s" % (TAS.decode()))
                    converted_Baro = (int(Baro) + 2750.0) / 100
                    baro_diff = converted_Baro - 29.921
                    converted_alt = int(int(PresAlt) + ((baro_diff) / 0.00108))
                     #0.00108 of inches of mercury change per foot.
                    print_xy(18, 0, "Baro:      %0.2f Alt:%d""ft" % (converted_Baro, converted_alt))
                    print_xy(19, 0, "DensitAlt: %s" % (DA.decode()))
                    print_xy(20, 0, "WndDir:    %s" % (WD.decode()))
                    print_xy(21, 0, "WndSpd:    %s" % (WS.decode()))
                    print_xy(22, 0, "ChkSum:    0x%s   int:%d " % (Checksum.decode(), intCheckSum))
                    print_xy(23, 0, "CalChkSum: %s   int:%d " % (calcChecksumHex, calcChecksum))
                    nextByte = ser.read(1)
                    print_xy(24, 0, "endbyte:   %s " % (repr(CRLF[0])))
            else:
                badmessageheaderCount += 1
            ser.flushInput()
        elif  dataType.decode() == "2":        # Dynon NAV, AP, etc Data Message:
            goodmessageheaderCount += 1
            msg = ser.read(91)
            #skyview_data.write("!2" + msg.decode())
            if len(msg) == 91:
                sinceLastGoodMessage = 0
                msg = (msg[:91]) if len(msg) > 91 else msg
                (DataVer, SysTime, HBug, AltBug, AirBug, VSBug, Course, CDISrcType, CDISourePort, CDIScale, CDIDeflection, GS, APEng, APRollMode, UnUsed1, APPitch, UnUsed2, APRollF, APRollP, APRollSlip, APPitchF, APPitchP, APPitchSlip, APYawF, APYawP, APYawSlip, TransponderStatus, TransponderReply, TransponderIdent, TransponderCode, UnUsed3, Checksum, CRLF) = struct.unpack(
                    "c8s3s5s4s4s3scc2s3s3sccccc3s5sc3s5sc3s5scccc4s10s2s2s", msg
                )
                if (CRLF[0]) == 13 or (CRLF[0]) == "\r":
                    intCheckSum = int("0x%s" % (Checksum.decode()), 0)
                    #print_xy(4, 0, msg.decode())
                    calcChecksum = 33 + (sum(map(ord, msg[:87].decode())) % 256)
                    calcChecksumHex = "0x{:02x}".format(calcChecksum)
                    print_xy(3, 30, bcolors.OKGREEN + "NAV, AP, Misc (Type:" + (dataType.decode()) + ")" + bcolors.ENDC)
                    #print_xy(4, 30, "DataType:     %s" % (dataType.decode()))
                    print_xy(4, 30, "Ver:          %s" % (DataVer.decode()))
                    print_xy(5, 30, "SysTime:      %s" % (SysTime.decode()))
                    print_xy(6, 30, "Heading Bug:  %s" % (HBug.decode()))
                    print_xy(7, 30, "Alt Bug:      %s" % (AltBug.decode()))
                    print_xy(8, 30, "AS Bug:       %s" % (AirBug.decode()))
                    print_xy(9, 30, "VS Bug:       %s" % (VSBug.decode()))
                    print_xy(10, 30, "Course:       %s" % (Course.decode()))
                    print_xy(11, 30, "CDI Type:     %s" % (CDISrcType.decode()))
                    print_xy(12, 30, "CDI Port:     %s" % (CDISourePort.decode()))
                    print_xy(13, 30, "CDI Scale:    %s" % (CDIScale.decode()))
                    print_xy(14, 30, "CDI Deflect   %s" % (CDIDeflection.decode()))
                    print_xy(15, 30, "VertSpd:      %s" % (GS.decode()))
                    print_xy(16, 30, "AP Engaged:   %s" % (APEng.decode()))
                    print_xy(17, 30, "AP Roll Mode: %s" % (APRollMode.decode()))
                    print_xy(18, 30, "AP Pitch Mode:%s" % (APPitch.decode()))
                    print_xy(19, 30, "AP Roll Slip: %s" % (APRollSlip.decode()))
                    print_xy(20, 30, "APPitchSlip:  %s" % (APPitchSlip.decode()))
                    print_xy(21, 30, "Xpnder Status:%s" % (TransponderStatus.decode()))
                    print_xy(22, 30, "Squawk Code:  %s" % (TransponderCode.decode()))
                    print_xy(23, 30, "ChkSum:       0x%s   int:%d " % (Checksum.decode(), intCheckSum))
                    print_xy(24, 30, "CalChkSum:    %s   int:%d " % (calcChecksumHex, calcChecksum))
                    nextByte = ser.read(1)
                    print_xy(25, 30, "endbyte:      %s " % (repr(CRLF[0])))
        elif  dataType.decode() == "3":        # Engine Data Message
            goodmessageheaderCount += 1
            msg = ser.read(223)
            #skyview_data.write("!3" + msg.decode())
            if len(msg) == 223:
                sinceLastGoodMessage = 0
                msg = (msg[:223]) if len(msg) > 223 else msg
                DataVer, SysTime, OilPress, OilTemp, RPM_L, RPM_R, MAP, FF1, FF2, FP, FL_L, FL_R, Frem, V1, V2, AMPs, Hobbs, Tach, TC1, TC2, TC3, TC4, TC5, TC6, TC7, TC8, TC9, TC10, TC11, TC12, TC13, TC14, GP1, GP2, GP3, GP4, GP5, GP6, GP7, GP8, GP9, GP10, GP11, GP12, GP13, Contacts, Pwr, EGTstate, Checksum, CRLF = struct.unpack(
                    "c8s3s4s4s4s3s3s3s3s3s3s3s3s3s4s5s5s4s4s4s4s4s4s4s4s4s4s4s4s4s4s6s6s6s6s6s6s6s6s6s6s6s6s6s16s3s1s2s2s", msg
                )
                # print("EMS Message !3:", msg)
                if (CRLF[0]) == 13 or (CRLF[0]) == "\r":
                    intCheckSum = int("0x%s" % (Checksum.decode()), 0)
                    #print_xy(4, 0, msg.decode())
                    calcChecksum = 33 + (sum(map(ord, msg[:219].decode())) % 256)
                    calcChecksumHex = "0x{:02x}".format(calcChecksum)
                    print_xy(3, 60, bcolors.OKGREEN + "  Engine (Type:" + (dataType.decode()) + ")" + bcolors.ENDC)
                    #print_xy(4, 60,  "DataType:     %s" % (dataType.decode()))
                    print_xy(4, 60,  "Ver:          %s" % (DataVer.decode()))
                    print_xy(5, 60,  "SysTime:      %s" % (SysTime.decode()))
                    print_xy(6, 60,  "Oil Pressure: %s" % (OilPress.decode()))
                    print_xy(7, 60,  "Oil Temp:     %s" % (OilTemp.decode()))
                    print_xy(8, 60,  "RPM Left:     %s" % (RPM_L.decode()))
                    print_xy(9, 60,  "MAP:          %s" % (MAP.decode()))
                    print_xy(10, 60, "Fuel Flow:    %s" % (FF1.decode()))
                    print_xy(11, 60, "Fuel Pres:    %s" % (FP.decode()))
                    print_xy(12, 60, "Fuel Left:    %s" % (FL_L.decode()))
                    print_xy(13, 60, "Fuel Right:   %s" % (FL_R.decode()))
                    print_xy(14, 60, "Fuel Rem      %s" % (Frem.decode()))
                    print_xy(15, 60, "Voltage-1:    %s" % (V1.decode()))
                    print_xy(16, 60, "Voltage-2:    %s" % (V2.decode()))
                    print_xy(17, 60, "AMPs:         %s" % (AMPs.decode()))
                    print_xy(18, 60, "Hobbs:        %s" % (Hobbs.decode()))
                    print_xy(24, 60, "Eng Power:    %s" % (Pwr.decode()))
                    print_xy(19, 60, "EGT1-4: %s" % (TC12.decode()) + " " + (TC10.decode()) + " " +  (TC8.decode()) + " " +  (TC6.decode()))
                    print_xy(20, 60, "CHT1-4: %s" % (TC11.decode()) + " " + (TC9.decode()) + " "  +  (TC7.decode()) + " " +  (TC5.decode()))
                    print_xy(21, 60, "GP1-4:  %s" % (GP1.decode()) + " " + (GP2.decode()) + " "  +  (GP3.decode()) + " " +  (GP4.decode()))
                    print_xy(22, 60, "GP5-8:  %s" % (GP5.decode()) + " " + (GP6.decode()) + " "  +  (GP7.decode()) + " " +  (GP8.decode()))
                    print_xy(23, 60, "GP9-13: %s" % (GP9.decode()) + " " + (GP10.decode()) + " "  +  (GP11.decode()) + " " +  (GP12.decode()) + " " +  (GP13.decode()))
                    print_xy(25, 60, "ChkSum:      0x%s   int:%d " % (Checksum.decode(), intCheckSum))
                    print_xy(26, 60, "CalChkSum:     %s   int:%d " % (calcChecksumHex, calcChecksum))
                    nextByte = ser.read(1)
                    print_xy(27, 60, "endbyte:      %s " % (repr(CRLF[0])))
        else:
            badmessageheaderCount += 1
            ser.flushInput()
            return
    except serial.serialutil.SerialException:
        print("exception")
        #skyview_data.close()

def readG3XMessage():
    global ser
    global badmessageheaderCount, sinceLastGoodMessage, goodmessageheaderCount, unknownMsgCount
    try:
        x = 0
        while x != 61:  # 61(=) is start of Garmin G3X.
            t = ser.read(1)
            sinceLastGoodMessage += 1
            print_xy(3, 0, "SinceGood: %d" % (sinceLastGoodMessage))
            print_xy(3, 24, "Bad msgHead: %d" % (badmessageheaderCount))
            print_xy(3, 49, "Good msgHead: %d " % (goodmessageheaderCount))
            print_xy(3, 74, "Unknown Msg: %d " % (unknownMsgCount))

            if len(t) != 0:
                x = ord(t)
        SentID = ser.read(1)
            
        if SentID.decode() == "1": #atittude/air data message
            msg = ser.read(57)
            if len(msg) == 57:
                sinceLastGoodMessage = 0
                msg = (msg[:57]) if len(msg) > 57 else msg
                SentVer, UTCHour, UTCMin, UTCSec, UTCSecFrac, Pitch, Roll, Heading, Airspeed, PressAlt, RateofTurn, LatAcc, VertAcc, AOA, VertSpeed, OAT, AltSet, Checksum, CRLF = struct.unpack(
                    "c2s2s2s2s4s5s3s4s6s4s3s3s2s4s3s3s2s2s", msg
                )
                if (CRLF[0]) == 13 or (CRLF[0]) == "\r":
                    intCheckSum = int("0x%s" % (Checksum.decode()), 0)
                    print_xy(4, 0, msg.decode())
                    calcChecksum = 61 + 49 + (sum(map(ord, msg[:53].decode())) % 256)
                    calcChecksumHex = "0x{:02X}".format(calcChecksum)
                    if SentVer.decode() == "1":
                        goodmessageheaderCount += 1
                        print_xy(5, 0, bcolors.OKGREEN + "ATTITUDE/AIR DATA MESSAGE" + bcolors.ENDC)
                        print_xy(6, 0, "Sentence ID:           1")
                        print_xy(7, 0, "Sentence Ver:          %s" % (SentVer.decode()))
                        print_xy(8, 0, "UTC Hour:              %s" % (UTCHour.decode()))
                        print_xy(9, 0, "UTC Minute:            %s" % (UTCMin.decode()))
                        print_xy(10, 0, "UTC Second:            %s" % (UTCSec.decode()))
                        print_xy(11, 0, "UTC Second Fraction:   %s" % (UTCSecFrac.decode()))
                        print_xy(12, 0, "Pitch:                 %s" % (Pitch.decode()))
                        print_xy(13, 0, "Roll:                  %s" % (Roll.decode()))
                        print_xy(14, 0, "Heading:               %s" % (Heading.decode()))
                        print_xy(15, 0, "Airspeed:              %s" % (Airspeed.decode()))
                        print_xy(16, 0, "Pressure Altitude:     %s" % (PressAlt.decode()))
                        print_xy(17, 0, "Rate of Turn:          %s" % (RateofTurn.decode()))
                        print_xy(18, 0, "Lateral Acceleration:  %s" % (LatAcc.decode()))
                        print_xy(19, 0, "Vertical Acceleration: %s" % (VertAcc.decode()))
                        print_xy(20, 0, "AOA:                   %s" % (AOA.decode()))
                        print_xy(21, 0, "Vertical Speed:        %s" % (VertSpeed.decode()))
                        print_xy(22, 0, "Outside Air Temp:      %s" % (OAT.decode()))
                        converted_Baro = (int(AltSet) + 2750.0) / 100
                        baro_diff = converted_Baro - 29.921
                        converted_alt = int(int(PressAlt) + ((baro_diff) / 0.00108))
                        # 0.00108 of inches of mercury change per foot.           
                        print_xy(23, 0, "Altimeter Setting:     %0.2f  Alt: %d ft   " % (converted_Baro, converted_alt))
                        print_xy(24, 0, "CheckSum:              0x%s   int: %d " % (Checksum.decode(), intCheckSum))
                        print_xy(25, 0, "CalChkSum:             %s   int: %d " % (calcChecksumHex, calcChecksum))
                        nextByte = ser.read(1)
                        print_xy(26, 0, "endbyte:               %s " % (repr(CRLF[0])))

        elif SentID.decode() == "7": #GPS AGL data message
            msg = ser.read(16)  
            if len(msg) == 16:
                sinceLastGoodMessage = 0
                msg = (msg[:16]) if len(msg) > 16 else msg
                SentVer, UTCHour, UTCMin, UTCSec, UTCSecFrac, HeightAGL, Checksum, CRLF = struct.unpack(
                "c2s2s2s2s3s2s2s", msg
                )
                if (CRLF[0]) == 13 or (CRLF[0]) == "\r":
                    intCheckSum = int("0x%s" % (Checksum.decode()), 0)
                    print_xy(28, 0, msg.decode())
                    calcChecksum = 61 + 55 + (sum(map(ord, msg[:12].decode())) % 256)
                    calcChecksumHex = "0x{:02X}".format(calcChecksum)
                    if SentVer.decode() == "1":
                        goodmessageheaderCount += 1
                        print_xy(29, 0, bcolors.OKGREEN + "GPS AGL DATA MESSAGE" + bcolors.ENDC)
                        print_xy(30, 0, "Sentence ID:           1")
                        print_xy(31, 0, "Sentence Ver:          %s" % (SentVer.decode()))
                        print_xy(32, 0, "UTC Hour:              %s" % (UTCHour.decode()))
                        print_xy(33, 0, "UTC Minute:            %s" % (UTCMin.decode()))
                        print_xy(34, 0, "UTC Second:            %s" % (UTCSec.decode()))
                        print_xy(35, 0, "UTC Second Fraction:   %s" % (UTCSecFrac.decode()))
                        print_xy(36, 0, "GPS Height AGL:        %s" % (HeightAGL.decode())) 
                        print_xy(37, 0, "CheckSum:              0x%s   int: %d " % (Checksum.decode(), intCheckSum))
                        print_xy(38, 0, "CalChkSum:             %s   int: %d " % (calcChecksumHex, calcChecksum))
                        nextByte = ser.read(1)
                        print_xy(39, 0, "endbyte:               %s " % (repr(CRLF[0])))
        else:
            badmessageheaderCount += 1
            ser.flushInput()
            return
    except serial.serialutil.SerialException:
        print("exception")

def showArgs():
    print("TronView Serial monitor tool. Version: %s" % (version))
    print("read_serial.py <options>")
    print(" -m (MGL iEFIS)")
    print(" -s (Dynon Skyview)")
    print(" -g (Garmin G3X)")
    print(" -l (list available serial ports on RaspberryPi/unix)")
    print(" -i (select input serial port. Default: /dev/ttyS0 )")
    sys.exit()


def list_serial_ports(printthem):

    # List all the Serial COM Ports on Raspberry Pi
    proc = subprocess.Popen(['ls /dev/tty[A-Za-z]*'], shell=True, stdout=subprocess.PIPE)
    com_ports = proc.communicate()[0]
    com_ports_list = str(com_ports).split("\\n") # find serial ports
    rtn = []
    for com_port in com_ports_list:
        if 'ttyS' in com_port:
            if(printthem==True): print("found serial port: "+com_port)
            rtn.append(com_port)
        if 'ttyUSB' in com_port:
            if(printthem==True): print("found USB serial port: "+com_port)
            rtn.append(com_port)
    return rtn


#
# MAIN LOOP


argv = sys.argv[1:]
readType = "none"
try:
    opts, args = getopt.getopt(argv, "hsmgli:", [""])
except getopt.GetoptError:
    showArgs()
for opt, arg in opts:
    if opt == "-h":
        showArgs()
    elif opt == "-s":
        readType = "skyview"
    elif opt == "-m":
        readType = "mgl"
    elif opt == "-g":
        readType = "g3x"    
    if opt == "-l":
        list_serial_ports(True)
        sys.exit()
    if opt == "-i":
        port=arg

if readType == "none":
    showArgs()

if sys.platform.startswith('win'):
    os.system('cls')  # on windows
else:
    os.system("clear")  # on Linux / os X
print_xy(
    1,
    0,
    bcolors.HEADER
    + "Serial data monitor."
    + bcolors.ENDC
    + "  Version: %s" % (version),
)

try:
    ser = serial.Serial(
        port=port,
        baudrate=115200,
        parity=serial.PARITY_NONE,
        stopbits=serial.STOPBITS_ONE,
        bytesize=serial.EIGHTBITS,
        timeout=1,
    )
except:
    print(f"Unable to open primary serial port: {port}")
    print(f"Trying backup port: {backup_port}")
    try:
        ser = serial.Serial(
            port=backup_port,
            baudrate=115200,
            parity=serial.PARITY_NONE,
            stopbits=serial.STOPBITS_ONE,
            bytesize=serial.EIGHTBITS,
            timeout=1,
        )
        print(f"Successfully opened port: {backup_port}")
        port = backup_port
    except:
        print(f"Unable to open port: {backup_port}")
        print("Try passing in port to command line with -i <port>")
        print("Here is a list of ports found:")
        list_serial_ports(True)
        sys.exit()

print_xy(1,0,f"Opened port: {port} @115200 baud (cntrl-c to quit)")

if readType == "skyview":
    print_xy(1, 65, "Data format: " + bcolors.OKBLUE + "Dynon Skyview" + bcolors.ENDC)
    print_xy(2, 0, "                                        ")  # clear line 2
    print_xy(3, 0, "                                        ")  # clear line 3
    #skyview_data = open('skyview_data_x.txt','a')
    while 1:
        readSkyviewMessage()
    #skyview_data.close()
elif readType == "mgl":
    print_xy(2, 0, "Data format: " + bcolors.OKBLUE + "MGL" + bcolors.ENDC)
    while 1:
        readMGLMessage()
elif readType == "g3x":
    print_xy(2, 0, "Data format: " + bcolors.OKBLUE + "Garmin G3X" + bcolors.ENDC)
    while 1:
        readG3XMessage()


