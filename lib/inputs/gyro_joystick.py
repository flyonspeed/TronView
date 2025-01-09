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
        self.num_axis = None
        self.axis_pitch = 1
        self.axis_roll = 0
        self.axis_yaw = 2
        self.freeze = False

    def initInput(self,num,aircraft):
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
                    
                    if aircraft.debug_mode > 0:
                        current_time = time.time()
                        self.imuData.hz = round(1 / (current_time - self.last_read_time), 1)
                        self.last_read_time = current_time

                    # Read joystick axis
                    if self.freeze == False:
                        # Map each axis to full 180 degree range (-180 to +180)
                        pitch = round(-self.joystick.get_axis(self.axis_pitch) * 180,3)  # Up/Down on left stick (-180 to 180 degrees)
                        roll = round(self.joystick.get_axis(self.axis_roll) * 180,3)    # Left/Right on left stick (-180 to 180 degrees)
                        yaw = round(self.joystick.get_axis(self.axis_yaw) * 180,3)     # Left/Right on right stick (-180 to 180 degrees)
                        # convert yaw to 0-360 degrees
                        if yaw < 0:
                            yaw += 360

                        # Update IMU data
                        self.imuData.updatePos(pitch, roll, yaw)

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

                    # button 0:  is home
                    if self.joystick.get_button(0):
                        print("Button 0 pressed: home!")
                        self.imuData.home()
                        # wait for button 0 to be released
                        while self.joystick.get_button(0):
                            time.sleep(0.1)
                    
                    # button 1: then freeze the current position
                    if self.joystick.get_button(1):
                        print("Button 1 pressed: freeze!")
                        if self.freeze == False:
                            self.freeze = True
                        else:
                            self.freeze = False
                        # wait for button 1 to be released
                        while self.joystick.get_button(1):
                            time.sleep(0.1)

        except Exception as e:
            print(e)
            traceback.print_exc()

        return aircraft

    def setJoystick(self, joystick):
        self.joystick = joystick
        self.num_axis = joystick.get_numaxes()
        print("setJoystick() %i: %s, num_axis: %s" % (joystick.get_instance_id(), joystick.get_name(), self.num_axis))

        # map nimbus joystick axes to the correct ones.
        if joystick.get_name() == "Nimbus":
            self.axis_pitch = 11
            self.axis_roll = 10
            self.axis_yaw = 14

    def setPostion(self, pitch, roll, yaw):
        """Manual position setting (mainly for testing)"""
        self.imuData.updatePos(pitch, roll, yaw)

# vi: modeline tabstop=8 expandtab shiftwidth=4 softtabstop=4 syntax=python
