#!/usr/bin/env python
          
      
import time
import serial


ser = serial.Serial(  
  port='/dev/ttyS0',
  baudrate = 115200,
  parity=serial.PARITY_NONE,
  stopbits=serial.STOPBITS_ONE,
  bytesize=serial.EIGHTBITS,
  timeout=1
)
counter=0




def readMessage():
  global ser
  try:
    x = 0
    while x != 5:
      t = ser.read(1)
      if len(t) != 0:
        x = ord(t);
    stx = ord(ser.read(1))
    msglength = ord(ser.read(1))
    if stx == 2:
      #print "found message len:",msglength
      msglengthxor = ord(ser.read(1))
      msgtype = ord(ser.read(1))
      msgrate = ord(ser.read(1))
      msgcount = ord(ser.read(1))
      msgversion = ord(ser.read(1))
      if msgtype == 3 : # attitude information
        heading = ord(ser.read(1)) + ord(ser.read(1))
        pitch = ord(ser.read(1)) + ord(ser.read(1))
        print "pitch: ",pitch
    else:
      return
  except serial.serialutil.SerialException:
    print "exception"


while 1:
  readMessage()
  #try:
  #  x = ser.read(1)
  #  if len(x) > 0:
  #    print ord(x)
  #except serial.serialutil.SerialException:
  #  print "exception"
  #
  #print x[0]
