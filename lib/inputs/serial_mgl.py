#!/usr/bin/env python

# Serial input source
# MGL iEFIS
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
        self.textMode_showAir = True
        self.textMode_showNav = True
        self.textMode_showTraffic = True
        self.shouldExit = False
        self.skipReadInput = False
        self.skipTextOutput = False
        self.output_logFile = None
        self.output_logFileName = ""
        self.input_logFileName = ""

    def initInput(self,aircraft):
        Input.initInput( self, aircraft )  # call parent init Input.
        #Input.setLogLinePrefixSuffix(struct.pack('5B', *newFileBytes))
        if aircraft.demoMode:
            # if in demo mode then load example data file.
            # get demo file to read from config.  else default to..
            if not len(aircraft.demoFile):
                defaultTo = "mgl_data1.bin"
                #defaultTo = "mgl_G430_v6_HSI_Nedl_2degsRtt_Vert_2Degs_Up.bin"
                #defaultTo = "mgl_G430_v7_Horz_Vert_Nedl_come to center.bin"
                aircraft.demoFile = hud_utils.readConfig(self.name, "demofile", defaultTo)
            #self.ser = open("lib/inputs/_example_data/%s"%(aircraft.demoFile), "rb")
            self.ser,self.input_logFileName = Input.openLogFile(self,aircraft.demoFile,"rb")
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
        if self.shouldExit == True: aircraft.errorFoundNeedToExit = True
        if aircraft.errorFoundNeedToExit: return aircraft
        if self.skipReadInput == True: return aircraft
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
                Message = 0
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
                            aircraft.slip_skid = Slip 
                            aircraft.msg_count += 1
                            aircraft.msg_last = binascii.hexlify(Message) # save last message.

                    elif msgType == 2:  # GPS Message
                        Message = self.ser.read(36)
                        if len(Message) == 36:
                            Latitude, Longitude, GPSAltitude, AGL, NorthV, EastV, DownV, GS, TrackTrue, Variation, GPS, SatsTracked = struct.unpack(
                                "<iiiiiiiHHhBB", Message
                            )
                            if GS > 0:
                                aircraft.gndspeed = GS * 0.06213712 # convert to mph
                            aircraft.agl = AGL
                            aircraft.gndtrack = int(TrackTrue * 0.1)
                            if (
                                aircraft.mag_head == 0
                            ):  # if no mag heading use ground track
                                aircraft.mag_head = aircraft.gndtrack
                            aircraft.msg_count += 1
                            aircraft.msg_last = binascii.hexlify(Message) # save last message.
                            # if self.logFile != None:
                            #     Input.addToLog(self,Message)

                    elif msgType == 1:  # Primary flight
                        Message = self.ser.read(30)
                        if len(Message) == 30:
                            PAltitude, BAltitude, ASI, TAS, AOA, VSI, Baro, LocalBaro, OAT, Humidity, SystemFlags, Hour, Min, Sec, Day, Month, Year  = struct.unpack(
                                "<iiHHhhHHhBBBBBBBB", Message
                            )
                            if ASI > 0:
                                aircraft.ias = ASI * 0.06213712 #idicated airspeed in 10th of Km/h.  * 0.05399565 to knots. * 0.6213712 to mph
                            if TAS > 0:
                                aircraft.tas = TAS * 0.06213712 # mph
                            # efis_alt = BAltitude
                            aircraft.baro = (
                                LocalBaro * 0.0029529983071445
                            )  # convert from mbar to inches of mercury.
                            aircraft.aoa = AOA
                            aircraft.vsi = VSI
                            aircraft.baro_diff = 29.921 - aircraft.baro
                            aircraft.PALT = PAltitude
                            aircraft.BALT = BAltitude
                            aircraft.alt = int(
                                PAltitude - (aircraft.baro_diff / 0.00108)
                            )  # 0.00108 of inches of mercury change per foot.
                            aircraft.oat = (OAT * 1.8) + 32 # convert from c to f
                            aircraft.sys_time_string = "%d:%d:%d"%(Hour,Min,Sec)

                            aircraft.msg_count += 1
                            aircraft.msg_last = binascii.hexlify(Message) # save last message.
                            # if self.logFile != None:
                            #     Input.addToLog(self,Message)

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
                            # if self.logFile != None:
                            #     Input.addToLog(self,Message)


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
                            # if self.logFile != None:
                            #     Input.addToLog(self,Message)

                    else:
                        aircraft.msg_unknown += 1 #else unknown message.
                        aircraft.nav.msg_last = 0
                    
                    if aircraft.demoMode:  #if demo mode then add a delay.  Else reading a file is way to fast.
                        time.sleep(.01)
                    else:
                        self.ser.flushInput()  # flush the serial after every message else we see delays

                    if self.output_logFile != None and aircraft.nav.msg_last != 0:
                        Input.addToLog(self,self.output_logFile,bytearray([5,2]))
                        Input.addToLog(self,self.output_logFile,MessageHeader)
                        Input.addToLog(self,self.output_logFile,Message)

                    return aircraft

                else: # bad message header found.
                    aircraft.msg_bad += 1

            else:
                aircraft.msg_bad += 1 #bad message found.

                return aircraft
        except serial.serialutil.SerialException:
            print("mgl serial exception")
            aircraft.errorFoundNeedToExit = True
        return aircraft

    # fast forward if reading from a file.
    def fastForward(self,aircraft,bytesToSkip):
            if aircraft.demoMode:
                current = self.ser.tell()
                moveTo = current - bytesToSkip
                try:
                    for _ in range(bytesToSkip):
                        next(self.ser) # have to use next...
                except:
                    # if error then just to start of file
                    self.ser.seek(0)
                #print("fastForward() before="+str(current)+" goto:"+str(moveTo)+" done="+str(self.ser.tell()))

    def fastBackwards(self,aircraft,bytesToSkip):
            if aircraft.demoMode:
                self.skipReadInput = True  # lets pause reading from the file for second while we mess with the file pointer.
                current = self.ser.tell()
                moveTo = current - bytesToSkip
                if(moveTo<0): moveTo = 0
                self.ser.seek(0) # reset back to begining.
                try:
                    for _ in range(moveTo):
                        next(self.ser) # jump to that postion???  not really working right.
                except:
                    # if error then just to start of file
                    self.ser.seek(0)
                #print("fastForward() before="+str(current)+" goto:"+str(moveTo)+" done="+str(self.ser.tell()))
                self.skipReadInput = False

    #############################################
    ## Function: printTextModeData
    def printTextModeData(self, aircraft):
        hud_text.print_header("Decoded data from Input Module: %s (Keys: n = nav data, a = all data)"%(self.name))
        if len(aircraft.demoFile):
            hud_text.print_header("Demofile: %s"%(aircraft.demoFile))

        if self.textMode_showAir==True:
            hud_text.print_object(aircraft)

        if self.textMode_showNav==True:
            hud_text.print_header("Decoded Nav Data")
            hud_text.print_object(aircraft.nav)

        if self.textMode_showTraffic==True:
            hud_text.changePos(1,100)
            hud_text.print_header("Decoded Traffic Data")
            hud_text.print_object(aircraft.traffic)

        hud_text.print_DoneWithPage()


    #############################################
    ## Function: textModeKeyInput
    ## this is only called when in text mode. And is used to changed text mode options.
    def textModeKeyInput(self, key, aircraft):
        if key==ord('n'):
            self.textMode_showNav = True
            self.textMode_showAir = False
            self.textMode_showTraffic = False
            hud_text.print_Clear()
            return 0,0
        elif key==ord('a'):
            self.textMode_showNav = True
            self.textMode_showAir = True
            self.textMode_showTraffic = True
            hud_text.print_Clear()
            return 0,0
        else:
            return 'quit',"%s Input: Key code not supported: %d ... Exiting \r\n"%(self.name,key)


    def startLog(self,aircraft):
        if self.output_logFile == None:
            self.output_logFile,self.output_logFileName = Input.createLogFile(self,".dat",True)
            print("Creating log output: %s\n"%(self.output_logFileName))
        else:
            print("Already logging to: "+self.output_logFileName)

    def stopLog(self,aircraft):
        if self.output_logFile != None:
            Input.closeLogFile(self,self.output_logFile)
            self.output_logFile = None


# vi: modeline tabstop=8 expandtab shiftwidth=4 softtabstop=4 syntax=python
