
#!/usr/bin/env python

# BNO 085 IMU 9 DOF gyro

from ._input import Input
from lib import hud_utils
from . import _utils
import time
from time import sleep
import board
import busio
import adafruit_bno08x
from adafruit_bno08x.i2c import BNO08X_I2C
from lib.common.dataship.dataship_imu import IMU
import math
import traceback

class gyro_i2c_bno085(Input):
    def __init__(self):
        self.name = "bno085 IMU 9dof"
        self.version = 1.0
        self.inputtype = "gyro"
        self.values = []

    def initInput(self,num,aircraft):
        Input.initInput( self,num, aircraft )  # call parent init Input.
        if(self.PlayFile!=None):
            self.isPlaybackMode = True
        else:
            self.isPlaybackMode = False

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
        if not hasattr(self, 'i2c'):
            self.i2c = busio.I2C(board.SCL, board.SDA)
        else:
            self.i2c.deinit()
            self.i2c = busio.I2C(board.SCL, board.SDA)
            self.bno = None
            sleep(1)
        self.bno = BNO08X_I2C(self.i2c, address=self.address)

        self.bno.enable_feature(adafruit_bno08x.BNO_REPORT_ACCELEROMETER)
        self.bno.enable_feature(adafruit_bno08x.BNO_REPORT_LINEAR_ACCELERATION)
        self.bno.enable_feature(adafruit_bno08x.BNO_REPORT_GYROSCOPE)
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
            if aircraft.debug_mode > 0:  # calculate hz.
                current_time = time.time()
                self.imuData.hz = round(1 / (current_time - self.last_read_time), 1)
                self.last_read_time = current_time
            
            #print("Rotation Vector Quaternion:")
            #quat_i, quat_j, quat_k, quat_real = self.bno.quaternion  # pylint:disable=no-member
            roll_offset, pitch_offset, yaw_offset = self.quaternion_to_euler(*self.bno.quaternion)

            #print( "I: %0.6f  J: %0.6f K: %0.6f  Real: %0.6f" % (quat_i, quat_j, quat_k, quat_real))
            #gyro_x, gyro_y, gyro_z = self.bno.gyro
            #accel_x, accel_y, accel_z = self.bno.linear_acceleration
            #print("X: %0.6f  Y: %0.6f Z: %0.6f rads/s" % (gyro_x, gyro_y, gyro_z))

            # update imuData object.
            #self.imuData.quat = [roll_offset, pitch_offset, yaw_offset]
            #self.imuData.gyro = [gyro_x , gyro_y , gyro_z ]
            #self.imuData.accel = [round(accel_x,2), round(accel_y,2), round(accel_z,2)]
            #self.imuData.cali_sys = self.bno.calibration_status

            # update the pitch.  it's backwards. pitch up is negative.
            self.imuData.pitch = -pitch_offset

            # update aircraft object.
            self.imuData.updatePos(pitch_offset, roll_offset, yaw_offset)
            aircraft.imus[self.num_imus] = self.imuData

            if self.feed_into_aircraft:
                aircraft.pitch = self.imuData.pitch
                aircraft.roll = self.imuData.roll
                aircraft.mag_head = self.imuData.yaw
                aircraft.yaw = self.imuData.yaw


        except Exception as e:
            #aircraft.errorFoundNeedToExit = True
            print(e)
            # print full traceback.
            traceback.print_exc()
            #self.bno.soft_reset()
            self.init_i2c()

        return aircraft


# vi: modeline tabstop=8 expandtab shiftwidth=4 softtabstop=4 syntax=python
