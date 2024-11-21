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
class gyro_i2c_bno055(Input):
    def __init__(self):
        self.name = "bno055"
        self.version = 1.0
        self.inputtype = "gyro"
        self.values = []
        self.num_bno055 = 1

    def initInput(self,num,aircraft):
        Input.initInput( self,num, aircraft )  # call parent init Input.
        if(self.PlayFile!=None):
            self.isPlaybackMode = True
        else:
            self.isPlaybackMode = False
        
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

        self.i2c = busio.I2C(board.SCL, board.SDA)
        self.bno = adafruit_bno055.BNO055_I2C(self.i2c, address=self.address)

        # create a empty imu object.
        self.imuData = IMU()
        self.imuData.id = self.id
        self.imuData.name = self.name
        self.imuData.address = self.address
        self.imuData.cali_mag = None
        self.imuData.cali_accel = None
        self.imuData.cali_gyro = None

        self.imuData.home_pitch = None
        self.imuData.home_roll = None
        self.imuData.home_yaw = None

        # create imu in dataship object. append to dict with key as num_imus.
        aircraft.imus[self.num_imus] = self.imuData

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
            if aircraft.debug_mode > 0:  # calculate hz.
                current_time = time.time()
                self.imuData.hz = round(1 / (current_time - self.last_read_time), 1)
                self.last_read_time = current_time

            #print("Rotation Vector Quaternion:")
            roll_offset, pitch_offset, yaw_offset = self.quaternion_to_euler(*self.bno.quaternion)
            #quat_i, quat_j, quat_k, quat_real = self.bno.quaternion
            #print( "I: %0.6f  J: %0.6f K: %0.6f  Real: %0.6f" % (quat_i, quat_j, quat_k, quat_real))
            #gyro_x, gyro_y, gyro_z = self.bno.gyro
            #print("X: %0.6f  Y: %0.6f Z: %0.6f rads/s" % (gyro_x, gyro_y, gyro_z))
            #accel_x, accel_y, accel_z = self.bno.linear_acceleration

            #aircraft.pitch = gyro_x * 180
            #aircraft.roll = gyro_y * 180

            # update imuData object.
            self.imuData.quat = [roll_offset, pitch_offset, yaw_offset]
            #self.imuData.gyro = [gyro_x , gyro_y , gyro_z ]
            #self.imuData.accel = [accel_x, accel_y, accel_z]
            self.imuData.cali_mag = self.bno.calibration_status[3]
            self.imuData.cali_accel = self.bno.calibration_status[2]
            self.imuData.cali_gyro = self.bno.calibration_status[1]
            self.imuData.cali_sys = self.bno.calibration_status[0]

            # reverse pitch and roll
            pitch_offset = -pitch_offset

            # update aircraft object.
            self.imuData.updatePos(pitch_offset, roll_offset, yaw_offset)
            aircraft.imus[self.num_imus] = self.imuData

            if self.feed_into_aircraft:
                aircraft.pitch = self.imuData.pitch
                aircraft.roll = self.imuData.roll
                aircraft.mag_head = self.imuData.yaw
                aircraft.yaw = self.imuData.yaw

        except Exception as e:
            aircraft.errorFoundNeedToExit = True
            print(e)
            #print(traceback.format_exc())
        return aircraft

# vi: modeline tabstop=8 expandtab shiftwidth=4 softtabstop=4 syntax=python
