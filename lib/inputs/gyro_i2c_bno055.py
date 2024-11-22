#!/usr/bin/env python

# BNO 055 IMU 9 DOF gyro

from ._input import Input
from lib import hud_utils
from . import _utils
import struct
import time
import statistics
import board
import busio
import adafruit_bno055
from lib.common.dataship.dataship_imu import IMU
import math
import binascii

class gyro_i2c_bno055(Input):
    def __init__(self):
        self.name = "bno055"
        self.version = 1.0
        self.inputtype = "gyro"
        self.values = []
        self.num_bno055 = 1
        self.isPlaybackMode = False

    def initInput(self,num,aircraft):
        Input.initInput( self,num, aircraft )  # call parent init Input.
        
        # Check if we're in playback mode
        if self.PlayFile is not None and self.PlayFile is not False:
            # if in playback mode then load example data file
            if self.PlayFile is True:
                defaultTo = "bno055_1.dat"
                self.PlayFile = hud_utils.readConfig(self.name, "playback_file", defaultTo)
            self.ser, self.input_logFileName = Input.openLogFile(self,self.PlayFile,"rb")
            self.isPlaybackMode = True
        else:
            # Normal I2C initialization
            self.i2c = busio.I2C(board.SCL, board.SDA)
            self.bno = adafruit_bno055.BNO055_I2C(self.i2c, address=self.address)

        # check how many imus are already in aircraft.imus. 
        self.num_imus = len(aircraft.imus)

        # check how many imus are named the same as this one. get next number for this one.
        self.num_bno055 = 1
        for index, imu_obj in aircraft.imus.items():
            if imu_obj.name == self.name:
                self.num_bno055 += 1

        # read address from config.
        self.id = hud_utils.readConfig("bno055", "device"+str(self.num_bno055)+"_id", "bno055_"+str(self.num_bno055))
        self.address = hud_utils.readConfigInt("bno055", "device"+str(self.num_bno055)+"_address", 40)

        # should this imu feed into aircraft roll/pitch/yaw? if num is 0 then default is true.
        self.feed_into_aircraft = hud_utils.readConfigBool("bno055", "device"+str(self.num_bno055)+"_aircraft", self.num_imus == 0)

        print("init bno055("+str(self.num_bno055)+") id: "+str(self.id)+" address: "+str(self.address))

        self.last_read_time = time.time()
        if num == 0:
            self.bno.offsets_magnetometer = (-83, -292, -349)
            self.bno.offsets_accelerometer = (23, -64, -42)
            self.bno.offsets_gyroscope = (-2, -1, 1)
        else:
            # else #2 IMU
            self.bno.offsets_magnetometer = (-54, -356, -220)
            self.bno.offsets_accelerometer = (9, -72, -23)
            self.bno.offsets_gyroscope = (1, 4, -1)
 
    def closeInput(self,aircraft):
        print("bno055("+str(self.inputNum)+") close")

    def quaternion_to_euler(self, w, x, y, z):
        roll = math.atan2(2.0 * (w * x + y * z), 1.0 - 2.0 * (x * x + y * y))
        roll = math.degrees(roll)

        pitch_raw = 2.0 * (w * y - z * x)
        pitch = math.asin(max(-1.0, min(1.0, pitch_raw)))  # Clamp value within -1 and 1
        pitch = math.degrees(pitch)

        yaw = -math.atan2(2.0 * (w * z + x * y), 1.0 - 2.0 * (y * y + z * z))
        yaw = math.degrees(yaw)

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
                
                if line.startswith('055'):
                    # Parse the log file format
                    parts = line.split(',')
                    if len(parts) >= 11:
                        pitch = float(parts[1])
                        roll = float(parts[2])
                        yaw = float(parts[3])
                        cali_mag = int(parts[4])
                        cali_accel = int(parts[5])
                        cali_gyro = int(parts[6])
                        cali_sys = int(parts[7])
                        home_pitch = None if parts[8] == 'None' else float(parts[8])
                        home_roll = None if parts[9] == 'None' else float(parts[9])
                        home_yaw = None if parts[10] == 'None' else float(parts[10])
                        
                        # Update IMU data
                        self.imuData.pitch = pitch
                        self.imuData.roll = roll
                        self.imuData.yaw = yaw
                        self.imuData.cali_mag = cali_mag
                        self.imuData.cali_accel = cali_accel
                        self.imuData.cali_gyro = cali_gyro
                        self.imuData.cali_sys = cali_sys
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
                # Existing live sensor reading code
                if aircraft.debug_mode > 0:
                    current_time = time.time()
                    self.imuData.hz = round(1 / (current_time - self.last_read_time), 1)
                    self.last_read_time = current_time

                roll_offset, pitch_offset, yaw_offset = self.quaternion_to_euler(*self.bno.quaternion)
                
                # Update IMU data
                self.imuData.quat = [roll_offset, pitch_offset, yaw_offset]
                self.imuData.cali_mag = self.bno.calibration_status[3]
                self.imuData.cali_accel = self.bno.calibration_status[2]
                self.imuData.cali_gyro = self.bno.calibration_status[1]
                self.imuData.cali_sys = self.bno.calibration_status[0]

                pitch_offset = -pitch_offset

                # Update positions and aircraft
                self.imuData.updatePos(pitch_offset, roll_offset, yaw_offset)
                aircraft.imus[self.num_imus] = self.imuData

                if self.feed_into_aircraft:
                    aircraft.pitch = self.imuData.pitch
                    aircraft.roll = self.imuData.roll
                    aircraft.mag_head = self.imuData.yaw
                    aircraft.yaw = self.imuData.yaw

                # Write to log file if enabled
                if self.output_logFile is not None:
                    log_line = f"055,{self.imuData.pitch},{self.imuData.roll},{self.imuData.yaw},"
                    log_line += f"{self.imuData.cali_mag},{self.imuData.cali_accel},{self.imuData.cali_gyro},"
                    log_line += f"{self.imuData.cali_sys},{self.imuData.home_pitch},{self.imuData.home_roll},"
                    log_line += f"{self.imuData.home_yaw}\n"
                    Input.addToLog(self, self.output_logFile, log_line.encode())

        except Exception as e:
            aircraft.errorFoundNeedToExit = True
            print(e)

        return aircraft

# vi: modeline tabstop=8 expandtab shiftwidth=4 softtabstop=4 syntax=python
