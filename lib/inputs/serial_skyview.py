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
                        "2s2s2s2s4s5s3s4s6s4s3s3s2s4s3s4s3s6s3s2s2s2s", msg
                    ) 
                    #print(msg)
                    dataship.sys_time_string = "%d:%d:%d"%(int(HH),int(MM),int(SS))
                    self.time_stamp_string = dataship.sys_time_string
                    self.time_stamp_min = int(MM)
                    self.time_stamp_sec = int(SS)
                    
                    #print("time: "+aircraft.sys_time_string)
                    #print("pitch:"+str(pitch))
                    dataship.pitch = Input.cleanInt(self,pitch) / 10
                    #print("roll:"+str(roll))
                    dataship.roll = Input.cleanInt(self,roll) / 10
                    #print("HeadingMAG:"+str(HeadingMAG))
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

                    #print("IAS:"+str(IAS))
                    dataship.ias = Input.cleanInt(self,IAS) * 0.1
                    #print("PALT:"+str(PresAlt))
                    dataship.PALT = Input.cleanInt(self,PresAlt)
                    #print("TurnRate:"+str(TurnRate))
                    #print("OAT:"+str(OAT))
                    dataship.oat = (Input.cleanInt(self,OAT) * 1.8) + 32 # c to f
                    #print("TAS:"+str(TAS))
                    dataship.tas = Input.cleanInt(self,TAS) * 0.1
                    #print("AOA:"+str(AOA))
                    if AOA == "XX":
                        dataship.aoa = 0
                    else:
                        dataship.aoa = Input.cleanInt(self,AOA)
                    #print("baro:"+str(Baro))
                    dataship.baro = (Input.cleanInt(self,Baro) + 2750.0) / 100
                    dataship.baro_diff = dataship.baro - 29.921
                    dataship.DA = Input.cleanInt(self,DA)
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
                    msg = self.ser.read(27)  # Read 27 fields of system data
                    if isinstance(msg, str):
                        msg = msg.encode()  # Convert to bytes if read from file

                    # Unpack the system data using struct
                    (sys_time, hdg_bug, alt_bug, air_bug, vs_bug, course,
                     cdi_src_type, cdi_src_port, cdi_scale, cdi_deflect, gs,
                     ap_eng, ap_roll_mode, not_used1, ap_roll_force, ap_roll_pos, ap_roll_slip,
                     ap_pitch_force, ap_pitch_pos, ap_pitch_slip, ap_yaw_force, ap_yaw_pos, ap_yaw_slip,
                     xpdr_status, xpdr_reply, xpdr_code, not_used2) = struct.unpack(
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
                         # 3s - Glide slope (3 bytes)
                         # c  - Autopilot engaged (1 byte)
                         # c  - AP roll mode (1 byte)
                         # c  - Not used (1 byte)
                         # c  - AP roll force (1 byte)
                         # c  - AP roll position (1 byte)
                         # c  - AP roll slip (1 byte)
                         # c  - AP pitch force (1 byte)
                         # c  - AP pitch position (1 byte)
                         # c  - AP pitch slip (1 byte)
                         # c  - AP yaw force (1 byte)
                         # c  - AP yaw position (1 byte)
                         # c  - AP yaw slip (1 byte)
                         # c  - Transponder status (1 byte)
                         # c  - Transponder reply (1 byte)
                         # c  - Transponder code (1 byte)
                         # c  - Not used (1 byte)
                         "8s3s5s4s4s3scc2s3s3sccccccccccccccc", msg)

                    # Update aircraft navigation and autopilot data
                    dataship.nav.msg_count += 1
                    dataship.nav.HeadBug = Input.cleanInt(self, hdg_bug)
                    dataship.nav.AltBug = Input.cleanInt(self, alt_bug) * 10
                    dataship.nav.ASIBug = Input.cleanInt(self, air_bug) / 10
                    dataship.nav.VSBug = Input.cleanInt(self, vs_bug) / 10
                    dataship.nav.WPTrack = Input.cleanInt(self, course)
                    
                    # CDI (Course Deviation Indicator) data
                    dataship.nav.HSISource = ord(cdi_src_type) if isinstance(cdi_src_type, bytes) else cdi_src_type
                    dataship.nav.HSISource = ord(cdi_src_port) if isinstance(cdi_src_port, bytes) else cdi_src_port
                    #dataship.nav. = Input.cleanInt(self, cdi_scale) / 10
                    #dataship.nav. = Input.cleanInt(self, cdi_deflect)
                    dataship.nav.GLSVert = Input.cleanInt(self, gs)

                    # Autopilot data
                    dataship.nav.AP = ord(ap_eng) if isinstance(ap_eng, bytes) else ap_eng
                    #dataship.nav. = ord(ap_roll_mode) if isinstance(ap_roll_mode, bytes) else ap_roll_mode
                    
                    # Autopilot forces and positions
                    dataship.nav.AP_RollForce = ord(ap_roll_force) if isinstance(ap_roll_force, bytes) else ap_roll_force
                    dataship.nav.AP_RollPos = ord(ap_roll_pos) if isinstance(ap_roll_pos, bytes) else ap_roll_pos
                    dataship.nav.AP_RollSlip = ord(ap_roll_slip) if isinstance(ap_roll_slip, bytes) else ap_roll_slip
                    
                    dataship.nav.AP_PitchForce = ord(ap_pitch_force) if isinstance(ap_pitch_force, bytes) else ap_pitch_force
                    dataship.nav.AP_PitchPos = ord(ap_pitch_pos) if isinstance(ap_pitch_pos, bytes) else ap_pitch_pos
                    dataship.nav.AP_PitchSlip = ord(ap_pitch_slip) if isinstance(ap_pitch_slip, bytes) else ap_pitch_slip
                    
                    dataship.nav.AP_YawForce = ord(ap_yaw_force) if isinstance(ap_yaw_force, bytes) else ap_yaw_force
                    dataship.nav.AP_YawPos = ord(ap_yaw_pos) if isinstance(ap_yaw_pos, bytes) else ap_yaw_pos
                    dataship.nav.AP_YawSlip = ord(ap_yaw_slip) if isinstance(ap_yaw_slip, bytes) else ap_yaw_slip

                    # Transponder data
                    dataship.nav.XPDR_Status = ord(xpdr_status) if isinstance(xpdr_status, bytes) else xpdr_status
                    dataship.nav.XPDR_Reply = ord(xpdr_reply) if isinstance(xpdr_reply, bytes) else xpdr_reply
                    dataship.nav.XPDR_Code = xpdr_code.decode() if isinstance(xpdr_code, bytes) else xpdr_code

                    if self.output_logFile is not None:
                        Input.addToLog(self, self.output_logFile, bytes([33, int(dataType), int(dataVer)]))
                        Input.addToLog(self, self.output_logFile, msg)

                elif dataType == b'3': #Engine data message EMS
                    msg = self.ser.read(47)  # Read 47 fields of engine data
                    if isinstance(msg, str): 
                        msg = msg.encode()  # Convert to bytes if read from file
                        
                    # Unpack the engine data using struct
                    (system_time, oil_press, oil_temp, rpm_l, rpm_r, map_press, 
                     fuel_flow1, fuel_flow2, fuel_press, fuel_l, fuel_r, fuel_rem,
                     volts1, volts2, amps, hobbs, tach, 
                     thermo1, thermo2, thermo3, thermo4, thermo5, thermo6, thermo7,
                     thermo8, thermo9, thermo10, thermo11, thermo12, thermo13, thermo14,
                     gp1, gp2, gp3, gp4, gp5, gp6, gp7, gp8, gp9, gp10, gp11, gp12, gp13,
                     contacts, pwr_pct, egt_status, checksum) = struct.unpack(
                         # First part - Engine parameters (47 bytes total):
                         # 8s - System time (8 bytes)
                         # 3s - Oil pressure (3 bytes)
                         # 3s - Oil temperature (3 bytes)
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
                         # 3s - Amperage (3 bytes)
                         # 5s - Hobbs time (5 bytes)
                         # 5s - Tach time (5 bytes)
                         # 14 thermocouples, each 3 bytes:
                         # 3s - Thermocouple 1 (3 bytes)
                         # 3s - Thermocouple 2 (3 bytes)
                         # 3s - Thermocouple 3 (3 bytes)
                         # 3s - Thermocouple 4 (3 bytes)
                         # 3s - Thermocouple 5 (3 bytes)
                         # 3s - Thermocouple 6 (3 bytes)
                         # 3s - Thermocouple 7 (3 bytes)
                         # 3s - Thermocouple 8 (3 bytes)
                         # 3s - Thermocouple 9 (3 bytes)
                         # 3s - Thermocouple 10 (3 bytes)
                         # 3s - Thermocouple 11 (3 bytes)
                         # 3s - Thermocouple 12 (3 bytes)
                         # 3s - Thermocouple 13 (3 bytes)
                         # 3s - Thermocouple 14 (3 bytes)
                         # Second part - General purpose inputs and status:
                         # c - General purpose input 1 (1 byte)
                         # c - General purpose input 2 (1 byte)
                         # c - General purpose input 3 (1 byte)
                         # c - General purpose input 4 (1 byte)
                         # c - General purpose input 5 (1 byte)
                         # c - General purpose input 6 (1 byte)
                         # c - General purpose input 7 (1 byte)
                         # c - General purpose input 8 (1 byte)
                         # c - General purpose input 9 (1 byte)
                         # c - General purpose input 10 (1 byte)
                         # c - General purpose input 11 (1 byte)
                         # c - General purpose input 12 (1 byte)
                         # c - General purpose input 13 (1 byte)
                         # c - Contact inputs status (1 byte)
                         # 2s - Power percentage (2 bytes)
                         # 2 - Checksum (2 bytes)
                         "8s3s3s4s4s3s3s3s3s3s3s3s3s3s3s5s5s3s3s3s3s3s3s3s3s3s3s3s3s3s3s" +
                         "cccccccccccccc2s2", msg)

                    # Update aircraft engine data
                    dataship.engine.OilPress = Input.cleanInt(self, oil_press)
                    dataship.engine.OilTemp = Input.cleanInt(self, oil_temp)
                    dataship.engine.RPM = Input.cleanInt(self, rpm_l)
                    #dataship.engine.RPM_Right = Input.cleanInt(self, rpm_r)
                    dataship.engine.ManPress = Input.cleanInt(self, map_press) / 10
                    dataship.engine.FuelFlow = Input.cleanInt(self, fuel_flow1) / 10
                    #dataship.engine.fuel_flow2 = Input.cleanInt(self, fuel_flow2) / 10
                    dataship.engine.FuelPress = Input.cleanInt(self, fuel_press) / 10

                    # Fuel levels and remaining
                    dataship.fuel.FuelLevels[0] = Input.cleanInt(self, fuel_l) / 10
                    dataship.fuel.FuelLevels[1] = Input.cleanInt(self, fuel_r) / 10
                    dataship.fuel.FuelRemain = Input.cleanInt(self, fuel_rem) / 10

                    dataship.engine.volts1 = Input.cleanInt(self, volts1) / 10
                    dataship.engine.volts2 = Input.cleanInt(self, volts2) / 10
                    dataship.engine.amps = Input.cleanInt(self, amps) / 10
                    dataship.engine.hobbs_time = Input.cleanInt(self, hobbs) / 10
                    dataship.engine.tach_time = Input.cleanInt(self, tach) / 10

                    # Update engine temperatures (thermocouples)
                    temps = [thermo1, thermo2, thermo3, thermo4, thermo5, thermo6, thermo7,
                             thermo8, thermo9, thermo10, thermo11, thermo12, thermo13, thermo14]

                    # EGT (Exhaust Gas Temperature) (first 8 thermocouples)
                    dataship.engine.EGT = [Input.cleanInt(self, t) for t in temps[:8]]

                    # CHT (Cylinder Head Temperature) (last 8 thermocouples)
                    dataship.engine.CHT = [Input.cleanInt(self, t) for t in temps[8:]]

                    dataship.engine.msg_count += 1

                    if self.output_logFile is not None:
                        Input.addToLog(self, self.output_logFile, bytes([33, int(dataType), int(dataVer)]))
                        Input.addToLog(self, self.output_logFile, msg)

                else:
                    dataship.msg_unknown += 1 # unknown message found.

            else:
                dataship.msg_bad += 1 # count this as a bad message
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
