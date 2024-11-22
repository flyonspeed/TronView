#!/usr/bin/env python

# BNO 085 IMU 9 DOF gyro

from ._input import Input
from lib import hud_utils
from . import _utils
import time
from time import sleep
import math
import traceback
import binascii
from lib.common.dataship.dataship_imu import IMU

class gyro_i2c_bno085(Input):
    def __init__(self):
        self.name = "bno085"
        self.version = 1.0
        self.inputtype = "gyro"
        self.values = []
        self.isPlaybackMode = False

    def initInput(self,num,aircraft):
        Input.initInput( self,num, aircraft )  # call parent init Input.

        # get this num of imu
        self.num_imus = len(aircraft.imus) # 0 is first imu.

        # check how many imus are named the same as this one. get next number for this one.
        self.num_bno085 = 1
        for index, imu in aircraft.imus.items():
            if imu.name == self.name:   
                self.num_bno085 += 1

        # read address from config.
        self.id = hud_utils.readConfig("bno085", "device"+str(self.num_bno085)+"_id", "bno085_"+str(self.num_bno085))
        self.address = hud_utils.readConfigInt("bno085", "device"+str(self.num_bno085)+"_address", 0x4A)
        # should this imu feed into aircraft roll/pitch/yaw? if num is 0 then default is true.
        self.feed_into_aircraft = hud_utils.readConfigBool("bno085", "device"+str(self.num_bno085)+"_aircraft", self.num_imus == 0)
        print("init bno085("+str(self.num_bno085)+") id: "+str(self.id)+" address: "+str(self.address))

        
        # Check if we're in playback mode
        if self.PlayFile is not None and self.PlayFile is not False:
            # if in playback mode then load example data file
            if self.PlayFile is True:
                defaultTo = "bno085_1.dat"
                self.PlayFile = hud_utils.readConfig(self.name, "playback_file", defaultTo)
            self.ser, self.input_logFileName = Input.openLogFile(self,self.PlayFile,"rb")
            self.isPlaybackMode = True
        else:
            self.init_i2c()

        # create a empty imu object.
        self.imuData = IMU()
        self.imuData.id = self.id
        self.imuData.name = self.name
        self.imuData.address = self.address
        self.imuData.home_pitch = None
        self.imuData.home_roll = None
        self.imuData.home_yaw = None

        # create imu in dataship object. append to dict with key as num_imus.
        aircraft.imus[self.num_imus] = self.imuData

        self.last_read_time = time.time()
        self.start_time = time.time()

    def init_i2c(self):
        import board
        import busio
        from adafruit_bno08x.i2c import BNO08X_I2C
        import adafruit_bno08x

        if not hasattr(self, 'i2c'):
            self.i2c = busio.I2C(board.SCL, board.SDA)
        else:
            self.i2c.deinit()
            self.i2c = busio.I2C(board.SCL, board.SDA)
            self.bno = None
            sleep(1)
        self.bno = BNO08X_I2C(self.i2c, address=self.address)

        #self.bno.enable_feature(adafruit_bno08x.BNO_REPORT_ACCELEROMETER)
        #self.bno.enable_feature(adafruit_bno08x.BNO_REPORT_LINEAR_ACCELERATION)
        #self.bno.enable_feature(adafruit_bno08x.BNO_REPORT_GYROSCOPE)
        #self.bno.enable_feature(adafruit_bno08x.BNO_REPORT_MAGNETOMETER)
        self.bno.enable_feature(adafruit_bno08x.BNO_REPORT_ROTATION_VECTOR)
        #self.bno.enable_feature(adafruit_bno08x.BNO_REPORT_GAME_ROTATION_VECTOR)

    def closeInput(self,aircraft):
        print("bno085 close")

    def quaternion_to_euler(self, x, y, z, w):
        roll = math.atan2(2.0 * (w * x + y * z), 1.0 - 2.0 * (x * x + y * y))
        roll = round(math.degrees(roll), 1)

        pitch_raw = 2.0 * (w * y - z * x)
        pitch = math.asin(max(-1.0, min(1.0, pitch_raw)))  # Clamp value within -1 and 1
        pitch = round(math.degrees(pitch), 1)

        yaw = -math.atan2(2.0 * (w * z + x * y), 1.0 - 2.0 * (y * y + z * z))
        yaw = round(math.degrees(yaw), 1)

        if yaw > 180:
            yaw -= 360
        elif yaw < -180:
            yaw += 360

        return roll, pitch, yaw

    #############################################
    ## Function: readMessage
    def readMessage(self, aircraft):
        if self.shouldExit == True: aircraft.errorFoundNeedToExit = True
        if aircraft.errorFoundNeedToExit: return aircraft
        if self.skipReadInput == True: return aircraft

        try:
            if self.isPlaybackMode:
                # Read from log file
                line = self.ser.readline().decode('utf-8').strip()
                if not line:
                    self.ser.seek(0)
                    return aircraft
                
                if line.startswith('085'):  # Changed from 055 to 085 for BNO085
                    # Parse the log file format
                    parts = line.split(',')
                    if len(parts) >= 8:
                        timeStamp = float(parts[1])
                        pitch = float(parts[2])
                        roll = float(parts[3])
                        yaw = float(parts[4])
                        home_pitch = None if parts[5] == 'None' else float(parts[5])
                        home_roll = None if parts[6] == 'None' else float(parts[6])
                        home_yaw = None if parts[7] == 'None' else float(parts[7])
                        
                        # Update IMU data
                        self.imuData.pitch = pitch
                        self.imuData.roll = roll
                        self.imuData.yaw = yaw
                        self.imuData.home_pitch = home_pitch
                        self.imuData.home_roll = home_roll
                        self.imuData.home_yaw = home_yaw
                        
                        # Update aircraft if this is the primary IMU
                        if self.feed_into_aircraft:
                            aircraft.pitch = pitch
                            aircraft.roll = roll
                            aircraft.mag_head = yaw
                            aircraft.yaw = yaw
                
                time.sleep(0.02)  # Add delay for playback mode
            else:
                # Live sensor reading code
                if aircraft.debug_mode > 0:
                    current_time = time.time()
                    self.imuData.hz = round(1 / (current_time - self.last_read_time), 1)
                    self.last_read_time = current_time

                roll_offset, pitch_offset, yaw_offset = self.quaternion_to_euler(*self.bno.quaternion)

                # update the pitch (it's backwards)
                pitch_offset = -pitch_offset

                # update aircraft object
                self.imuData.updatePos(pitch_offset, roll_offset, yaw_offset)
                aircraft.imus[self.num_imus] = self.imuData

                if self.feed_into_aircraft:
                    aircraft.pitch = self.imuData.pitch
                    aircraft.roll = self.imuData.roll
                    aircraft.mag_head = self.imuData.yaw
                    aircraft.yaw = self.imuData.yaw

                # Write to log file if enabled
                if self.output_logFile is not None:
                    log_line = f"085,{time.time()},{self.imuData.pitch},{self.imuData.roll},{self.imuData.yaw},{self.imuData.home_pitch},{self.imuData.home_roll},{self.imuData.home_yaw}\n"
                    Input.addToLog(self, self.output_logFile, log_line.encode())

        except Exception as e:
            print(e)
            traceback.print_exc()
            if not self.isPlaybackMode:
                self.init_i2c()

        return aircraft

# vi: modeline tabstop=8 expandtab shiftwidth=4 softtabstop=4 syntax=python
