#!/usr/bin/env python

from ._input import Input
from lib import hud_utils
import time
import traceback
import pygame
from lib.common.dataship.dataship_imu import IMU

class gyro_joystick(Input):
    def __init__(self):
        self.name = "imuJoystick"
        self.version = 1.0
        self.inputtype = "gyro"
        self.values = []
        self.isPlaybackMode = False

        self.joystick = None
        self.num_axes = None  

    def initInput(self,num,aircraft):
        pygame.joystick.init()
        Input.initInput(self,num,aircraft)  # call parent init Input.

        # get this num of imu
        self.num_imus = len(aircraft.imus)

        # check how many imus are named the same as this one. get next number for this one.
        self.num_imu = 1
        for index, imu in aircraft.imus.items():
            if imu.name == self.name:   
                self.num_imu += 1

        # read address from config.
        self.id = hud_utils.readConfig("imu_joystick", "device"+str(self.num_imu)+"_id", "imu_joystick_"+str(self.num_imu))
        self.feed_into_aircraft = hud_utils.readConfigBool("imu_joystick", "device"+str(self.num_imu)+"_aircraft", self.num_imus == 0)
        print("init imu_joystick("+str(self.num_imu)+") id: "+str(self.id))
        
        # Playback mode handling
        if self.PlayFile is not None and self.PlayFile is not False:
            if self.PlayFile is True:
                defaultTo = "imu_joystick1.dat"
                self.PlayFile = hud_utils.readConfig(self.name, "playback_file", defaultTo)
            self.ser, self.input_logFileName = Input.openLogFile(self,self.PlayFile,"rb")
            self.isPlaybackMode = True

        # create a empty imu object.
        self.imuData = IMU()
        self.imuData.id = self.id
        self.imuData.name = self.name
        self.imuData.home_pitch = None
        self.imuData.home_roll = None
        self.imuData.home_yaw = None
        self.imuData.input = self

        # create imu in dataship object
        aircraft.imus[self.num_imus] = self.imuData

        self.last_read_time = time.time()
        self.start_time = time.time()

    def closeInput(self,aircraft):
        print("imu_joystick close")

    def readMessage(self, aircraft):
        if self.shouldExit == True: aircraft.errorFoundNeedToExit = True
        if aircraft.errorFoundNeedToExit: return aircraft
        if self.skipReadInput == True: return aircraft

        try:
            if self.isPlaybackMode:
                # Playback mode code remains the same...
                # ... (previous playback code)
                pass
            
            else:
                # Handle joystick input
                if self.joystick:
                    #pygame.event.pump()  # Process pygame events
                    
                    # Read joystick axes
                    # Map each axis to full 180 degree range (-180 to +180)
                    pitch = round(-self.joystick.get_axis(1) * 180,2)  # Up/Down on left stick (-180 to 180 degrees)
                    roll = round(self.joystick.get_axis(0) * 180,2)    # Left/Right on left stick (-180 to 180 degrees)
                    yaw = round(self.joystick.get_axis(2) * 180,2)     # Left/Right on right stick (-180 to 180 degrees)
                    # convert yaw to 0-360 degrees
                    if yaw < 0:
                        yaw += 360
                    
                    #print("pitch: %s, roll: %s, yaw: %s" % (pitch, roll, yaw))
                    
                    # Update IMU data
                    self.imuData.updatePos(pitch, roll, yaw)
                    aircraft.imus[self.num_imus] = self.imuData

                    # Update aircraft if this is the primary IMU
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

        return aircraft

    def setJoystick(self, joystick):
        self.joystick = joystick
        self.num_axes = joystick.get_numaxes()
        print("setJoystick() %i: %s, num_axes: %s" % (joystick.get_instance_id(), joystick.get_name(), self.num_axes))

    def setPostion(self, pitch, roll, yaw):
        """Manual position setting (mainly for testing)"""
        self.imuData.updatePos(pitch, roll, yaw)

# vi: modeline tabstop=8 expandtab shiftwidth=4 softtabstop=4 syntax=python
