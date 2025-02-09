from enum import Enum

## Enum: Purpose
class IMU_Purpose(Enum):
    NONE    = 0
    CAMERA  = 1
    AHRS    = 2


#############################################
## Class: IMU
class IMUData(object):
    def __init__(self):
        self.inputSrcName = None
        self.inputSrcNum = None

        self.id = ""
        self.name = ""
        self.purpose: IMU_Purpose = None # IMU_Purpose
        self.address = 0
        self.hz = 0

        self.pitch = None
        self.roll = None
        self.yaw = None
        self.turn_rate = None # Turn rate in 10th of a degree per second
        self.slip_skid = None # -99 to +99.  (-99 is full right)
        self.mag_head = None # Magnetic heading in degrees
        self.vert_G = None # Vertical G force.
        
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

        self.msg_count = 0
        self.msg_last = None
        self.msg_bad = 0
        self.msg_unknown = 0

    
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
        
        # convert yaw from 0-360 to -180 to 180.
        if yaw is not None:
            self.org_yaw = ((yaw + 180) % 360) - 180

        # if not None then adjust all values relative to home.
        if self.home_pitch is not None:
            # Subtract home values and normalize to -180 to 180 range
            self.pitch = round(((self.org_pitch - self.home_pitch + 180) % 360) - 180,3)
            self.roll = round(((self.org_roll - self.home_roll + 180) % 360) - 180,3)
            self.yaw = round(((self.org_yaw - self.home_yaw + 180) % 360) - 180,3)
        else:
            self.pitch = self.org_pitch
            self.roll = self.org_roll
            self.yaw = self.org_yaw

