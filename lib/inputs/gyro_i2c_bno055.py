
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

class gyro_i2c_bno055(Input):
    def __init__(self):
        self.name = "bno055 IMU 9dof"
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
        self.bno = adafruit_bno055.BNO055_I2C(self.i2c)

        # create gyro in aircraft object.
        #aircraft.imus.append()


    def closeInput(self,aircraft):
        print("bno055 close")

    #############################################
    ## Function: readMessage
    def readMessage(self, aircraft):
        if self.shouldExit == True: aircraft.errorFoundNeedToExit = True
        if aircraft.errorFoundNeedToExit: return aircraft
        if self.skipReadInput == True: return aircraft

        try:
            
            #print("Rotation Vector Quaternion:")
            quat_i, quat_j, quat_k, quat_real = self.bno.quaternion
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
