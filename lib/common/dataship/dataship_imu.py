from lib.common import shared

#############################################
## Class: IMU
class IMU(object):
    def __init__(self):
        self.id = ""
        self.name = ""
        self.address = 0
        self.hz = 0

        self.pitch = None
        self.roll = None
        self.yaw = None

        self.quat = [0,0,0,0]
        self.gyro = [0,0,0]
        self.accel = [0,0,0]
        self.mag = [0,0,0]
        self.temp = 0

        self.cali_mag = None
        self.cali_accel = None
        self.cali_gyro = None

        self.home_pitch = None
        self.home_roll = None
        self.home_yaw = None

        self.org_pitch = None
        self.org_roll = None
        self.org_yaw = None

        self.input = None
    
    def home(self, delete=False):
        '''
        Set the home position.
        '''
        if delete:
            self.home_pitch = None
            self.home_roll = None
            self.home_yaw = None
        else:
            # now set the new home position.
            self.home_pitch = self.org_pitch
            self.home_roll = self.org_roll
            self.home_yaw = self.org_yaw
            shared.GrowlManager.add_message(self.id + ": Set home position")
    
    def updatePos(self, pitch, roll, yaw):
        '''
        Update the position of the IMU.
        This will adjust the pitch, roll, and yaw to be relative to the home position (if set)
        '''
        if pitch is None or roll is None:
            self.pitch = None
            self.roll = None
            self.yaw = None
            return
        else:
            self.org_pitch = pitch
            self.org_roll = roll

        # check if pitch and roll are within -180 to 180 degrees
        # if self.org_pitch > 180:
        #     self.org_pitch = 360 - self.org_pitch
        # if self.org_roll > 180:
        #     self.org_roll = 360 - self.org_roll
        # if self.org_pitch < -180:
        #     self.org_pitch = 360 + self.org_pitch
        # if self.org_roll < -180:
        #     self.org_roll = 360 + self.org_roll
        
        # convert yaw from 0-360 to -180 to 180.
        if yaw is not None:
            self.org_yaw = ((yaw + 180) % 360) - 180

        # if not None then adjust all values relative to home.
        if self.home_pitch is not None:
            # Subtract home values and normalize to -180 to 180 range
            self.pitch = round(((self.org_pitch - self.home_pitch + 180) % 360) - 180,1)
            self.roll = round(((self.org_roll - self.home_roll + 180) % 360) - 180,1)
            self.yaw = round(((self.org_yaw - self.home_yaw + 180) % 360) - 180,1)
        else:
            self.pitch = self.org_pitch
            self.roll = self.org_roll
            self.yaw = self.org_yaw

