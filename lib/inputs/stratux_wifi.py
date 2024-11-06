#!/usr/bin/env python

# wifi udp input source
# Stratux UDP
# 1/23/2019 Topher
# 11/4/2024 - Adding debug, and working on AHRS message parsing. 

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
from lib.common.dataship.dataship import Target
import time
import math
from geographiclib.geodesic import Geodesic
import datetime
from lib.common.dataship.dataship import IMU

class stratux_wifi(Input):
    def __init__(self):
        self.name = "stratux"
        self.version = 1.0
        self.inputtype = "network"

    def initInput(self,num,aircraft):
        Input.initInput( self,num, aircraft )  # call parent init Input.

        if(aircraft.inputs[self.inputNum].PlayFile!=None):
            # if in playback mode then load example data file.
            # get file to read from config.  else default to..
            if aircraft.inputs[self.inputNum].PlayFile==True:
                defaultTo = "stratux_9.dat"
                aircraft.inputs[self.inputNum].PlayFile = hud_utils.readConfig(self.name, "playback_file", defaultTo)
            self.ser,self.input_logFileName = Input.openLogFile(self,aircraft.inputs[self.inputNum].PlayFile,"rb")
            self.isPlaybackMode = True
        else:
            self.udpport = hud_utils.readConfigInt("Stratux", "udpport", "4000")

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

        # if this input is not the first input then don't default to read the ahrs input.
        if(num==0): 
            defaultUseAHRS = True
        else: 
            defaultUseAHRS = False
        self.use_ahrs = hud_utils.readConfigBool("Stratux", "use_ahrs", defaultUseAHRS)
        if(self.use_ahrs==False):
            print("Skipping AHRS data from Stratux")

        if(self.use_ahrs):
            # create a empty imu object.
            self.imuData = IMU()
            self.imuData.id = "stratux_imu"
            self.imuData.name = self.name
            self.imu_index = len(aircraft.imus)  # Start at 0
            print("new imu "+str(self.imu_index)+": "+str(self.imuData))
            aircraft.imus[self.imu_index] = self.imuData
            self.last_read_time = time.time()


    def closeInput(self,aircraft):
        if self.isPlaybackMode:
            self.ser.close()
        else:
            self.ser.close()

    def getNextChunck(self,aircraft):
        if self.isPlaybackMode:
            
            x = 0
            while x != 126: # read until ~
                t = self.ser.read(1)
                if len(t) != 0:
                    x = ord(t)
                    #print(str(x), end ="." )
                else:
                    self.ser.seek(0)
                    print("Stratux file reset")

            #print("first ~", end ="." )
            x = 0
            data = bytearray(b"~")
            while x != 126: # read until ~
                t = self.ser.read(1)
                if len(t) != 0:
                    x = ord(t)
                    data.extend(t)
                    #print(str(x), end ="." )
                else:
                    self.ser.seek(0)
                    print("Stratux file reset")
            #print("end ~", end ="." )
            return data
            
            #data = self.ser.read(80)
            #if(len(data)==0): 
            #    self.ser.seek(0)
            #    print("Replaying file: "+self.input_logFileName)
            #TODO: read to the next ~ in the file??
            #print(type(data))
            #return data
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
        if(aircraft.debug_mode>1):
            print("stratux: "+str(msg[1])+" "+str(msg[2])+" "+str(msg[3])+" "+str(len(msg))+" "+str(msg))

        for line in msg.split(b'~~'):
            theLen = len(line)
            if(theLen>3):
                if(line[0]!=126): # if no ~ then add one...
                    newline = b''.join([b'~',line])
                    theLen += 1
                else:
                    newline = line
                if(newline[theLen-1]!=126): # add ~ on the end if not there.
                    newline = b''.join([newline,b'~'])
                aircraft = self.processSingleMessage(newline,aircraft)

                if self.output_logFile != None:
                    Input.addToLog(self,self.output_logFile,newline)

            #key = wait_key()
            #if(key=='q'): aircraft.errorFoundNeedToExit = True



        return aircraft

    #############################################
    def processSingleMessage(self, msg, aircraft):
        try:
            
            if(len(msg)<1):
                pass
            elif(msg[0]==126 and msg[1]==ord('L') and msg[2]==ord('E')):  # Check for Levil specific messages ~LE
                #print(msg)
                #print("Len:"+str(len(msg)))
                if(aircraft.debug_mode>0):
                    print("Message ID "+format(msg[3]));
                # check if we want to read in ahrs data input.
                # if(self.use_ahrs == False):
                #     return aircraft

                if(msg[3]==0): # status message
                    #print(msg)
                    #print("status message len:"+str(len(msg)))
                    # B          B     H     B    B   
                    FirmwareVer, Batt, Error,WAAS,Aux = struct.unpack(">BBHBB",msg[5:11])
                    aircraft.inputs[self.inputNum].FirmwareVer = FirmwareVer
                    aircraft.inputs[self.inputNum].Battery = Batt
                    if(msg[4]==2):
                        if(WAAS==1):
                            aircraft.gps.GPSWAAS = 1
                        else:
                            aircraft.gps.GPSWAAS = 0


                elif(msg[3]==1): # ahrs and air data.
                    if(aircraft.debug_mode>0):
                        print("ahrs levil :"+str(len(msg))+" "+str(msg[len(msg)-1]))
                    if(len(msg)==28):
                        # //###########################################################################################################################
                        # //                 Stratux AHRS message
                        # //  -------------------------------------------------------------------------------------------------------------------------
                        # //  BOM  |ID/TYP|resvd|roll  |  pitch  |   hdg   |slip |  yaw    |  G's | airspd  | palt   | vspd    | resvd   | chksm | EOM  
                        # //  -------------------------------------------------------------------------------------------------------------------------                   
                        # //  [126, 76, 69, 1, 1, 0, 0, 255, 255, 127, 255, 0, 0, 127, 255, 0, 10, 127, 255, 24, 162, 255, 255, 127, 255, 42, 249, 126]
                        # //############################################################################################################################

                        # h   h     h   h      h         h,    h   H        h     B   B
                        Roll,Pitch,Yaw,Inclin,TurnCoord,GLoad,ias,pressAlt,vSpeed,AOA,OAT = struct.unpack(">hhhhhhhHhBB",msg[5:25]) 
                        aircraft.roll = None if Roll == 32767 else Roll / 10
                        aircraft.pitch = None if Pitch == 32767 else Pitch / 10
                        aircraft.mag_head = 0 if Yaw == 32767 else Yaw / 10
                        aircraft.slip_skid = None if TurnCoord == 32767 else TurnCoord / 100
                        aircraft.vert_G = None if GLoad == 32767 else GLoad / 10
                        #aircraft.ias = ias # if ias is 32767 then no airspeed given?
                        aircraft.PALT = pressAlt -5000 # 5000 is sea level.
                        aircraft.vsi = vSpeed
                        if(msg[4]==2): # if version is 2 then read AOA and OAT
                            aircraft.aoa = AOA
                            aircraft.oat = OAT
                        if(self.textMode_showRaw==True): aircraft.msg_last = msg
                        aircraft.msg_count += 1

                        # Update IMU data
                        self.imuData.roll = aircraft.roll
                        self.imuData.pitch = aircraft.pitch
                        self.imuData.yaw = aircraft.yaw
                        self.imuData.heading = aircraft.mag_head
                        self.imuData.turn_rate = aircraft.turn_rate
                        self.imuData.slip_skid = aircraft.slip_skid
                        self.imuData.g_force = aircraft.vert_G
                        #self.imuData.timestamp = time.time()
                        current_time = time.time()
                        # calculate hz.
                        self.imuData.hz = round(1 / (current_time - self.last_read_time), 1)
                        self.last_read_time = current_time
                        # Update the IMU in the aircraft's imus dictionary
                        aircraft.imus[self.imu_index] = self.imuData                        

                    else:
                        aircraft.msg_bad +=1
                        #aircraft.msg_len = len(msg)

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
                    
                if self.isPlaybackMode:  #if playback mode then add a delay.  Else reading a file is way to fast.
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
                    #Status1,Status2 = struct.unpack(">BB",msg[2:4]) 
                    #Time = struct.unpack(">H",msg[4:6]) 
                    #print("Time "+str(Time))
                    if(len(msg)==11):
                        statusByte2 = msg[3]
                        timeStamp = _unsigned16(msg[4:], littleEndian=True)
                        if (statusByte2 & 0b10000000) != 0:
                            timeStamp += (1 << 16)
                        aircraft.traffic.lcl_time_string = str(datetime.timedelta(seconds=int(timeStamp)))   # get time stamp for gdl hearbeat.
                        self.time_stamp_string = aircraft.traffic.lcl_time_string
                        timeObj = datetime.datetime.strptime(aircraft.traffic.lcl_time_string, "%H:%M:%S")
                        self.time_stamp_min = int(timeObj.minute)
                        self.time_stamp_sec = int(timeObj.second)

                    if(self.use_ahrs==True): 
                        aircraft.sys_time_string = aircraft.traffic.lcl_time_string

                elif(msg[1]==10): # GDL ownership
                    #print("GDL 90 owership id:"+str(msg[1])+" len:"+str(len(msg)))
                    if(len(msg)==32):

                        # save gps data coming from traffic source..
                        latLongIncrement = 180.0 / (2**23)
                        aircraft.traffic.src_lat = _signed24(msg[6:]) * latLongIncrement
                        aircraft.traffic.src_lon = _signed24(msg[9:]) * latLongIncrement
                        alt = _thunkByte(msg[12], 0xff, 4) + _thunkByte(msg[13], 0xf0, -4)
                        aircraft.traffic.src_alt = (alt * 25) - 1000

                        horzVelo = _thunkByte(msg[15], 0xff, 4) + _thunkByte(msg[16], 0xf0, -4)
                        if horzVelo == 0xfff:  # no info available
                            horzVelo = None
                        aircraft.traffic.src_gndspeed = int(horzVelo)

                        trackIncrement = 360.0 / 256
                        aircraft.traffic.src_gndtrack = int(msg[18] * trackIncrement)  # track/heading, 0-358.6 degrees

                        # if no gps data is currently being tracked then use it from GDL source.
                        if(aircraft.gps.Source == None or aircraft.gps.Source == self.name):
                            aircraft.gps.Source = self.name
                            aircraft.gps.LatDeg = aircraft.traffic.src_lat
                            aircraft.gps.LonDeg = aircraft.traffic.src_lon
                            aircraft.gps.GPSAlt = aircraft.traffic.src_alt
                            aircraft.gps.GPSStatus = 3
                            aircraft.gps.GndSpeed = aircraft.traffic.src_gndspeed
                            aircraft.gndtrack = aircraft.traffic.src_gndtrack
                            aircraft.gps.GndTrack = aircraft.traffic.src_gndtrack

                elif(msg[1]==11): # GDL OwnershipGeometricAltitude
                    if(self.use_ahrs==False): return aircraft
                    # get alt from GDL90
                    aircraft.alt = _signed16(msg[2:]) * 5

                elif(msg[1]==20): # Traffic report
                    #print("GDL 90 Traffic message id:"+str(msg[1])+" len:"+str(len(msg)))
                    if(len(msg)==32): 
                        #print(msg.hex())

                        callsign = re.sub(r'[^A-Za-z0-9]+', '', msg[20:28].rstrip().decode('ascii', errors='ignore') ) # clean the N number.
                        targetStatus = _thunkByte(msg[2], 0x0b11110000, -4) # status
                        targetType = _thunkByte(msg[2], 0b00001111) # type

                        target = Target(callsign)
                        target.aStat = targetStatus
                        target.type = targetType
                        target.address =  (msg[3] << 16) + (msg[4] << 8) + msg[5] # address
                        # get lat/lon
                        latLongIncrement = 180.0 / (2**23)
                        target.lat = _signed24(msg[6:]) * latLongIncrement
                        target.lon = _signed24(msg[9:]) * latLongIncrement
                        # alt of target.
                        alt = _thunkByte(msg[12], 0xff, 4) + _thunkByte(msg[13], 0xf0, -4)
                        target.alt = (alt * 25) - 1000

                        target.misc = _thunkByte(msg[13], 0x0f) # misc
                        target.NIC = _thunkByte(msg[14], 0xf0, -4) # NIC
                        target.NACp = _thunkByte(msg[14], 0x0f) # NACp

                        #speed
                        horzVelo = _thunkByte(msg[15], 0xff, 4) + _thunkByte(msg[16], 0xf0, -4)
                        if horzVelo == 0xfff:  # no hvelocity info available
                            horzVelo = 0
                        target.speed = int(horzVelo * 1.15078) # convert to mph
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

                        target.cat = int(msg[19]) # emitter category (type/size of aircraft)

                        # # check distance and brng to target. if we know our location..
                        # if(aircraft.gps.LatDeg != None and aircraft.gps.LonDeg != None and target.lat != 0 and target.lon != 0):
                        #     target.dist = _distance(aircraft.gps.LatDeg,aircraft.gps.LonDeg,target.lat,target.lon)
                        #     if(target.dist<500):
                        #         brng = Geodesic.WGS84.Inverse(aircraft.gps.LatDeg,aircraft.gps.LonDeg,target.lat,target.lon)['azi1']
                        #         if(brng<0): target.brng = int(360 - (abs(brng))) # convert foward azimuth to bearing to.
                        #         elif(brng!=brng):
                        #             #its NaN.
                        #             target.brng = None
                        #         else: target.brng = int(brng)
                        # # check difference in altitude from self.
                        # if(aircraft.gps.GPSAlt != None and target.alt != None):
                        #     target.altDiff = target.alt - aircraft.gps.GPSAlt

                        aircraft.traffic.addTarget(target,aircraft) # add/update target to traffic list.

                        aircraft.traffic.msg_count += 1
                    else:
                        aircraft.traffic.msg_bad += 1

                    if(self.textMode_showRaw==True): 
                        aircraft.traffic.msg_last = binascii.hexlify(msg)
                        aircraft.traffic.msg_len = len(msg)

                elif(msg[1]==101): # Foreflight id?
                    pass
                
                else: # unknown message id
                    if(aircraft.debug_mode>0):
                        print("stratuxmessage id:"+str(msg[1])+" "+str(msg[2])+" "+str(msg[3])+" len:"+str(len(msg)))
                    pass

                if(self.textMode_showRaw==True): 
                    aircraft.gdl_msg_last = binascii.hexlify(msg) # save last message.
                    msgNum = int(msg[1])
                    if(msgNum!=20 and msgNum != 10 and msgNum != 11 and msgNum != 83):
                        aircraft.gdl_msg_last_id = " "+str(msgNum)+" "



            return aircraft
        except ValueError as e :
            print("stratux value error exception")
            aircraft.errorFoundNeedToExit = True
            print(e)
            print(traceback.format_exc())
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
    #if(len(data) >= 3): raise Exception("_unsigned24 len(data) >= 3")
    if(len(data)<3): return 0
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
    #if(len(data) >= 2): raise Exception("_unsigned16 len(data) >= 2")
    if(len(data)<2): return 0
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
