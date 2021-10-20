#!/usr/bin/env python

# Serial input source
# Dynon D10 and D100
# 2/2/2019 Christopher Jones

from ._input import Input
from lib import hud_utils
import serial
import struct
from lib import hud_text
import time

class serial_d100(Input):
    def __init__(self):
        self.name = "D100"
        self.version = 1.0
        self.inputtype = "serial"

    def initInput(self,num,aircraft):
        Input.initInput( self,num, aircraft )  # call parent init Input.
        
        if aircraft.demoMode:
            # if in demo mode then load example data file.
            self.ser = open("lib/inputs/_example_data/dynon_d100_data1.txt", "r") 
        else:
            self.efis_data_format = hud_utils.readConfig("DataInput", "format", "none")
            self.efis_data_port = hud_utils.readConfig("DataInput", "port", "/dev/ttyS0")
            self.efis_data_baudrate = hud_utils.readConfigInt(
                "DataInput", "baudrate", 115200
            )

            # open serial connection.
            self.ser = serial.Serial(
                port=self.efis_data_port,
                baudrate=self.efis_data_baudrate,
                parity=serial.PARITY_NONE,
                stopbits=serial.STOPBITS_ONE,
                bytesize=serial.EIGHTBITS,
                timeout=1,
            )

    # close this data input 
    def closeInput(self,aircraft):
        if aircraft.demoMode:
            self.ser.close()
        else:
            self.ser.close()

    #############################################
    ## Function: readMessage
    def readMessage(self, aircraft):
        if aircraft.errorFoundNeedToExit:
            return aircraft;
        try:
            x = 0
            while x != 10:  # wait for CR (10) because this is the end of line for a message. (there is no start of a line char on the d10/100 series )
                t = self.ser.read(1)
                if len(t) != 0:
                    x = ord(t)
                else:
                    if aircraft.demoMode:  # if no bytes read and in demo mode.  then reset the file pointer to the start of the file.
                        self.ser.seek(0)
                    return aircraft
            msg = self.ser.read(51)  
            if len(msg) == 51:
                msg = (msg[:51]) if len(msg) > 51 else msg
                aircraft.msg_last = msg
                # 8b        4b    5b   3b  4b   5b   4b        3b        3b         2b   6b                2b          2s  
                HH,MM,SS,FF,pitch,roll,yaw,IAS, Alt, TurnRate, LatAccel, VertAccel, AOA, StatusBitMaskHex, InteralUse, Checksum = struct.unpack(
                    "2s2s2s2s4s5s3s4s5s4s3s3s2s6s2s2s", str.encode(msg)
                )

                if True:
                    aircraft.sys_time_string = "%d:%d:%d"%(int(HH),int(MM),int(SS))
                    aircraft.roll = int(roll) * 0.1
                    aircraft.pitch = int(pitch) * 0.1
                    aircraft.ias = int(IAS) * 0.224  # airspeed in units of 1/10 m/s (1555 = 155.5 m/s) convert to MPH

                    aircraft.aoa = int(AOA)
                    aircraft.mag_head = int(yaw)
                    #aircraft.baro = (int(Baro) + 2750.0) / 100   # no baro for D100 data.
                    #aircraft.baro_diff = aircraft.baro - 29.921
                    #aircraft.alt = int( int(Alt) + (aircraft.baro_diff / 0.00108) )  # 0.00108 of inches of mercury change per foot.
                    aircraft.slip_skid = float(LatAccel) / 100  # slip skid 00 to 99, lateral g's in units of 1/100 g (99 = 0.99 g's).
                    # check status if bit 1 is 0.. then.
                    statusInt = int(StatusBitMaskHex, 16)  # convert hex-ascii to int value
                    if statusInt & 1 == 0:
                        aircraft.BALT = int(Alt) * 3.28084 # convert meters to feet.
                        aircraft.turn_rate = int(TurnRate) * 10
                    else:
                        aircraft.alt = int(Alt) * 3.28084 # convert meters to feet.
                        aircraft.vsi = int(TurnRate)  # vert speed for D100 data
                    

                    aircraft.msg_count += 1

                    if aircraft.demoMode:  #if demo mode then add a delay.  Else reading a file is way to fast.
                        time.sleep(.05)
                    else:
                        self.ser.flushInput()  # flush the serial after every message else we see delays
                    return aircraft
                else:
                    aircraft.msg_unknown += 1 # unknown message found.

            else:
                aircraft.msg_bad += 1 # count this as a bad message
                if aircraft.demoMode:  #if demo mode then add a delay.  Else reading a file is way to fast.
                    time.sleep(.01)
                else:
                    self.ser.flushInput()  # flush the serial after every message else we see delays
                return aircraft
        except ValueError as ex:
            print("dynon d100 data conversion error")
            print(ex)
            aircraft.errorFoundNeedToExit = True
        except serial.serialutil.SerialException:
            print("dynon d100 serial exception")
            aircraft.errorFoundNeedToExit = True
        return aircraft



# vi: modeline tabstop=8 expandtab shiftwidth=4 softtabstop=4 syntax=python
