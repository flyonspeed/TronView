#!/usr/bin/env python

# Serial input source
# MGL iEFIS
# 1/23/2019 Christopher Jones

from ._input import Input
from lib import hud_utils
from . import _utils
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
        self.textMode_showEngine = True
        self.textMode_showFuel = True
        self.textMode_showRaw = False
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
                        Message = self.ser.read(32)
                        if len(Message) == 32:
                            # use struct to unpack binary data.  https://docs.python.org/2.7/library/struct.html
                            HeadingMag, PitchAngle, BankAngle, YawAngle, TurnRate, Slip, GForce, LRForce, FRForce, BankRate, PitchRate, YawRate, SensorFlags, Padding1, Padding2, Padding3, Checksum = struct.unpack(
                                "<HhhhhhhhhhhhBBBBi", Message
                            )
                            aircraft.pitch = PitchAngle * 0.1  #
                            aircraft.roll = BankAngle * 0.1  #
                            if HeadingMag != 0:
                                aircraft.mag_head = HeadingMag * 0.1
                            aircraft.slip_skid = Slip * .1
                            aircraft.vert_G = GForce * 0.01
                            aircraft.msg_count += 1
                            if(self.textMode_showRaw==True): aircraft.msg_last = binascii.hexlify(Message) # save last message.
                            else: aircraft.msg_last = None

                    elif msgType == 2:  # GPS Message
                        Message = self.ser.read(48)
                        if len(Message) == 48:
                            Latitude, Longitude, GPSAltitude, AGL, NorthV, EastV, DownV, GS, TrackTrue, Variation, GPS, SatsTracked, SatsVisible, HorizontalAccuracy, VerticalAccuracy, GPScapability, RAIMStatus, RAIMherror, RAIMverror, padding, Checksum = struct.unpack(
                                "<iiiiiiiHHhBBBBBBBBBBi", Message
                            )
                            if GS > 0:
                                aircraft.gndspeed = GS * 0.06213712 # convert to mph
                            # aircraft.agl = AGL
                            aircraft.gndtrack = int(TrackTrue * 0.1)
                            aircraft.mag_decl = Variation * 0.1 # Magnetic variation 10th/deg West = Neg
                            if (
                                aircraft.mag_head == 0
                            ):  # if no mag heading use ground track
                                aircraft.mag_head = aircraft.gndtrack
                            aircraft.msg_count += 1
                            if(self.textMode_showRaw==True): aircraft.msg_last = binascii.hexlify(Message) # save last message.
                            else: aircraft.msg_last = None

                    elif msgType == 1:  # Primary flight
                        Message = self.ser.read(36)
                        if len(Message) == 36:
                            PAltitude, BAltitude, ASI, TAS, AOA, VSI, Baro, LocalBaro, OAT, Humidity, SystemFlags, Hour, Min, Sec, Day, Month, Year,FTHour, FTMin,Checksum  = struct.unpack(
                                "<iiHHhhHHhBBBBBBBBBBi", Message
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
                            if(self.textMode_showRaw==True): aircraft.msg_last = binascii.hexlify(Message) # save last message.
                            else: aircraft.msg_last = None


                            aircraft.wind_speed, aircraft.wind_dir, aircraft.norm_wind_dir = _utils.windSpdDir(
                            aircraft.tas * 0.8689758, # back to knots.
                            aircraft.gndspeed * 0.8689758, # convert back to knots
                            aircraft.gndtrack,
                            aircraft.mag_head,
                            aircraft.mag_decl,
                            )


                    elif msgType == 6:  # Traffic message
                        Message = self.ser.read(msgLength)+6
                        if len(Message) == 4:
                            TrafficMode, NumOfTraffic, NumMsg, MsgNum = struct.unpack(
                                "!BBBB", Message
                            )
                            aircraft.traffic.TrafficMode = TrafficMode
                            aircraft.traffic.TrafficCount = NumOfTraffic
                            aircraft.traffic.NumMsg = NumMsg
                            aircraft.traffic.MsgNum = ThisMsgNum

                            aircraft.traffic.msg_count += 1
                            if(self.textMode_showRaw==True): aircraft.traffic.msg_last = binascii.hexlify(Message) # save last message.
                            else: aircraft.traffic.msg_last = None


                    elif msgType == 30:  # Navigation message
                        Message = self.ser.read(56)
                        if len(Message) == 56:
                            # H     B            B         B        B       h=small int     H = Word        h       h     h       i=long  i       i     i     h=small h     h 
                            Flags, HSISource, VNAVSource, APMode, Padding, HSINeedleAngle, HSIRoseHeading, HSIDev, VDev, HeadBug, AltBug, WPDist, WPLat,WPLon,WPTrack,vor1r,vor2r,dme1,dme2,ILSDev,GSDev,GLSHoriz,GLSVert,Padding,Checksum = struct.unpack(
                                "<HBBBBhHhhhiiiihhhHHhhhhHi", Message
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
                            if(self.textMode_showRaw==True): aircraft.nav.msg_last = binascii.hexlify(Message) # save last message.
                            else: aircraft.nav.msg_last = None

                    elif msgType == 4:  # Various input states and signals
                        Message = self.ser.read(msgLength+6)
                        # todo... read message

                    elif msgType == 11:  # fuel levels
                        Message = self.ser.read(4)
                        # H = Word (16 bit unsigned integer),  h=small (16 bit signed integer), B = byte, i = long (32 bit signed integer)
                        NumOfTanks  = struct.unpack( "<i", Message )
                        for x in range(NumOfTanks[0]):
                            TankMessage = self.ser.read(8)
                            Level,Type,TankOn,TankSensors  = struct.unpack("<iBBH", TankMessage)
                            aircraft.fuel.FuelLevels[x] = round(Level * 0.02641729, 2) # convert liters to gallons

                        aircraft.fuel.msg_count += 1
                        if(self.textMode_showRaw==True): aircraft.fuel.msg_last = binascii.hexlify(Message) # save last message.
                        else: aircraft.fuel.msg_last = None

                    elif msgType == 10:  # Engine message
                        Message = self.ser.read(40)
                        if len(Message) == 40:
                            # H = Word,  h=small, B = byte, i = long
                            # B            B           B            B           H    H      H             H              H             h           h         h          h        h           h       h         H         H        H             H              h          H
                            EngineNumber, EngineType, NumberOfEGT, NumberOfCHT, RPM, Pulse, OilPressure1, OilPressure2, FuelPressure, CoolantTemp, OilTemp1, OilTemp2, AuxTemp1, AuxTemp2, AuxTemp3, AuxTemp4, FuelFlow, AuxFuel, ManiPressure, BoostPressure, InletTemp, AmbientTemp  = struct.unpack(
                                "<BBBBHHHHHhhhhhhhHHHHhH", Message
                            )

                            aircraft.engine.NumberOfCylinders = NumberOfEGT
                            aircraft.engine.RPM = RPM
                            aircraft.engine.OilPress = round(OilPressure1 * 0.01450377,2) # In 10th of a millibar (Main oil pressure) convert to PSI
                            aircraft.engine.OilPress2 = round(OilPressure2 * 0.01450377,2)
                            aircraft.engine.FuelPress = round(FuelPressure * 0.01450377,2)
                            aircraft.engine.CoolantTemp = round((CoolantTemp * 1.8) + 32)
                            aircraft.engine.OilTemp = round((OilTemp1 * 1.8) + 32)  # convert from C to F
                            aircraft.engine.OilTemp2 = round((OilTemp2 * 1.8) + 32) # convert from C to F
                            aircraft.engine.FuelFlow = round(FuelFlow * 0.002642,2) # In 10th liters/hour convert to Gallons/hr
                            aircraft.engine.ManPress = ManiPressure * 0.0029529983071445 #In 10th of a millibar to inches of mercury

                            # Then read in a small int for each egt and cht.
                            for x in range(NumberOfEGT):
                                EGTCHTMessage = self.ser.read(2)
                                EGTinC  = struct.unpack("<h", EGTCHTMessage)
                                aircraft.engine.EGT[x] = round((EGTinC[0] * 1.8) + 32) # convert from C to F
                            for x in range(NumberOfCHT):
                                EGTCHTMessage = self.ser.read(2)
                                CHTinC  = struct.unpack("<h", EGTCHTMessage)
                                aircraft.engine.CHT[x] = round((CHTinC[0] * 1.8) + 32)

                            Checksum = self.ser.read(4) # read in last checksum part

                            aircraft.engine.msg_count += 1
                            if(self.textMode_showRaw==True): aircraft.engine.msg_last = binascii.hexlify(Message) # save last message.
                            else: aircraft.engine.msg_last = None

                    else:
                        aircraft.msg_unknown += 1 #else unknown message.
                    
                    if aircraft.demoMode:  #if demo mode then add a delay.  Else reading a file is way to fast.
                        time.sleep(.01)
                        pass
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
        hud_text.print_header("Decoded data from Input Module: %s (Keys: n=nav, a=all, r=raw)"%(self.name))
        if len(aircraft.demoFile):
            hud_text.print_header("Demofile: %s"%(aircraft.demoFile))

        if self.textMode_showAir==True:
            hud_text.print_object(aircraft)

        if self.textMode_showNav==True:
            hud_text.print_header("Nav Data")
            hud_text.print_object(aircraft.nav)

        if self.textMode_showTraffic==True:
            hud_text.changePos(2,40)
            hud_text.print_header("Traffic Data")
            hud_text.print_object(aircraft.traffic)

        if self.textMode_showEngine==True:
            hud_text.changePos(2,75)
            hud_text.print_header("Engine Data")
            hud_text.print_object(aircraft.engine)

        if self.textMode_showFuel==True:
            hud_text.print_header("Fuel Data")
            hud_text.print_object(aircraft.fuel)

        hud_text.print_DoneWithPage()


    #############################################
    ## Function: textModeKeyInput
    ## this is only called when in text mode. And is used to changed text mode options.
    def textModeKeyInput(self, key, aircraft):
        if key==ord('n'):
            self.textMode_showNav = True
            self.textMode_showAir = False
            self.textMode_showTraffic = False
            self.textMode_showEngine = False
            self.textMode_showFuel = False
            hud_text.print_Clear()
            return 0,0
        elif key==ord('a'):
            self.textMode_showNav = True
            self.textMode_showAir = True
            self.textMode_showTraffic = True
            self.textMode_showEngine = True
            self.textMode_showFuel = True
            hud_text.print_Clear()
            return 0,0
        elif key==ord('r'):
            if self.textMode_showRaw == True: self.textMode_showRaw = False
            else: self.textMode_showRaw = True
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
