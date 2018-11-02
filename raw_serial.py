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

# print at location
def print_xy(x, y, text):
     sys.stdout.write("\x1b7\x1b[%d;%df%s\x1b8" % (x, y, text))
     sys.stdout.flush()


def readMessage():
  global ser
  try:
      t = ser.read(1)
      x = ord(t)
      print "\t",x,

  except serial.serialutil.SerialException:
    print "exception"


os.system('clear')
while 1:
  readMessage()

