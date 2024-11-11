#!/usr/bin/env python

# Serial input source
# Skyview
# 1/23/2019  Topher
# 11/6/2024  Added IMU data.

from ._input import Input
from lib import hud_utils
import math, sys
import serial
import struct
from lib import hud_text
import time
from lib.common.dataship.dataship import IMU


class serial_skyview(Input):
    def __init__(self):
        self.name = "skyview"
        self.version = 1.0
        self.inputtype = "serial"
        self.EOL = 10

    def initInput(self,num,aircraft):
        Input.initInput( self,num, aircraft )  # call parent init Input.
        
        if(self.PlayFile!=None):
            # load playback file.
            if self.PlayFile==True:
                defaultTo = "dynon_skyview_data1.txt"
                self.PlayFile = hud_utils.readConfig(self.name, "playback_file", defaultTo)
            self.ser,self.input_logFileName = Input.openLogFile(self,self.PlayFile,"r")
            self.isPlaybackMode = True
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
                timeout=1
            )

        # create a empty imu object.
        self.imuData = IMU()
        self.imuData.id = "skyview_imu"
        self.imuData.name = self.name
        self.imu_index = len(aircraft.imus)  # Start at 0
        aircraft.imus[self.imu_index] = self.imuData
        self.last_read_time = time.time()

    # close this data input 
    def closeInput(self,aircraft):
        if self.isPlaybackMode:
            self.ser.close()
        else:
            self.ser.close()

    #############################################
    ## Function: readMessage
    def readMessage(self, aircraft):
        if aircraft.errorFoundNeedToExit:
            return aircraft;
        try:
            x = 0
            while x != 33:  # 33(!) is start of dynon skyview.
                t = self.ser.read(1)
                if len(t) != 0:
                    x = ord(t)
                else:
                    if self.isPlaybackMode:  # if no bytes read and in playback mode.  then reset the file pointer to the start of the file.
                        self.ser.seek(0)
                    return aircraft
            dataType = self.ser.read(1)
            dataVer  = self.ser.read(1)

            if isinstance(dataType,str):
                dataType = dataType.encode() # if read from file then convert to bytes
                dataVer = dataVer.encode()

            if True:
                #msg = (msg[:73]) if len(msg) > 73 else msg
                #aircraft.msg_last = msg
                if dataType == b'1':  # AHRS message
                    msg = self.ser.read(71)
                    if(isinstance(msg,str)): msg = msg.encode() # if read from file then convert to bytes
                    HH, MM, SS, FF, pitch, roll, HeadingMAG, IAS, PresAlt, TurnRate, LatAccel, VertAccel, AOA, VertSpd, OAT, TAS, Baro, DA, WD, WS, Checksum, CRLF = struct.unpack(
                        "2s2s2s2s4s5s3s4s6s4s3s3s2s4s3s4s3s6s3s2s2s2s", msg
                    ) 
                    #print(msg)
                    aircraft.sys_time_string = "%d:%d:%d"%(int(HH),int(MM),int(SS))
                    self.time_stamp_string = aircraft.sys_time_string
                    self.time_stamp_min = int(MM)
                    self.time_stamp_sec = int(SS)
                    
                    #print("time: "+aircraft.sys_time_string)
                    #print("pitch:"+str(pitch))
                    aircraft.pitch = Input.cleanInt(self,pitch) / 10
                    #print("roll:"+str(roll))
                    aircraft.roll = Input.cleanInt(self,roll) / 10
                    #print("HeadingMAG:"+str(HeadingMAG))
                    aircraft.mag_head = Input.cleanInt(self,HeadingMAG)

                    # Update IMU data
                    self.imuData.roll = aircraft.roll
                    self.imuData.pitch = aircraft.pitch
                    self.imuData.yaw = aircraft.yaw
                    self.imuData.heading = aircraft.mag_head
                    if aircraft.debug_mode > 0:
                        current_time = time.time() # calculate hz.
                        self.imuData.hz = round(1 / (current_time - self.last_read_time), 1)
                        self.last_read_time = current_time
                    # Update the IMU in the aircraft's imu list
                    aircraft.imus[self.imu_index] = self.imuData

                    #print("IAS:"+str(IAS))
                    aircraft.ias = Input.cleanInt(self,IAS) * 0.1
                    #print("PALT:"+str(PresAlt))
                    aircraft.PALT = Input.cleanInt(self,PresAlt)
                    #print("TurnRate:"+str(TurnRate))
                    #print("OAT:"+str(OAT))
                    aircraft.oat = (Input.cleanInt(self,OAT) * 1.8) + 32 # c to f
                    #print("TAS:"+str(TAS))
                    aircraft.tas = Input.cleanInt(self,TAS) * 0.1
                    #print("AOA:"+str(AOA))
                    if AOA == "XX":
                        aircraft.aoa = 0
                    else:
                        aircraft.aoa = Input.cleanInt(self,AOA)
                    #print("baro:"+str(Baro))
                    aircraft.baro = (Input.cleanInt(self,Baro) + 2750.0) / 100
                    aircraft.baro_diff = aircraft.baro - 29.921
                    aircraft.DA = Input.cleanInt(self,DA)
                    aircraft.alt = int( Input.cleanInt(self,PresAlt) + (aircraft.baro_diff / 0.00108) )  # 0.00108 of inches of mercury change per foot.
                    aircraft.BALT = aircraft.alt
                    aircraft.turn_rate = Input.cleanInt(self,TurnRate) * 0.1
                    aircraft.vsi = Input.cleanInt(self,VertSpd) * 10
                    aircraft.vert_G = Input.cleanInt(self,VertAccel) * 0.1
                    try:
                        aircraft.wind_dir = Input.cleanInt(self,WD)
                        aircraft.wind_speed = Input.cleanInt(self,WS)
                        aircraft.norm_wind_dir = (aircraft.mag_head - aircraft.wind_dir) % 360 #normalize the wind direction to the airplane heading
                        # compute Gnd Speed when Gnd Speed is unknown (not provided in data)
                        aircraft.gndspeed = math.sqrt(math.pow(aircraft.tas,2) + math.pow(aircraft.wind_speed,2) + (2 * aircraft.tas * aircraft.wind_speed * math.cos(math.radians(180 - (aircraft.wind_dir - aircraft.mag_head)))))
                        aircraft.gndtrack = aircraft.mag_head 
                    except ValueError as ex:
                        # if error trying to parse wind then must not have that info.
                        aircraft.wind_dir = 0
                        aircraft.wind_speed = 0
                        aircraft.norm_wind_dir = 0 #normalize the wind direction to the airplane heading
                        aircraft.gndspeed = 0


                    aircraft.msg_count += 1

                    if self.output_logFile != None:
                        Input.addToLog(self,self.output_logFile,bytes([33,int(dataType),int(dataVer)]))
                        Input.addToLog(self,self.output_logFile,msg)

                elif dataType == b'2': #Dynon System message (nav,AP, etc)
                    aircraft.nav.msg_count += 1
                    #8s     3s   5s      4s     4s    3s     c          c            2s       3s            3s c     c          c    c       c    3s      5s      c            
                    sysTime,HBug,AltBug, AirBug,VSBug,Course,CDISrcType,CDISourePort,CDIScale,CDIDeflection,GS,APEng,APRollMode,Not1,APPitch,Not2,APRollF,APRollP,APRollSlip= struct.unpack(
                        "8s3s5s4s4s3scc2s3s3sccccc3s5sc", msg
                    ) 

                elif dataType == b'3': #Engine data message
                    aircraft.engine.msg_count += 1 

                else:
                    aircraft.msg_unknown += 1 # unknown message found.

            else:
                aircraft.msg_bad += 1 # count this as a bad message
        except ValueError:
            aircraft.msg_bad += 1
            #print("bad:"+str(msg))
            pass
        except struct.error:
            aircraft.msg_bad += 1
            pass
        except serial.serialutil.SerialException:
            print("skyview serial exception")
            aircraft.errorFoundNeedToExit = True


        if self.isPlaybackMode:  #if play back mode then add a delay.  Else reading a file is way to fast.
            time.sleep(.05)
        else:
            #pass
            self.ser.flushInput()  # flush the serial after every message else we see delays


        return aircraft


# vi: modeline tabstop=8 expandtab shiftwidth=4 softtabstop=4 syntax=python
