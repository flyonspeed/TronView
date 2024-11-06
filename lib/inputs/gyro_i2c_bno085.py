
#!/usr/bin/env python

# BNO 085 IMU 9 DOF gyro

from ._input import Input
from lib import hud_utils
from . import _utils
import struct
import time
import statistics
import board
import busio
import adafruit_bno08x
from adafruit_bno08x.i2c import BNO08X_I2C
from lib.common.dataship.dataship_imu import IMU

class gyro_i2c_bno085(Input):
    def __init__(self):
        self.name = "bno085 IMU 9dof"
        self.version = 1.0
        self.inputtype = "gyro"
        self.values = []

    def initInput(self,num,aircraft):
        Input.initInput( self,num, aircraft )  # call parent init Input.
        if(aircraft.inputs[self.inputNum].PlayFile!=None):
            self.isPlaybackMode = True
        else:
            self.isPlaybackMode = False

        # check how many imus are already in aircraft.imus. this is number of imus + 1.
        self.num_imus = len(aircraft.imus) + 1

        # check how many imus are named the same as this one. get next number for this one.
        self.num_bno085 = 1
        for imu in aircraft.imus:
            if imu.id == self.id:   
                self.num_bno085 += 1

        # read address from config.
        self.id = hud_utils.readConfig("bno085", "device"+str(self.num_bno085)+"_id", "bno085_"+str(self.num_bno085))
        self.address = hud_utils.readConfigInt("bno085", "device"+str(self.num_bno085)+"_address", 0x4A)

        # should this imu feed into aircraft roll/pitch/yaw?
        self.feed_into_aircraft = hud_utils.readConfigBool("bno085", "device"+str(self.num_bno085)+"_aircraft", False)

        print("init bno085("+str(self.num_bno085)+") id: "+str(self.id)+" address: "+str(self.address))


        self.i2c = busio.I2C(board.SCL, board.SDA)
        self.bno = BNO08X_I2C(self.i2c, address=self.address)

        #self.bno.enable_feature(BNO_REPORT_ACCELEROMETER)
        self.bno.enable_feature(adafruit_bno08x.BNO_REPORT_GYROSCOPE)
        #self.bno.enable_feature(BNO_REPORT_MAGNETOMETER)
        self.bno.enable_feature(adafruit_bno08x.BNO_REPORT_ROTATION_VECTOR)
        #self.bno.enable_feature(adafruit_bno08x.BNO_REPORT_GAME_ROTATION_VECTOR)

        # create a empty imu object.
        self.imuData = IMU()
        self.imuData.id = self.id
        self.imuData.name = self.name
        self.imuData.address = self.address

        # create imu in dataship object. append to dict with key as num_imus.
        aircraft.imus[self.num_imus] = self.imuData

        self.last_read_time = time.time()


    def closeInput(self,aircraft):
        print("bno085 close")

    #############################################
    ## Function: readMessage
    def readMessage(self, aircraft):
        if self.shouldExit == True: aircraft.errorFoundNeedToExit = True
        if aircraft.errorFoundNeedToExit: return aircraft
        if self.skipReadInput == True: return aircraft

        try:
            current_time = time.time()
            # calculate hz.
            self.imuData.hz = 1 / (current_time - self.last_read_time)
            self.last_read_time = current_time

            
            #print("Rotation Vector Quaternion:")
            quat_i, quat_j, quat_k, quat_real = self.bno.quaternion  # pylint:disable=no-member
            #print( "I: %0.6f  J: %0.6f K: %0.6f  Real: %0.6f" % (quat_i, quat_j, quat_k, quat_real))
            gyro_x, gyro_y, gyro_z = self.bno.gyro
            #print("X: %0.6f  Y: %0.6f Z: %0.6f rads/s" % (gyro_x, gyro_y, gyro_z))

            # update imuData object.
            self.imuData.quat = [quat_i * 180, quat_j * 180, quat_k * 180, quat_real * 180]
            self.imuData.gyro = [gyro_x * 180, gyro_y * 180, gyro_z * 180]
            self.imuData.pitch = self.imuData.quat[1]
            self.imuData.roll = self.imuData.quat[0]
            self.imuData.yaw = self.imuData.quat[2]

            # update aircraft object.
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
