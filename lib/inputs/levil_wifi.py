#!/usr/bin/env python

# wifi udp input source
# levil (ilevil and B.O.M)
# 1/23/2019 Christopher Jones

from ._input import Input
from lib import hud_utils
import struct
from lib import hud_text
import binascii
import time
import socket

class levil_wifi(Input):
    def __init__(self):
        self.name = "levil"
        self.version = 1.0
        self.inputtype = "network"
        self.port = 43211
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

        if aircraft.demoMode:
            # if in demo mode then load example data file.
            # get demo file to read from config.  else default to..
            if not len(aircraft.demoFile):
                defaultTo = "levil_data1.bin"
                aircraft.demoFile = hud_utils.readConfig(self.name, "demofile", defaultTo)
            self.ser,self.input_logFileName = Input.openLogFile(self,aircraft.demoFile,"rb")
        else:
            self.udpport = hud_utils.readConfigInt("DataInput", "udpport", "43211")

            # open udp connection.
            self.ser = socket.socket(socket.AF_INET, #Internet
                                    socket.SOCK_DGRAM) #UDP
                             
            #Bind to any available address on port *portNum*
            print("using UDP port:"+str(self.udpport))
            self.ser.bind(("",self.udpport))
            
            #Prevent the socket from blocking until it receives all the data it wants
            #Note: Instead of blocking, it will throw a socket.error exception if it
            #doesn't get any data
            #self.ser.settimeout(.1)
            self.ser.setblocking(0)

    def closeInput(self,aircraft):
        if aircraft.demoMode:
            self.ser.close()
        else:
            self.ser.close()

    def getNextChunck(self,aircraft):
        if aircraft.demoMode:
            data = self.ser.read(300)
            if(len(data)==0): self.ser.seek(0)
            #TODO: read to the next ~ in the file??
            # x = 0
            # while x != 128: #read to 2nd ~
            #     t = self.ser.read(1)
            #     if len(t) != 0:
            #         x = ord(t)
            #         data.append(x)
            #     else:
            #         self.ser.seek(0) #if at end of file reset
            #         return bytes(0)
            return data
        else:
            try:
                #Attempt to receive up to 1024 bytes of data
                data = self.ser.recvfrom(1024)
                return data[0]
            except socket.timeout:
                pass
            except socket.error:
                #If no data is received, you get here, but it's not an error
                #Ignore and continue
                pass
        return bytes(0)

    #############################################
    ## Function: readMessage
    def readMessage(self, aircraft):
        if self.shouldExit == True: aircraft.errorFoundNeedToExit = True
        if aircraft.errorFoundNeedToExit: return aircraft
        if self.skipReadInput == True: return aircraft
        msg = self.getNextChunck(aircraft)
        #count = msg.count(b'~~')
        #print("-----------------------------------------------\nNEW Chunk len:"+str(len(msg))+" seperator count:"+str(count))
        #print("chunk:"+str(msg))

        for line in msg.split(b'~~'):
            if(len(line)>3):
                if(line[0]!=126): # if no ~ then add one...
                    newline = b''.join([b'~',line])
                else:
                    newline = line
                aircraft = self.processSingleMessage(newline,aircraft)
            #key = wait_key()
            #if(key=='q'): aircraft.errorFoundNeedToExit = True

        if self.output_logFile != None:
            #Input.addToLog(self,self.output_logFile,bytearray([5,2]))
            Input.addToLog(self,self.output_logFile,msg)


        return aircraft

    #############################################
    def processSingleMessage(self, msg, aircraft):
        try:
            
            if(len(msg)<1):
                pass
            elif(msg[0]==126 and msg[1]==ord('L') and msg[2]==ord('E')):  # Check for Levil specific messages ~LE
                #print(msg)
                #print("Len:"+str(len(msg)))
                #print("Message ID "+format(msg[3]));
                if(msg[3]==0): # status message
                    #print(msg)
                    #print("status message len:"+str(len(msg)))
                    # B          B     H     B    B   
                    FirmwareVer, Batt, Error,WAAS,Aux = struct.unpack(">BBHBB",msg[5:11])
                    aircraft.input1.Name = 'Levil'
                    aircraft.input1.Connect = 'UDP'
                    aircraft.input1.Ver = FirmwareVer
                    aircraft.input1.Battery = Batt
                    if(msg[4]==2):
                        if(WAAS==1):
                            aircraft.gps.GPSWAAS = 1
                        else:
                            aircraft.gps.GPSWAAS = 0


                elif(msg[3]==1): # ahrs and air data.
                    # h   h     h   h      h         h,    h   H        h     B   B
                    Roll,Pitch,Yaw,Inclin,TurnCoord,GLoad,ias,pressAlt,vSpeed,AOA,OAT = struct.unpack(">hhhhhhhHhBB",msg[5:25]) 
                    aircraft.roll = Roll * 0.1
                    aircraft.pitch = Pitch * 0.1
                    aircraft.mag_head = Yaw * 0.1
                    aircraft.slip_skid = TurnCoord * 0.01
                    aircraft.vert_G = GLoad * 0.1
                    aircraft.ias = ias * 0.115078 # convert to MPH
                    aircraft.PALT = pressAlt
                    aircraft.vsi = vSpeed
                    if(msg[4]==2): # if version is 2 then read AOA and OAT
                        aircraft.aoa = AOA
                        aircraft.oat = OAT
                    aircraft.msg_last = msg

                elif(msg[3]==2): # more metrics.. like AOA for BOM.
                    #print("additonal metrics message len:"+str(len(msg)))
                    AOA,OAT = struct.unpack(">BB",msg[5:7]) 
                    aircraft.aoa = AOA
                    aircraft.oat = OAT

                elif(msg[3]==7):
                    #print("additonal metrics message len:"+str(len(msg)))
                    WAASstatus, Sats, Power, OutRate = struct.unpack(">BBHB",msg[5:10]) 
                    aircraft.gps.SatsTracked = Sats
                    aircraft.gps.msg_count += 1

                else:
                    #print("unkown message id:"+str(msg[3])+" len:"+str(len(msg)))
                    #print(msg)
                    aircraft.msg_unknown += 1 #else unknown message.
                    
                if aircraft.demoMode:  #if demo mode then add a delay.  Else reading a file is way to fast.
                    time.sleep(.02)
                    pass
                else:
                    #else reading realtime data via udp connection
                    pass

                return aircraft

            else:
                #print("GDL 90 message id:"+str(msg[1])+" "+str(msg[2])+" "+str(msg[3])+" len:"+str(len(msg)))
                #print(msg.hex())
                #aircraft.msg_bad += 1 #bad message found.
                if(msg[1]==0): # GDL heart beat. 
                    #print("GDL 90 HeartBeat message id:"+str(msg[1])+" len:"+str(len(msg)))
                    #print(msg.hex())
                    Status1,Status2 = struct.unpack(">BB",msg[2:4]) 
                    Time = struct.unpack(">H",msg[4:6]) 
                    #print("Time "+str(Time))
                elif(msg[1]==10): # GDL ownership
                    #print("GDL 90 HeartBeat message id:"+str(msg[1])+" len:"+str(len(msg)))
                    #print(msg.hex())
                    pass
                elif(msg[1]==101): # Foreflight id?
                    pass


            return aircraft
        except ValueError:
            print("levil value error exception")
            aircraft.errorFoundNeedToExit = True
        except struct.error:
            #error with read in length.. ignore for now?
            #print("Error with read in length")
            pass
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
            hud_text.changePos(2,40)
            hud_text.print_header("Nav Data")
            hud_text.print_object(aircraft.nav)

        if self.textMode_showTraffic==True:
            hud_text.print_header("Traffic Data")
            hud_text.print_object(aircraft.traffic)
            hud_text.print_header("GPS")
            hud_text.print_object(aircraft.gps)

        if self.textMode_showEngine==True:
            hud_text.changePos(2,75)
            hud_text.print_header("Engine Data")
            hud_text.print_object(aircraft.engine)

        if self.textMode_showFuel==True:
            hud_text.print_header("Fuel Data")
            hud_text.print_object(aircraft.fuel)
            hud_text.print_header("Input Source")
            hud_text.print_object(aircraft.input1)

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
