#!/usr/bin/env python

# Virtual IMU

from ._input import Input
from lib import hud_utils
from . import _utils
import time
from time import sleep
import math
import traceback
import binascii
from lib.common.dataship.dataship_imu import IMUData
from lib.common.dataship.dataship import Dataship
from lib.common.dataship.dataship_gps import GPSData

class gyro_virtual(Input):
    def __init__(self):
        self.name = "imuVirtual"
        self.version = 1.0
        self.inputtype = "gyro"
        self.values = []
        self.isPlaybackMode = False
        self.imuData = IMUData()

    def initInput(self,num,dataship: Dataship):
        Input.initInput( self,num, dataship )  # call parent init Input.

        # get this num of imu
        self.num_imus = len(dataship.imuData) # 0 is first imu.

        # check how many imus are named the same as this one. get next number for this one.
        self.num_imu = 1
        for imu in dataship.imuData:
            if imu.name == self.name:   
                self.num_imu += 1

        # read address from config.
        self.id = hud_utils.readConfig("imu_virtual", "device"+str(self.num_imu)+"_id", "imu_virtual_"+str(self.num_imu))
        print("init imu_virtual("+str(self.num_imu)+") id: "+str(self.id))
        
        # Check if we're in playback mode
        if self.PlayFile is not None and self.PlayFile is not False:
            # if in playback mode then load example data file
            if self.PlayFile is True:
                defaultTo = "imu_virtual1.dat"
                self.PlayFile = hud_utils.readConfig(self.name, "playback_file", defaultTo)
            self.ser, self.input_logFileName = Input.openLogFile(self,self.PlayFile,"rb")
            if self.ser is not None:
                self.isPlaybackMode = True

        # create a empty imu object.
        self.imuData = IMUData()
        self.imuData.name = self.name
        self.imuData.id = self.id+str(self.num_imu)
        self.imuData.home_pitch = None
        self.imuData.home_roll = None
        self.imuData.home_yaw = None
        self.imuData.input = self

        # create imu in dataship object by appending to list
        dataship.imuData.append(self.imuData)

        self.last_read_time = time.time()
        self.start_time = time.time()

        self.test_pitch = 0
        self.test_roll = 0
        self.test_yaw = 0

        self.auto_rotate_pitch = 0
        self.auto_rotate_roll = 0
        self.auto_rotate_yaw = 0
        
    def closeInput(self,dataship: Dataship):
        print("imu_virtual close")

    #############################################
    ## Function: readMessage
    def readMessage(self, dataship: Dataship):
        if self.shouldExit == True: dataship.errorFoundNeedToExit = True
        if dataship.errorFoundNeedToExit: return dataship
        if self.skipReadInput == True: return dataship

        try:
            if self.isPlaybackMode:
                # Read from log file
                line = self.ser.readline().decode('utf-8').strip()
                if not line:
                    self.ser.seek(0)
                    return dataship
                
                if line.startswith('imu'):
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
                                        
                time.sleep(0.02)  # Add delay for playback mode
            else:
                # Live sensor reading code

                if self.auto_rotate_pitch != 0:
                    self.test_pitch += self.auto_rotate_pitch
                    if self.test_pitch > 180:
                        self.test_pitch = -180 + (self.test_pitch - 180)
                    if self.test_pitch < -180:
                        self.test_pitch = 180 + (self.test_pitch + 180)
                if self.auto_rotate_roll != 0:
                    self.test_roll += self.auto_rotate_roll
                    if self.test_roll > 180:
                        self.test_roll = -180 + (self.test_roll - 180)
                    if self.test_roll < -180:
                        self.test_roll = 180 + (self.test_roll + 180)
                if self.auto_rotate_yaw != 0:
                    self.test_yaw += self.auto_rotate_yaw
                    if self.test_yaw > 180:
                        self.test_yaw = -180 + (self.test_yaw - 180)
                    if self.test_yaw < -180:
                        self.test_yaw = 180 + (self.test_yaw + 180)

                # update aircraft object
                self.imuData.updatePos(self.test_pitch, self.test_roll, self.test_yaw)

                # Write to log file if enabled
                if self.output_logFile is not None:
                    log_line = f"085,{time.time()},{self.imuData.pitch},{self.imuData.roll},{self.imuData.yaw},{self.imuData.home_pitch},{self.imuData.home_roll},{self.imuData.home_yaw}\n"
                    Input.addToLog(self, self.output_logFile, log_line.encode())

        except Exception as e:
            print(e)
            traceback.print_exc()
            if not self.isPlaybackMode:
                self.init_i2c()

        return dataship

    def setPostion(self, pitch, roll, yaw):
        self.test_pitch = pitch
        self.test_roll = roll
        self.test_yaw = yaw
    
    def setAutoRotate(self, pitch, roll, yaw):
        self.auto_rotate_pitch = pitch
        self.auto_rotate_roll = roll
        self.auto_rotate_yaw = yaw

# vi: modeline tabstop=8 expandtab shiftwidth=4 softtabstop=4 syntax=python
