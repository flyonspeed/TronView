

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
