#!/usr/bin/env python

#######################################################################################################################################
#######################################################################################################################################
# hud.py
#
# Python hud script for taking in efis data and displaying it in a custom HUD style format.
# Have Fun.
#
# 1/23/2019 Refactor to make pretty.  Christopher Jones
#
#


import math, os, sys, random
import argparse, pygame
import time
import serial
import struct
import threading, getopt
import ConfigParser
import importlib
from lib import hud_graphics
from lib import hud_utils

#############################################
## Class: DataSource
class DataSource(object):
    def __init__(self,datatype):
        if datatype == "skyview":
            self.type = "skyview"
        elif datatype == "mgl":
            self.type = "mgl"
        # load some default data from config.
        self.data_format = hud_utils.readConfig("DataInput","format","none")
        self.data_port   = hud_utils.readConfig("DataInput","port","/dev/ttyS0")
        self.data_baudrate   = hud_utils.readConfigInt("DataInput","baudrate",115200)


#############################################
## Class: Aircraft
class Aircraft(object):
    def __init__(self):
        self.pitch = 0.0
        self.roll = 0.0
        self.ias = 0
        self.tas = 0
        self.alt = 0
        self.agl = 0
        self.PALT = 0
        self.BALT = 0
        self.aoa = 0
        self.mag_head = 0
        self.gndtrack = 0
        self.baro = 0
        self.baro_diff = 0
        self.vsi = 0
        self.gndspeed = 0

        self.msg_count = 0


#############################################
## Function: readMGLMessage
def readMGLMessage():
  global ser, done
  global aircraft
  try:
    x = 0
    while x != 5:
      t = ser.read(1)
      if len(t) != 0:
        x = ord(t);
    stx = ord(ser.read(1))
    
    if stx == 2:
      MessageHeader = ser.read(6)
      if(len(MessageHeader) == 6):
        msgLength,msgLengthXOR,msgType,msgRate,msgCount,msgVerion = struct.unpack("!BBBBBB", MessageHeader)

        if msgType == 3 : # attitude information
            Message = ser.read(25)
            if(len(Message) == 25):
                # use struct to unpack binary data.  https://docs.python.org/2.7/library/struct.html
                HeadingMag,PitchAngle,BankAngle,YawAngle,TurnRate,Slip,GForce,LRForce,FRForce,BankRate,PitchRate,YawRate,SensorFlags = struct.unpack("<HhhhhhhhhhhhB", Message)
                aircraft.pitch = PitchAngle * 0.1 # 
                aircraft.roll = BankAngle * 0.1 # 
                if HeadingMag != 0:
                    aircraft.mag_head = HeadingMag * 0.1
                aircraft.msg_count +=1

        elif msgType == 2 : # GPS Message
          Message = ser.read(36)
          if len(Message) == 36:
            Latitude,Longitude,GPSAltitude,AGL,NorthV,EastV,DownV,GS,TrackTrue,Variation,GPS,SatsTracked = struct.unpack("<iiiiiiiHHhBB", Message)
            if GS>0:
                    aircraft.gndspeed = GS * 0.05399565
            aircraft.agl = AGL
            aircraft.gndtrack = int(TrackTrue * 0.1)
            if aircraft.mag_head == 0:  # if no mag heading use ground track
                aircraft.mag_head = aircraft.gndtrack  
            aircraft.msg_count +=1

        if msgType == 1 : # Primary flight
            Message = ser.read(20)
            if(len(Message) == 20):
                PAltitude,BAltitude,ASI,TAS,AOA,VSI,Baro,LocalBaro = struct.unpack("<iiHHhhHH", Message)
                if ASI>0:
                    aircraft.ias = ASI * 0.05399565
                if TAS>0:
                    aircraft.tas = TAS * 0.05399565
                #efis_alt = BAltitude
                aircraft.baro = LocalBaro * 0.0029529983071445 # convert from mbar to inches of mercury.
                aircraft.aoa = AOA
                aircraft.baro_diff = 29.921 - aircraft.baro
                aircraft.PALT = PAltitude
                aircraft.BALT = BAltitude
                aircraft.alt = int(PAltitude - (aircraft.baro_diff / 0.00108)) # 0.00108 of inches of mercury change per foot.
                aircraft.vsi = VSI
                aircraft.msg_count +=1

        if msgType == 6 : # Traffic message
            Message = ser.read(4)
            if(len(Message) == 4):
                TrafficMode,NumOfTraffic,NumMsg,MsgNum = struct.unpack("!BBBB", Message)
                aircraft.msg_count +=1

        if msgType == 4 : # Navigation message
            Message = ser.read(24)
            if(len(Message) == 24):
                Flags,HSISource,VNAVSource,APMode,Padding,HSINeedleAngle,HSIRoseHeading,HSIDeviation,VerticalDeviation,HeadingBug,AltimeterBug,WPDistance = struct.unpack("<HBBBBhHhhhii", Message)
                aircraft.msg_count +=1

        ser.flushInput()
    else:
      return
  except serial.serialutil.SerialException:
    print "serial exception"
    done = True;

#############################################
## Function: readSkyviewMessage
def readSkyviewMessage():
  global ser, done
  global aircraft
  try:
    x = 0
    while x != 33:  # 33(!) is start of dynon skyview.
      t = ser.read(1)
      if len(t) != 0:
        x = ord(t)
    msg = ser.read(73)  #91 ?
    if len(msg) == 73:
      msg = (msg[:73]) if len(msg) > 73 else msg
      dataType,DataVer,SysTime,pitch,roll,HeadingMAG,IAS,PresAlt,TurnRate,LatAccel,VertAccel,AOA,VertSpd,OAT,TAS,Baro,DA,WD,WS,Checksum,CRLF = struct.unpack("cc8s4s5s3s4s6s4s3s3s2s4s3s4s3s6s3s2s2s2s", msg)
      #if ord(CRLF[0]) == 13:
      if dataType == '1' and ord(CRLF[0]) == 13:
            aircraft.roll = int(roll) * 0.1
            aircraft.pitch = int(pitch) * 0.1
            aircraft.ias = int(IAS) * 0.1
            
            aircraft.aoa = int(AOA)
            aircraft.mag_head = int(HeadingMAG)
            aircraft.baro = (int(Baro) + 27.5) / 10
            aircraft.baro_diff = 29.921 - aircraft.baro
            aircraft.alt = int(int(PresAlt) + (aircraft.baro_diff / 0.00108)) # 0.00108 of inches of mercury change per foot.
            aircraft.vsi = int(VertSpd) * 10
            aircraft.msg_count +=1

            ser.flushInput()

    else:
      ser.flushInput()
      return
  except serial.serialutil.SerialException:
    print "serial exception"
    done = True;

#############################################
## Function: main
## Main loop.  read global var data of efis data and display graphicaly
def main():
    global done, aircraft
    # init common things.
    maxframerate = hud_utils.readConfigInt('HUD','maxframerate',15)
    pygamescreen, screen_size = hud_graphics.initDisplay(0)
    width, height = screen_size
    pygame.mouse.set_visible(False) # hide the mouse
    CurrentScreen.initDisplay(pygamescreen,width,height) # tell the screen we are about to start.
    clock = pygame.time.Clock()

    # MAIN loop
    while not done:
        clock.tick(maxframerate)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                thread1.stop()
                done = True
            # KEY MAPPINGS
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_q:
                    done = True
                else:
                    CurrentScreen.processEvent(event) # send this key command to the hud screen object

        # main draw loop.. clear then draw frame from current screen object.
        CurrentScreen.clearScreen()
        CurrentScreen.draw(aircraft) # draw method for current screen object


    # close down pygame. and exit.
    pygame.quit()
    pygame.display.quit()
    os.system('killall python')

#############################################
## Class: myThreadSerialReader
## Read serial input data on seperate thread.
class myThreadSerialReader (threading.Thread):
   def __init__(self):
      threading.Thread.__init__(self)
   def run(self):
        global done
        if efis_data_format == 'skyview':
          while 1 and done==False:
            readSkyviewMessage()
        elif efis_data_format == 'mgl':
          while 1 and done==False:
            readMGLMessage()
        else:
            done = True
            print "Unkown efis_data_format: ",efis_data_format
        pygame.display.quit()
        pygame.quit()
        #sys.stdout.flush()
        #sys.stderr.flush()
        sys.exit()

#############################################
#############################################
# Hud start code.
#
#

# redirct output to output.log
#sys.stdout = open('output.log', 'w')
#sys.stderr = open('output_error.log', 'w')


# load hud.cfg file if it exists.
configParser = ConfigParser.RawConfigParser()   
configParser.read("hud.cfg")
aircraft = Aircraft()
done = False
ScreenNameToLoad = hud_utils.readConfig("Hud","screen","DefaultScreen") #default screen to load
# load some default data from config.
efis_data_format = hud_utils.readConfig("DataInput","format","none")
efis_data_port   = hud_utils.readConfig("DataInput","port","/dev/ttyS0")
efis_data_baudrate   = hud_utils.readConfigInt("DataInput","baudrate",115200)

# open serial connection.
ser = serial.Serial(  
  port=efis_data_port,
  baudrate = efis_data_baudrate,
  parity=serial.PARITY_NONE,
  stopbits=serial.STOPBITS_ONE,
  bytesize=serial.EIGHTBITS,
  timeout=1
)

# check args passed in.
if __name__ == '__main__':
    argv = sys.argv[1:]
    #print 'ARGV      :', sys.argv[2:]
    try:
      opts, args = getopt.getopt(sys.argv[1:],'h:s:d:z', ['help=', 'screen=','dataformat=','zdummy='])
    except getopt.GetoptError:
      hud_utils.showArgs(efis_data_format)
    for opt, arg in opts:
      #print arg
      if opt in ('-h', '--help'):
        hud_utils.showArgs(efis_data_format)
      elif opt in ('-d'):
        efis_data_format = arg
      if opt == '-s' :
        ScreenNameToLoad = arg
    if efis_data_format == 'none': hud_utils.showArgs(efis_data_format)

    print "input data format: ",efis_data_format
    if hud_utils.doesEfisScreenExist(ScreenNameToLoad) == False:
        print "Screen module not found: ",ScreenNameToLoad
        hud_utils.listEfisScreens()
        sys.exit()
    print "loading screen module: ",ScreenNameToLoad
    module = ".%s"%(ScreenNameToLoad)
    mod = importlib.import_module(module,"lib.screens") #dynamically load screen class
    class_ = getattr(mod, ScreenNameToLoad)
    CurrentScreen = class_()

    thread1 = myThreadSerialReader() # start read serial data thread
    thread1.start()
   
    sys.exit(main()) # start main loop

# vi: modeline tabstop=8 expandtab shiftwidth=4 softtabstop=4 syntax=python
