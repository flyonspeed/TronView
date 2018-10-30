#!/usr/bin/env python
          
      
import time
import serial
import struct
import sys
import os

version = "0.1"

ser = serial.Serial(  
  port='/dev/ttyS0',
  baudrate = 115200,
  parity=serial.PARITY_NONE,
  stopbits=serial.STOPBITS_ONE,
  bytesize=serial.EIGHTBITS,
  timeout=1
)
counter=0

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

# MGL data formats to Python.
# Longint (32 bit signed int) = i
# Smallint (16 bit signed int) = h  (signed short)
# Word (16 unsigned int) = H  (unsigned short)

# print at location
def print_xy(x, y, text):
     sys.stdout.write("\x1b7\x1b[%d;%df%s\x1b8" % (x, y, text))
     sys.stdout.flush()

def readMessage():
  global ser
  try:
    x = 0
    while x != 5:
      t = ser.read(1)
      if len(t) != 0:
        x = ord(t);
    stx = ord(ser.read(1))
    
    if stx == 2:
      MessageHeader = ser.read(6)
      msgLength,msgLengthXOR,msgType,msgRate,msgCount,msgVerion = struct.unpack("!BBBBBB", MessageHeader)

      #print "found message len:",msgLength

      if msgType == 3 : # attitude information
        Message = ser.read(25)
        # use struct to unpack binary data.  https://docs.python.org/2.7/library/struct.html
        HeadingMag,PitchAngle,BankAngle,YawAngle,TurnRate,Slip,GForce,LRForce,FRForce,BankRate,PitchRate,YawRate,SensorFlags = struct.unpack("<HhhhhhhhhhhhB", Message)
        print_xy(4 ,0,bcolors.OKGREEN+"Attitude"+bcolors.ENDC)
        print_xy(5 ,0,"Pitch:   %d  " % (PitchAngle))
        print_xy(6 ,0,"Bank:    %d  " % (BankAngle))
        print_xy(7 ,0,"Yaw:     %d  " % (YawAngle))
        print_xy(8 ,0,"TurnRate:%d  " % (TurnRate))
        print_xy(9,0,"Slip:    %d  " % (Slip))
        print_xy(10,0,"GForce:  %d  " % (GForce))
        print_xy(11,0,bin(SensorFlags))

      if msgType == 1 : # Primary flight
        Message = ser.read(18)
        PAltitude,BAltitude,ASI,TAS,AOA,VSI,Baro = struct.unpack("<iiHHhhH", Message)
        print_xy(4 ,20,bcolors.OKGREEN+"Primary flight")
        print_xy(5 ,20,"Pat Alt: %d  " % (PAltitude))
        print_xy(6 ,20,"Bao Alt: %d  " % (BAltitude))
        print_xy(7 ,20,"ASI:     %d  " % (ASI))
        print_xy(8 ,20,"TAS:     %d  " % (TAS))
        print_xy(9 ,20,"AOA:     %d  " % (AOA))
        print_xy(10,20,"VSI:     %d  " % (VSI))
        print_xy(11,20,"Baro:    %d  " % (Baro))

      if msgType == 6 : # Traffic message
        Message = ser.read(18)
        TrafficMode,NumOfTraffic,NumMsg,MsgNum = struct.unpack("!BBBB", Message)
        print_xy(9 ,40,bcolors.OKGREEN+"Traffic"+bcolors.ENDC)
        print_xy(10,40,"Mode:  %d  " % (TrafficMode))
        print_xy(11,40,"Count: %d  " % (NumOfTraffic))
        print_xy(12,40,"NumMsg:%d  " % (NumMsg))

      if msgType == 4 : # Navigation message
        Message = ser.read(24)
        Flags,HSISource,VNAVSource,APMode,Padding,HSINeedleAngle,HSIRoseHeading,HSIDeviation,VerticalDeviation,HeadingBug,AltimeterBug,WPDistance = struct.unpack("<HBBBBhHhhhii", Message)
        print_xy(15,0,bcolors.OKGREEN+"Navigation"+bcolors.ENDC)
        print_xy(16,0,"HSISource:  %d  " % (HSISource))
        print_xy(17,0,"VNAVSource: %d  " % (VNAVSource))
        print_xy(18,0,"HSI >:      %d  " % (HSINeedleAngle))
        print_xy(19,0,"HSI Head:   %d  " % (HSIRoseHeading))
        print_xy(20,0,"HSI Dev:    %d  " % (HSIDeviation))
        print_xy(21,0,"Vert Dev:   %d  " % (VerticalDeviation))
        print_xy(22,0,"Head Bug:   %d  " % (HeadingBug))
        print_xy(23,0,"Alt Bug:    %d  " % (AltimeterBug))
        print_xy(24,0,"WP Dist:    %d  " % (WPDistance))
        print_xy(25,0,bin(Flags))

    else:
      return
  except serial.serialutil.SerialException:
    print "exception"

#
# MAIN LOOP
os.system('clear')
print_xy(1,0,bcolors.HEADER+"HUD serial data monitor."+bcolors.ENDC+"  Version: %s" % (version))
print_xy(2,0,"Data format: "+bcolors.OKBLUE+"MGL"+bcolors.ENDC)
while 1:
  readMessage()

