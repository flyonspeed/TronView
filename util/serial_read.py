#!/usr/bin/env python
from __future__ import print_function

import time
import serial
import struct
import sys
import os, getopt

version = "0.1"

ser = serial.Serial(
    port="/dev/ttyS0",
    baudrate=115200,
    parity=serial.PARITY_NONE,
    stopbits=serial.STOPBITS_ONE,
    bytesize=serial.EIGHTBITS,
    timeout=1,
)
counter = 0
badmessageheaderCount = 0
goodmessageheaderCount = 0
sinceLastGoodMessage = 0
unkownMsgCount = 0


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
    global badmessageheaderCount, sinceLastGoodMessage, goodmessageheaderCount, unkownMsgCount
    try:
        stx = ord(ser.read(1))
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
                print_xy(3, 74, "Unknown Msg: %d " % (unkownMsgCount))

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
                    unkownMsgCount += 1
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
    global badmessageheaderCount, sinceLastGoodMessage, goodmessageheaderCount, unkownMsgCount
    try:
        x = 0
        while x != 33:  # 33(!) is start of dynon skyview.
            t = ser.read(1)
            sinceLastGoodMessage += 1
            print_xy(3, 0, "SinceGood: %d" % (sinceLastGoodMessage))
            print_xy(3, 24, "Bad msgHead: %d" % (badmessageheaderCount))
            print_xy(3, 49, "Good msgHead: %d " % (goodmessageheaderCount))
            print_xy(3, 74, "Unknown Msg: %d " % (unkownMsgCount))

            if len(t) != 0:
                x = ord(t)

        msg = ser.read(73)
        if len(msg) == 73:
            sinceLastGoodMessage = 0
            msg = (msg[:73]) if len(msg) > 73 else msg
            dataType, DataVer, SysTime, pitch, roll, HeadingMAG, IAS, PresAlt, TurnRate, LatAccel, VertAccel, AOA, VertSpd, OAT, TAS, Baro, DA, WD, WS, Checksum, CRLF = struct.unpack(
                "cc8s4s5s3s4s6s4s3s3s2s4s3s4s3s6s3s2s2s2s", msg
            )
            # dataType,DataVer,SysTime = struct.unpack("cc8s", msg)

            if (CRLF[0]) == 13 or (CRLF[0]) == "\r":
                intCheckSum = int("0x%s" % (Checksum.decode()), 0)
                print_xy(4, 0, msg.decode())
                calcChecksum = 33 + (sum(map(ord, msg[:69].decode())) % 256)
                calcChecksumHex = "0x{:02x}".format(calcChecksum)
                if dataType.decode() == "1":
                    goodmessageheaderCount += 1
                    print_xy(5, 0, bcolors.OKGREEN + "ADHRS(1)" + bcolors.ENDC)
                    print_xy(6, 0, "DataType:   %s" % (dataType.decode()))
                    print_xy(7, 0, "Ver:        %s" % (DataVer.decode()))
                    print_xy(8, 0, "SysTime:    %s" % (SysTime.decode()))
                    print_xy(9, 0, "Pitch:      %s" % (pitch.decode()))
                    print_xy(10, 0, "Roll:       %s" % (roll.decode()))
                    print_xy(11, 0, "HeadMag:    %s" % (HeadingMAG.decode()))
                    print_xy(12, 0, "IAS:        %s" % (IAS.decode()))
                    print_xy(13, 0, "PresAlt:    %s" % (PresAlt.decode()))
                    print_xy(14, 0, "TurnRate:   %s" % (TurnRate.decode()))
                    print_xy(15, 0, "LatAccel:   %s" % (LatAccel.decode()))
                    print_xy(16, 0, "VertAccel:  %s" % (VertAccel.decode()))
                    print_xy(17, 0, "AOA:        %s" % (AOA.decode()))
                    print_xy(18, 0, "VertSpd:    %s" % (VertSpd.decode()))
                    print_xy(19, 0, "OAT:        %s" % (OAT.decode()))
                    print_xy(20, 0, "TAS:        %s" % (TAS.decode()))
                    converted_Baro = (int(Baro) + 2750.0) / 100
                    baro_diff = converted_Baro - 29.921
                    converted_alt = int(int(PresAlt) + ((baro_diff) / 0.00108))
                     #0.00108 of inches of mercury change per foot.
                    print_xy(21, 0, "Baro:       %0.2f  Alt:  %d ft   " % (converted_Baro, converted_alt))
                    print_xy(22, 0, "DensitAlt:  %s" % (DA.decode()))
                    print_xy(23, 0, "WndDir:     %s" % (WD.decode()))
                    print_xy(24, 0, "WndSpd:     %s" % (WS.decode()))
                    print_xy(25, 0, "ChkSum:     0x%s   int:%d " % (Checksum.decode(), intCheckSum))
                    print_xy(26, 0, "CalChkSum:  %s   int:%d " % (calcChecksumHex, calcChecksum))
                    nextByte = ser.read(1)
                    print_xy(27, 0, "endbyte:    %s " % (repr(CRLF[0])))
            else:
                badmessageheaderCount += 1
            ser.flushInput()

        else:
            badmessageheaderCount += 1
            ser.flushInput()
            return
    except serial.serialutil.SerialException:
        print("exception")
  

def readG3XMessage():
    global ser
    global badmessageheaderCount, sinceLastGoodMessage, goodmessageheaderCount, unkownMsgCount
    try:
        x = 0
        while x != 61:  # 61(=) is start of Garmin G3X.
            t = ser.read(1)
            sinceLastGoodMessage += 1
            print_xy(3, 0, "SinceGood: %d" % (sinceLastGoodMessage))
            print_xy(3, 24, "Bad msgHead: %d" % (badmessageheaderCount))
            print_xy(3, 49, "Good msgHead: %d " % (goodmessageheaderCount))
            print_xy(3, 74, "Unknown Msg: %d " % (unkownMsgCount))

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
    print("EFIS 2 Hud Serial monitor tool. Version: %s" % (version))
    print("read_serial.py <options>")
    print(" -m (MGL iEFIS)")
    print(" -s (Dynon Skyview)")
    print(" -g (Garmin G3X)")
    sys.exit()



#
# MAIN LOOP


argv = sys.argv[1:]
readType = "none"
try:
    opts, args = getopt.getopt(argv, "hsmg", ["skyview="])
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

if readType == "none":
    showArgs()

os.system("clear")
print_xy(
    1,
    0,
    bcolors.HEADER
    + "HUD serial data monitor."
    + bcolors.ENDC
    + "  Version: %s" % (version),
)
if readType == "skyview":
    print_xy(2, 0, "Data format: " + bcolors.OKBLUE + "Dynon Skyview" + bcolors.ENDC)
    while 1:
        readSkyviewMessage()
elif readType == "mgl":
    print_xy(2, 0, "Data format: " + bcolors.OKBLUE + "MGL" + bcolors.ENDC)
    while 1:
        readMGLMessage()
elif readType == "g3x":
    print_xy(2, 0, "Data format: " + bcolors.OKBLUE + "Garmin G3X" + bcolors.ENDC)
    while 1:
        readG3XMessage()


