#!/usr/bin/env python

# wifi udp input source
# Stratux UDP
# 1/23/2019 Christopher Jones

from ._input import Input
from lib import hud_utils
import struct
from lib import hud_text
import binascii
import time
import socket
import re
import sys
import traceback
from lib.aircraft import Target
import time

class stratux_wifi(Input):
    def __init__(self):
        self.name = "stratux"
        self.version = 1.0
        self.inputtype = "network"

    def initInput(self,num,aircraft):
        Input.initInput( self,num, aircraft )  # call parent init Input.

        if aircraft.demoMode:
            # if in demo mode then load example data file.
            # get demo file to read from config.  else default to..
            if not len(aircraft.demoFile):
                defaultTo = "stratux_data1.bin"
                aircraft.demoFile = hud_utils.readConfig(self.name, "demofile", defaultTo)
            self.ser,self.input_logFileName = Input.openLogFile(self,aircraft.demoFile,"rb")
        else:
            self.udpport = hud_utils.readConfigInt("DataInput", "udpport", "4000")

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
                    aircraft.input1.Name = 'Stratux'
                    aircraft.input1.Connect = 'UDP'
                    aircraft.input1.Ver = FirmwareVer
                    aircraft.input1.Battery = Batt
                    if(msg[4]==2):
                        if(WAAS==1):
                            aircraft.gps.GPSWAAS = 1
                        else:
                            aircraft.gps.GPSWAAS = 0


                elif(msg[3]==1): # ahrs and air data.
                    #print("len:"+str(len(msg))+" "+str(msg[len(msg)-1]))
                    if(len(msg)==27):
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
                        aircraft.msg_count += 1
                    else:
                        aircraft.msg_bad +=1

                elif(msg[3]==2): # more metrics.. 
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

                if(self.textMode_showRaw==True): aircraft.msg_last = binascii.hexlify(msg) # save last message.

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
                elif(msg[1]==20): # Traffic report
                    #print("GDL 90 Traffic message id:"+str(msg[1])+" len:"+str(len(msg)))
                    #print(msg.hex())

                    callsign = re.sub(r'[^A-Za-z0-9]+', '', msg[20:28].rstrip().decode('ascii', errors='ignore') ) # clean the N number.
                    targetStatus = _thunkByte(msg[2], 0x0b11110000, -4) ;# status
                    targetType = _thunkByte(msg[2], 0b00001111) ;# type

                    target = Target(callsign)
                    target.aStat = targetStatus
                    target.type = targetType
                    # get lat/lon
                    latLongIncrement = 180.0 / (2**23)
                    target.lat = _signed24(msg[6:]) * latLongIncrement
                    target.lon = _signed24(msg[9:]) * latLongIncrement
                    # alt of target.
                    alt = _thunkByte(msg[12], 0xff, 4) + _thunkByte(msg[13], 0xf0, -4)
                    target.alt = (alt * 25) - 1000
                    #speed
                    horzVelo = _thunkByte(msg[15], 0xff, 4) + _thunkByte(msg[16], 0xf0, -4)
                    if horzVelo == 0xfff:  # no hvelocity info available
                        horzVelo = 0
                    target.speed = int(horzVelo)
                    # heading
                    trackIncrement = 360.0 / 256
                    target.track = int(msg[18] * trackIncrement)  # track/heading, 0-358.6 degrees
                    # vert speed. 12-bit signed value of 64 fpm increments
                    vertVelo = _thunkByte(msg[16], 0x0f, 8) + _thunkByte(msg[17])
                    if vertVelo == 0x800:   # not avail
                        vertVelo = 0
                    elif (vertVelo >= 0x1ff and vertVelo <= 0x7ff) or (vertVelo >= 0x801 and vertVelo <= 0xe01):  # not used, invalid
                        vertVelo = 0
                    elif vertVelo > 2047:  # two's complement, negative values
                        vertVelo -= 4096
                    target.vspeed = (vertVelo * 64) ;# vertical velocity

                    aircraft.traffic.addTarget(target) # add/update target to traffic list.

                    aircraft.traffic.msg_count += 1
                    if(self.textMode_showRaw==True): 
                        aircraft.traffic.msg_last = binascii.hexlify(msg)
                    pass
                elif(msg[1]==101): # Foreflight id?
                    pass

                if(self.textMode_showRaw==True): 
                    aircraft.gdl_msg_last = binascii.hexlify(msg) # save last message.
                    msgNum = int(msg[1])
                    if(msgNum!=20 and msgNum != 10 and msgNum != 11 and msgNum != 83):
                        aircraft.gdl_msg_last_id = " "+str(msgNum)+" "



            return aircraft
        except ValueError:
            print("stratux value error exception")
            aircraft.errorFoundNeedToExit = True
        except struct.error:
            #error with read in length.. ignore for now?
            #print("Error with read in length")
            pass
        except Exception as e:
            aircraft.errorFoundNeedToExit = True
            print(e)
            print(traceback.format_exc())
        return aircraft


def _unsigned24(data, littleEndian=False):
    """return a 24-bit unsigned integer with selectable Endian"""
    assert len(data) >= 3
    if littleEndian:
        b0 = data[2]
        b1 = data[1]
        b2 = data[0]
    else:
        b0 = data[0]
        b1 = data[1]
        b2 = data[2]
    
    val = (b0 << 16) + (b1 << 8) + b2
    return val


def _signed24(data, littleEndian=False):
    """return a 24-bit signed integer with selectable Endian"""
    val = _unsigned24(data, littleEndian)
    if val > 8388607:
        val -= 16777216
    return val


def _unsigned16(data, littleEndian=False):
    """return a 16-bit unsigned integer with selectable Endian"""
    assert len(data) >= 2
    if littleEndian:
        b0 = data[1]
        b1 = data[0]
    else:
        b0 = data[0]
        b1 = data[1]
    
    val = (b0 << 8) + b1
    return val


def _signed16(data, littleEndian=False):
    """return a 16-bit signed integer with selectable Endian"""
    val = _unsigned16(data, littleEndian)
    if val > 32767:
        val -= 65536
    return val

def _thunkByte(c, mask=0xff, shift=0):
    """extract an integer from a byte applying a mask and a bit shift
    @c character byte
    @mask the AND mask to get the desired bits
    @shift negative to shift right, positive to shift left, zero for no shift
    """
    val = c & mask
    if shift < 0:
        val = val >> abs(shift)
    elif shift > 0:
        val = val << shift
    return val

# vi: modeline tabstop=8 expandtab shiftwidth=4 softtabstop=4 syntax=python
