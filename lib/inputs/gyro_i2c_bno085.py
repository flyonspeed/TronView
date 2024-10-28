
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

        self.i2c = busio.I2C(board.SCL, board.SDA)
        self.bno = BNO08X_I2C(self.i2c)

        #self.bno.enable_feature(BNO_REPORT_ACCELEROMETER)
        self.bno.enable_feature(adafruit_bno08x.BNO_REPORT_GYROSCOPE)
        #self.bno.enable_feature(BNO_REPORT_MAGNETOMETER)
        self.bno.enable_feature(adafruit_bno08x.BNO_REPORT_ROTATION_VECTOR)
        #self.bno.enable_feature(adafruit_bno08x.BNO_REPORT_GAME_ROTATION_VECTOR)

        # create gyro in aircraft object.
        #aircraft.imus.append()


    def closeInput(self,aircraft):
        print("bno085 close")

    #############################################
    ## Function: readMessage
    def readMessage(self, aircraft):
        if self.shouldExit == True: aircraft.errorFoundNeedToExit = True
        if aircraft.errorFoundNeedToExit: return aircraft
        if self.skipReadInput == True: return aircraft

        try:
            
            #print("Rotation Vector Quaternion:")
            quat_i, quat_j, quat_k, quat_real = self.bno.quaternion  # pylint:disable=no-member
            print( "I: %0.6f  J: %0.6f K: %0.6f  Real: %0.6f" % (quat_i, quat_j, quat_k, quat_real))
            gyro_x, gyro_y, gyro_z = self.bno.gyro
            #print("X: %0.6f  Y: %0.6f Z: %0.6f rads/s" % (gyro_x, gyro_y, gyro_z))


            #aircraft.pitch = gyro_x * 180
            #aircraft.roll = gyro_y * 180

            aircraft.pitch = quat_j * 180
            aircraft.roll = quat_i * 180
            aircraft.mag_head = quat_k * 360


        except Exception as e:
            aircraft.errorFoundNeedToExit = True
            print(e)
            #print(traceback.format_exc())
        return aircraft




# vi: modeline tabstop=8 expandtab shiftwidth=4 softtabstop=4 syntax=python
