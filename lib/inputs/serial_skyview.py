#!/usr/bin/env python

# Serial input source
# Skyview
# 1/23/2019  Topher
# 11/6/2024  Added IMU data
# 11/30/2024 Added NAV, Autopilot and EMS data   Zap

from ._input import Input
from lib import hud_utils
import math, sys
import serial
import struct
from lib import hud_text
import time
from lib.common.dataship.dataship import IMU
import traceback
from lib.common.dataship.dataship import Dataship

class serial_skyview(Input):
    def __init__(self):
        self.name = "skyview"
        self.version = 1.0
        self.inputtype = "serial"
        self.EOL = 10

    def initInput(self,num,aircraft):
        Input.initInput( self,num, aircraft )  # call parent init Input.
        
        if(self.PlayFile!=None and self.PlayFile!=False):
            # load playback file.
            if self.PlayFile==True:
                defaultTo = "dynon_skyview_data2.txt"
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
    def readMessage(self, dataship: Dataship):
        if dataship.errorFoundNeedToExit:
            return dataship;
        try:
            x = 0
            while x != 33:  # 33(!) is start of dynon skyview.
                t = self.ser.read(1)
                if len(t) != 0:
                    x = ord(t)
                else:
                    if self.isPlaybackMode:  # if no bytes read and in playback mode.  then reset the file pointer to the start of the file.
                        self.ser.seek(0)
                    return dataship
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
                         # Format string breakdown:
                         # 8s - System time (8 bytes)
                         # 4s - Pitch (4 bytes)
                         # 5s - Roll bug (5 bytes)
                         # 3s - Heading bug (3 bytes)
                         # 4s - IAS (4 bytes)
                         # 6s - Pres Alt (6 bytes)
                         # 4s - Turn Rate (4 bytes)
                         # 3s - Lat Accel (3 bytes)
                         # 3s - Vert Accel (3 bytes)
                         # 2s - AOA (2 bytes)
                         # 4s - Vertical Speed (4 bytes)
                         # 3s - OAT (3 bytes)
                         # 4s - TAS (4 bytes)
                         # 3s - Baro Setting (3 bytes)
                         # 6s - Density Altitude (6 bytes)
                         # 3s - Wind Direction (3 bytes)
                         # 2s - Wind Speed (2 bytes)
                         # 2s - Checksum (2 bytes)
                         # 2s - CRLF (2 bytes)                            
                        "2s2s2s2s4s5s3s4s6s4s3s3s2s4s3s4s3s6s3s2s2s2s", msg
                    ) 
                    if HH != b'--' and MM != b'--' and SS != b'--':
                        dataship.sys_time_string = "%d:%d:%d"%(int(HH),int(MM),int(SS))
                        self.time_stamp_string = dataship.sys_time_string
                        self.time_stamp_min = int(MM)
                        self.time_stamp_sec = int(SS)
                        #print("time: "+aircraft.sys_time_string)
                    dataship.pitch = Input.cleanInt(self,pitch) / 10
                    dataship.roll = Input.cleanInt(self,roll) / 10
                    dataship.mag_head = Input.cleanInt(self,HeadingMAG)

                    # Update IMU data
                    self.imuData.heading = dataship.mag_head
                    if dataship.debug_mode > 0:
                        current_time = time.time() # calculate hz.
                        self.imuData.hz = round(1 / (current_time - self.last_read_time), 1)
                        self.last_read_time = current_time
                    # Update the IMU in the aircraft's imu list
                    self.imuData.updatePos(dataship.pitch, dataship.roll, dataship.mag_head)
                    dataship.imus[self.imu_index] = self.imuData

                    dataship.ias = Input.cleanInt(self,IAS) * 0.1
                    dataship.PALT = Input.cleanInt(self,PresAlt)
                    if OAT != b'XXX': dataship.oat = (Input.cleanInt(self,OAT) * 1.8) + 32 # c to f
                    if TAS != b'XXXX': dataship.tas = Input.cleanInt(self,TAS) * 0.1
                    if AOA == b'XX':
                        dataship.aoa = 0
                    else:
                        dataship.aoa = Input.cleanInt(self,AOA)
                    dataship.baro = (Input.cleanInt(self,Baro) + 2750.0) / 100
                    dataship.baro_diff = dataship.baro - 29.921
                    if DA != b'XXXXXX': dataship.DA = Input.cleanInt(self,DA)
                    dataship.alt = int( Input.cleanInt(self,PresAlt) + (dataship.baro_diff / 0.00108) )  # 0.00108 of inches of mercury change per foot.
                    dataship.BALT = dataship.alt
                    dataship.turn_rate = Input.cleanInt(self,TurnRate) * 0.1
                    dataship.vsi = Input.cleanInt(self,VertSpd) * 10
                    dataship.vert_G = Input.cleanInt(self,VertAccel) * 0.1
                    try:
                        dataship.wind_dir = Input.cleanInt(self,WD)
                        dataship.wind_speed = Input.cleanInt(self,WS)
                        dataship.norm_wind_dir = (dataship.mag_head - dataship.wind_dir) % 360 #normalize the wind direction to the airplane heading
                        # compute Gnd Speed when Gnd Speed is unknown (not provided in data)
                        dataship.gndspeed = math.sqrt(math.pow(dataship.tas,2) + math.pow(dataship.wind_speed,2) + (2 * dataship.tas * dataship.wind_speed * math.cos(math.radians(180 - (dataship.wind_dir - dataship.mag_head)))))
                        dataship.gndtrack = dataship.mag_head 
                    except ValueError as ex:
                        # if error trying to parse wind then must not have that info.
                        dataship.wind_dir = 0
                        dataship.wind_speed = 0
                        dataship.norm_wind_dir = 0 #normalize the wind direction to the airplane heading
                        dataship.gndspeed = 0
                    dataship.msg_count += 1

                    if self.output_logFile != None:
                        Input.addToLog(self,self.output_logFile,bytes([33,int(dataType),int(dataVer)]))
                        Input.addToLog(self,self.output_logFile,msg)

                elif dataType == b'2': #Dynon System message (nav,AP, etc)
                    dataship.nav.msg_count += 1
                    msg = self.ser.read(90)
                    if isinstance(msg, str): msg = msg.encode()  # if read from file then convert to bytes
                    HH,MM,SS,FF,HBug,AltBug, ASIBug,VSBug,Course,CDISrcType,CDISourePort,CDIScale,CDIDeflection,GS,APEng,APRollMode,Not1,APPitch,Not2,APRollF,APRollP,APRollSlip,APPitchF, APPitchP,APPitchSlip,APYawF,APYawP,APYawSlip,TransponderStatus,TransponderReply,TransponderIdent,TransponderCode,DynonUnused,Checksum,CRLF= struct.unpack(
                         # Format string breakdown:
                         # 8s - System time (8 bytes)
                         # 3s - Heading bug (3 bytes)
                         # 5s - Altitude bug (5 bytes)
                         # 4s - Airspeed bug (4 bytes)
                         # 4s - Vertical speed bug (4 bytes)
                         # 3s - Course (3 bytes)
                         # c  - CDI source type (1 byte)
                         # c  - CDI source port (1 byte)
                         # 2s - CDI scale (2 bytes)
                         # 3s - CDI deflection (3 bytes)
                         # 3s - Glide slope % (3 bytes)
                         # c  - Autopilot engaged (1 byte)
                         # c  - AP roll mode (1 byte)
                         # c  - Not used (1 byte)
                         # c  - AP pitch mode (1 byte)
                         # c  - Not used (1 byte)
                         # 3s - AP roll force (3 bytes)
                         # 5s - AP roll position (5 bytes)
                         # c  - AP roll slip (1 byte)
                         # 3s - AP pitch force (3 byte)
                         # 5s - AP pitch position (5 bytes)
                         # c  - AP pitch slip (1 byte)
                         # 3s - AP yaw force (3 bytes)
                         # 5s - AP yaw position (5 bytes)
                         # c  - AP yaw slip (1 byte)
                         # c  - Transponder status (1 byte)
                         # c  - Transponder reply (1 byte)
                         # c  - Transponder Ident (1 byte)
                         # 4s - Transponder code (4 bytes)
                         # 10s- Not used (10 bytes)
                         # 2s - Checksum (2 bytes)
                         # 2s - CRLF (2 bytes)
                        "2s2s2s2s3s5s4s4s3scc2s3s3sccccc3s5sc3s5sc3s5scccc4s10s2s2s", msg
                    )
                    if HH != b'--' and MM != b'--' and SS != b'--':
                        dataship.sys_time_string = "%d:%d:%d"%(int(HH),int(MM),int(SS))
                        self.time_stamp_string = dataship.sys_time_string
                        self.time_stamp_min = int(MM)
                        self.time_stamp_sec = int(SS)

                    if HBug != b'XXX': dataship.nav.HeadBug = Input.cleanInt(self, HBug)
                    if AltBug != b'XXXXX': dataship.nav.AltBug = Input.cleanInt(self,AltBug) * 10
                    if ASIBug != b'XXXX': dataship.nav.ASIBug = Input.cleanInt(self,ASIBug) / 10
                    if VSBug != b'XXXX': dataship.nav.VSBug = Input.cleanInt(self,VSBug) / 10
                    if CDIDeflection != b'XXX': dataship.nav.ILSDev = Input.cleanInt(self,CDIDeflection)
                    if GS != b'XXX': dataship.nav.GSDev = Input.cleanInt(self,GS)
                    dataship.nav.HSISource = Input.cleanInt(self,CDISourePort)
                    if CDISrcType == b'0':
                        navSourceType = 'GPS'
                    elif CDISrcType == b'1':
                        navSourceType = 'NAV'
                    elif CDISrcType == b'2':
                        navSourceType = 'LOC'
                    dataship.nav.SourceDesc = navSourceType + str(Input.cleanInt(self,CDISourePort))
                    if CDIScale != b'XX': dataship.nav.GLSHoriz = Input.cleanInt(self,CDIScale) / 10
                    if APEng == b'0': 
                        dataship.nav.APeng = 0
                    elif APEng == b'1' or APEng == b'2' or APEng == b'3' or APEng == b'4' or APEng == b'5' or APEng == b'6' or APEng == b'7':
                        dataship.nav.APeng = 1
                        dataship.nav.AP_RollForce = Input.cleanInt(self,APRollF)
                        if APRollP != 'XXXXX': dataship.nav.AP_RollPos = Input.cleanInt(self,APRollP)
                        dataship.nav.AP_RollSlip = Input.cleanInt(self,APRollSlip)
                        dataship.nav.AP_PitchForce = Input.cleanInt(self,APPitchF)
                        if APPitchP != b'XXXXX': dataship.nav.AP_PitchPos = Input.cleanInt(self,APPitchP)
                        dataship.nav.AP_PitchSlip = Input.cleanInt(self,APPitchSlip)
                        dataship.nav.AP_YawForce = Input.cleanInt(self,APYawF)
                        if APYawP != b'XXXXX': dataship.nav.AP_YawPos = Input.cleanInt(self,APYawP)
                        dataship.nav.AP_YawSlip = Input.cleanInt(self,APYawSlip)
                    if TransponderStatus == b'X':
                        dataship.nav.XPDR_Status = 'OFF'
                    elif TransponderStatus == b'0':
                        dataship.nav.XPDR_Status = 'SBY'
                    elif TransponderStatus == b'1':
                        dataship.nav.XPDR_Status = 'GND'
                    elif TransponderStatus == b'2':
                        dataship.nav.XPDR_Status = 'ON'
                    elif TransponderStatus == b'3':
                        dataship.nav.XPDR_Status = 'ALT'
                    if TransponderReply != b'X': dataship.nav.XPDR_Reply = Input.cleanInt(self,TransponderReply)
                    if TransponderIdent != b'X': dataship.nav.XPDR_Ident = Input.cleanInt(self,TransponderIdent)
                    if TransponderCode != b'XXXX': dataship.nav.XPDR_Code = Input.cleanInt(self,TransponderCode)
                    if self.output_logFile != None:
                        Input.addToLog(self,self.output_logFile,bytes([33,int(dataType),int(dataVer)]))
                        Input.addToLog(self,self.output_logFile,msg)

                elif dataType == b'3': #Dynon EMS Engine data message
                    dataship.engine.msg_count += 1
                    msg = self.ser.read(222)
                    if isinstance(msg,str):msg = msg.encode() # if read from file then convert to bytes
                    HH,MM,SS,FF,OilPress,OilTemp, RPM_L,RPM_R,MAP,FF1,FF2,FP,FL_L,FL_R,Frem,V1,V2,AMPs,Hobbs,Tach,TC1,TC2,TC3,TC4,TC5,TC6,TC7,TC8,TC9,TC10,TC11,TC12,TC13,TC14,GP1,GP2,GP3,GP4,GP5,GP6,GP7,GP8,GP9,GP10,GP11,GP12,GP13,Contacts,Pwr,EGTstate,Checksum,CRLF= struct.unpack(
                                                  # First part - Engine parameters (47 bytes total):
                         # 8s - System time (8 bytes)
                         # 3s - Oil pressure (3 bytes)
                         # 4s - Oil temperature (4 bytes)
                         # 4s - Left RPM (4 bytes)
                         # 4s - Right RPM (4 bytes)
                         # 3s - Manifold pressure (3 bytes)
                         # 3s - Fuel flow 1 (3 bytes)
                         # 3s - Fuel flow 2 (3 bytes)
                         # 3s - Fuel pressure (3 bytes)
                         # 3s - Left fuel quantity (3 bytes)
                         # 3s - Right fuel quantity (3 bytes)
                         # 3s - Fuel remaining (3 bytes)
                         # 3s - Voltage 1 (3 bytes)
                         # 3s - Voltage 2 (3 bytes)
                         # 4s - Amperage (4 bytes)
                         # 5s - Hobbs time (5 bytes)
                         # 5s - Tach time (5 bytes)
                         # 14 Thermocouples, each 4 bytes:
                         # 4s - Thermocouple 1 (4 bytes)
                         # 4s - Thermocouple 2 (4 bytes)
                         # 4s - Thermocouple 3 (4 bytes)
                         # 4s - Thermocouple 4 (4 bytes)
                         # 4s - Thermocouple 5 (4 bytes)
                         # 4s - Thermocouple 6 (4 bytes)
                         # 4s - Thermocouple 7 (4 bytes)
                         # 4s - Thermocouple 8 (4 bytes)
                         # 4s - Thermocouple 9 (4 bytes)
                         # 4s - Thermocouple 10 (4 bytes)
                         # 4s - Thermocouple 11 (4 bytes)
                         # 4s - Thermocouple 12 (4 bytes)
                         # 4s - Thermocouple 13 (4 bytes)
                         # 4s - Thermocouple 14 (4 bytes)
                         # Second part - General purpose inputs and status:
                         # 6s- General purpose input 1 (6 bytes)
                         # 6s- General purpose input 2 (6 bytes)
                         # 6s- General purpose input 3 (6 bytes)
                         # 6s- General purpose input 4 (6 bytes)
                         # 6s- General purpose input 5 (6 bytes)
                         # 6s- General purpose input 6 (6 bytes)
                         # 6s- General purpose input 7 (6 bytes)
                         # 6s- General purpose input 8 (6 bytes)
                         # 6s- General purpose input 9 (6 bytes)
                         # 6s- General purpose input 10 (6 bytes)
                         # 6s- General purpose input 11 (6 bytes)
                         # 6s- General purpose input 12 (6 bytes)
                         # 6s- General purpose input 13 (6 bytes)
                         # 16c- Contact inputs status (Not Used) (16 bytes)
                         # 3s - Power percentage (3 bytes)
                         # 2s - Checksum (2 bytes)
                         "2s2s2s2s3s4s4s4s3s3s3s3s3s3s3s3s3s4s5s5s4s4s4s4s4s4s4s4s4s4s4s4s4s4s6s6s6s6s6s6s6s6s6s6s6s6s6s16s3s1s2s2s", msg
                    )
                    if HH != b'--' and MM != b'--' and SS != b'--':
                        dataship.sys_time_string = "%d:%d:%d"%(int(HH),int(MM),int(SS))
                        self.time_stamp_string = dataship.sys_time_string
                        self.time_stamp_min = int(MM)
                        self.time_stamp_sec = int(SS)

                    if OilPress != b'XXX': dataship.engine.OilPress = Input.cleanInt(self,OilPress)
                    if OilTemp != b'XXXX': dataship.engine.OilTemp = Input.cleanInt(self,OilTemp)
                    dataship.engine.RPM = max(Input.cleanInt(self,RPM_L), Input.cleanInt(self,RPM_R))
                    if MAP != b'XXX': dataship.engine.ManPress = Input.cleanInt(self,MAP) / 10
                    dataship.engine.FuelFlow = Input.cleanInt(self,FF1) / 10
                    dataship.engine.FuelFlow2 = Input.cleanInt(self,FF2) / 10
                    if FP != b'XXX': dataship.engine.FuelPress = Input.cleanInt(self,FP) / 10
                    fuel_level_left  = Input.cleanInt(self, FL_L) / 10
                    fuel_level_right = Input.cleanInt(self, FL_R) / 10
                    dataship.fuel.FuelLevels = [fuel_level_left, fuel_level_right, 0, 0]
                    dataship.fuel.FuelRemain = Input.cleanInt(self,Frem) / 10
                    dataship.engine.volts1 = Input.cleanInt(self,V1) / 10
                    dataship.engine.volts2 = Input.cleanInt(self,V2) / 10
                    if AMPs != b'XXXX': dataship.engine.amps = Input.cleanInt(self,AMPs) / 10
                    dataship.engine.hobbs_time = Input.cleanInt(self,Hobbs) / 10
                    dataship.engine.tach_time = Input.cleanInt(self,Tach) / 10

                    if TC12 != b'XXXX': dataship.engine.EGT[0] = round(((Input.cleanInt(self, TC12)) * 1.8) + 32)  # convert from C to F
                    if TC10 != b'XXXX': dataship.engine.EGT[1] = round(((Input.cleanInt(self, TC10)) * 1.8) + 32)  # convert from C to F
                    if TC8 != b'XXXX': dataship.engine.EGT[2] = round(((Input.cleanInt(self, TC8)) * 1.8) + 32)  # convert from C to F
                    if TC6 != b'XXXX': dataship.engine.EGT[3] = round(((Input.cleanInt(self, TC6)) * 1.8) + 32)  # convert from C to F
                    if TC4 != b'XXXX': dataship.engine.EGT[4] = round(((Input.cleanInt(self, TC4)) * 1.8) + 32)  # convert from C to F
                    if TC2 != b'XXXX': dataship.engine.EGT[5] = round(((Input.cleanInt(self, TC2)) * 1.8) + 32)  # convert from C to F

                    if TC11 != b'XXXX': dataship.engine.CHT[0] = round(((Input.cleanInt(self, TC11)) * 1.8) + 32)  # convert from C to F
                    if TC9 != b'XXXX': dataship.engine.CHT[1] = round(((Input.cleanInt(self, TC9)) * 1.8) + 32)  # convert from C to F
                    if TC7 != b'XXXX': dataship.engine.CHT[2] = round(((Input.cleanInt(self, TC7)) * 1.8) + 32)  # convert from C to F
                    if TC5 != b'XXXX': dataship.engine.CHT[3] = round(((Input.cleanInt(self, TC5)) * 1.8) + 32)  # convert from C to F
                    if TC3 != b'XXXX': dataship.engine.EGT[4] = round(((Input.cleanInt(self, TC3)) * 1.8) + 32)  # convert from C to F
                    if TC1 != b'XXXX': dataship.engine.EGT[5] = round(((Input.cleanInt(self, TC1)) * 1.8) + 32)  # convert from C to F

                    if self.output_logFile != None:
                        Input.addToLog(self,self.output_logFile,bytes([33,int(dataType),int(dataVer)]))
                        Input.addToLog(self,self.output_logFile,msg)
                else:
                    dataship.msg_unknown += 1 # unknown message found.
        except ValueError:
            dataship.msg_bad += 1
            #print("bad:"+str(msg))
            pass
        except struct.error:
            dataship.msg_bad += 1
            pass
        except serial.serialutil.SerialException:
            print("skyview serial exception")
            traceback.print_exc()
            dataship.errorFoundNeedToExit = True

        if self.isPlaybackMode:  #if play back mode then add a delay.  Else reading a file is way to fast.
            time.sleep(.05)
        else:
            #pass
            self.ser.flushInput()  # flush the serial after every message else we see delays

        return dataship


# vi: modeline tabstop=8 expandtab shiftwidth=4 softtabstop=4 syntax=python
