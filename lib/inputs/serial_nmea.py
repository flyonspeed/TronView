#!/usr/bin/env python

# Serial input source
# NMEA 0183 V3.01

from ._input import Input
from . import _utils
import serial
import struct
import math, sys
import time
import datetime
import pytz
import airportsdata
from timezonefinder import TimezoneFinder

tf = TimezoneFinder()

#######################################
###     FAA Mode indicator decoder  ###
## A = Autonomous Mode               ##
## C = Caution                       ##
## D = Differential (WAAS)           ##
## E = Estimated/Dead-Reckoning Mode ##
## F = RTK Float Mode                ##
## M = Manual Input Mode             ##
## N = Invalid                       ##
## R = RTK Integer Mode              ##
## S = Simulated Mode                ##
## U = Unsafe                        ##
#######################################

#######################################
###   GPS Quality Indicator Decoder ###
## 0 = No Fix                        ##
## 1 = GPS Fix                       ##
## 2 = Differential (WAAS)           ##
## 3 = PPS Fix                       ##
## 4 = Realtime Kinematic            ##
## 5 = Float RTK                     ##
## 6 = Estimated (Dead-Reckoning)    ##
## 7 = Manual Input Mode             ##
## 8 = Simulated Mode                ##
#######################################

#############################################
### NMEA Sentences Not Used Intentionally ###
## GPGSA = GPS Degree of Precision         ##
## GPGSV = GPS Satellites In View          ##
## GPAP A/B = Autopilot Type A/B           ##
## Most proprietary sentences              ##
#############################################

class serial_nmea(Input):
    def __init__(self):
        self.name = "nmea"
        self.version = 3.01
        self.inputtype = "serial"

        # Setup moving averages to smooth a bit
        self.readings = []
        self.max_samples = 10
        self.readings1 = []
        self.max_samples1 = 20
        self.EOL = 10

    def initInput(self,num, aircraft):
        Input.initInput(self,num, aircraft)  # call parent init Input.
        self.efis_data_port = "/dev/cu.PL2303G-USBtoUART110"
        self.efis_data_baudrate = 9600
        # open serial connection.
        self.ser = serial.Serial(
            port=self.efis_data_port,
            baudrate=self.efis_data_baudrate,
            parity=serial.PARITY_NONE,
            stopbits=serial.STOPBITS_ONE,
            bytesize=serial.EIGHTBITS,
            timeout=None,
        )

        # check for system platform??
        #if sys.platform.startswith('win'):
        #    self.EOL = 10
        #else:
        #    self.EOL = 13
        self.EOL = 13

    # close this input source
    def closeInput(self, aircraft):
        self.ser.close()

    #############################################
    ## Function: readMessage
    def readMessage(self, aircraft):
        airports = airportsdata.load()
        def mean(nums):
            return float(sum(nums)) / max(len(nums), 1)

        if aircraft.errorFoundNeedToExit:
            return aircraft
        try:
            x = 0
            t = self.ser.read(1)
            if len(t) != 0:
                x = ord(t)
            if x == 36:
                msg = self.ser.readline()
                checksum = None
                aircraft.msg_last = msg
                if self.output_logFile != None:
                    Input.addToLog(self,self.output_logFile,bytes([64]))
                    Input.addToLog(self,self.output_logFile,msg)
                msg = msg.rstrip(b'\r\n')
                try:
                    msg = msg.decode('utf-8')
                except:
                    aircraft.nav.msg_bad += 1
                    return aircraft
                try:
                    msg = msg.split('*')
                    checksum = msg[1:]
                    # print(checksum)
                    msg = msg[0]
                    # print(msg)
                    if(self.calcChecksum(msg,checksum)):
                        aircraft.msg_count += 1
                    else:
                        aircraft.gps.msg_bad += 1
                        return aircraft
                    msg = msg.split(",")
                    # print(msg)
                except:
                   msg = msg.split(",")
                   aircraft.msg_count += 1
                sentence = msg[0] # break out sentence ID from the list so we can perform a switch action on it
                match sentence:
                    case "GPRMC": # Recommended Minimum Navigation Info Sentence C
                        utctime = msg[1] # UTC Time in format hhmmss
                        status = msg[2] # GPS Status, A = Acive, V = Warning
                        lat = msg[3] # Latitude in format ddmm.mmmm
                        lathemi = msg[4] # Latitude hemisphere in N/S
                        lon = msg[5] # Longitude in format dddmm.mmmm
                        lonhemi = msg[6] # Longitude hemisphere in E/W
                        gs = msg[7] # GPS Groundspeed
                        truetrack = msg[8] # GPS Track in true heading
                        date = msg[9] # UTC date in ddmmyy
                        magvar = msg[10] # Magnetic variation x.x degrees
                        magvardir = msg[11] # magnetic variation E or W
                        mode = msg[12] # FAA Mode, explained at top of file
                        aircraft.sys_time_string = "%d:%d:%d"%(int(utctime[0:1]),int(utctime[2:3]),int(utctime[4:5]))
                        self.time_stamp_string = aircraft.sys_time_string
                        self.time_stamp_min = int(utctime[2:3])
                        self.time_stamp_sec = int(utctime[4:5])
                        aircraft.gps.LatHemi = lathemi
                        aircraft.gps.LatDeg = int(lat[0:1])
                        aircraft.gps.LatMin = float(lat[2:8])
                        aircraft.gps.LonHemi = lonhemi
                        aircraft.gps.LonDeg = int(lon[0:2])
                        aircraft.gps.LonMin = int(lon[3:9])
                        aircraft.gps.GndSpeed = float(gs)
                        aircraft.groundspeed = float(gs)
                        if(magvardir == "E"):
                            magvar = (magvar - (magvar * 2))
                        aircraft.gndtrack = (truetrack + magvar)
                        aircraft.gps.GPSTrack = aircraft.gndtrack
                        aircraft.gps.Source = "NMEA"
                    case "GPRMB": # Recommended Minimum Navigation Info Sentence B - Note: Destination waypoint is NOT related to the actual flight plan - it is the waypoint currently being navigated to
                        status = msg[1] # A = Active, V = Invalid
                        xtkerror = msg[2] # Crosstrack error NM x.x
                        steerdir = msg[3] # Steer left or right for course? L/R
                        originwpt = msg[4] # Origin Waypoint ID xxxxx
                        destwpt = msg[5] # Destination Waypoint ID xxxxx
                        destlat = msg[6] # Destination waypoint latitude ddmm.mmmm
                        destlathemi = msg[7] # Destination waypoint latitude hemisphere N/S
                        destlon = msg[8] # Destination waypoint longitude dddmm.mmmm
                        destlonhemi = msg[9] # Destination longitude hemisphere E/W
                        distwpt = msg[10] # Distance to destination waypoint xx.x
                        destbrg = msg[11] # Bearing in degrees TRUE to destination waypoint xxx.x
                        wptclosure = msg[12] # Closure rate to destination waypoint xxx.x
                        wptarrival = msg[13] # Arrival alarm for destination waypoint A = arriving, V = not arriving
                        mode = msg[14] # FAA Mode, explained at top of file
                        if(not aircraft.mag_decl == None):
                            aircraft.nav.WPTrack = float(destbrg) + aircraft.mag_decl
                        if(not aircraft.nav.Source == "NMEA GPBWC"):
                            aircraft.nav.WPName = destwpt
                            aircraft.nav.WPDist = float(distwpt)
                    case "GPGGA": # GPS Pos and Altitude
                        utctime = msg[1] # hhmmss
                        lat = msg[2] # Latitude in format ddmm.mmmm
                        lathemi = msg[3] # Latitude hemisphere in N/S
                        lon = msg[4] # Longitude in format dddmm.mmmm
                        lonhemi = msg[5] # Longitude hemisphere in E/W
                        quality = msg[6] # GPS Quality explained at top of file x
                        satnum = msg[7] # Number of satellites used in solution xx
                        hprecision = msg[8] # Horizontal precision in meters x.x
                        gpsalt = msg[9] # GPS Altitude in MSL (geoid) xx.x
                        altunit = msg[10] # GPS Altitude unit of measure X
                        geosep = msg[11] # Geoidal separation between WGS-84 and MSL xx.x
                        geosepunit = msg[12] # unit of measure for geoidal separation X
                        diffage = msg[13] # Age of differential (WAAS) GPS data in seconds x.x
                        diffstation = msg[14] # Station ID of differential reference station (WAAS Station)
                        aircraft.sys_time_string = "%d:%d:%d"%(int(utctime[0:1]),int(utctime[2:3]),int(utctime[4:5]))
                        self.time_stamp_string = aircraft.sys_time_string
                        self.time_stamp_min = int(utctime[2:3])
                        self.time_stamp_sec = int(utctime[4:5])
                        aircraft.gps.LatHemi = lathemi
                        aircraft.gps.LatDeg = int(lat[0:1])
                        aircraft.gps.LatMin = float(lat[2:8])
                        aircraft.gps.LonHemi = lonhemi
                        aircraft.gps.LonDeg = int(lon[0:2])
                        aircraft.gps.LonMin = int(lon[3:9])
                        aircraft.gps.SatsTracked = int(satnum)
                        aircraft.gps.GPSAlt = int(round(float(gpsalt)))
                        if(quality == "1"):
                            aircraft.gps.GPSStatus = 2
                            aircraft.gps.GPSWAAS = 0
                        if(quality == "2"):
                            aircraft.gps.GPSStatus = 3
                            aircraft.gps.GPSWAAS = 1
                    case "GPGLL": # GPS Lat/Long
                        lat = msg[1] # Latitude in format ddmm.mmmm
                        lathemi = msg[2] # Latitude hemisphere in N/S
                        lon = msg[3] # Longitude in format dddmm.mmmm
                        lonhemi = msg[4] # Longitude hemisphere in E/W
                        utctime = msg[5] # hhmmss
                        status = msg[6] # A = Active, V = Invalid
                        mode = msg[7] # FAA Mode, explained at top of file
                        aircraft.sys_time_string = "%d:%d:%d"%(int(utctime[0:1]),int(utctime[2:3]),int(utctime[4:5]))
                        self.time_stamp_string = aircraft.sys_time_string
                        self.time_stamp_min = int(utctime[2:3])
                        self.time_stamp_sec = int(utctime[4:5])
                        aircraft.gps.LatHemi = lathemi
                        aircraft.gps.LatDeg = int(lat[0:1])
                        aircraft.gps.LatMin = float(lat[2:8])
                        aircraft.gps.LonHemi = lonhemi
                        aircraft.gps.LonDeg = int(lon[0:2])
                        aircraft.gps.LonMin = int(lon[3:9])
                        if(mode == "D"):
                            aircraft.gps.GPSWAAS = 1
                        else:
                            aircraft.gps.GPSWAAS = 0
                    case "GPBOD": # Bearing waypoint to waypoint
                        brgtrue = msg[1] # Bearing to waypoint in degrees True xx.x
                        brgmag = msg[3] # bearing to waypoint in degrees Magnetic xx.x
                        nextwpt = msg[5] # Destination (next) waypoint XXXX
                        originwpt = msg[6] # Origin (from) waypoint XXXX
                    case "GPBWC": # bearing and distance to waypoint - Great Circle
                        utctime = msg[1] # hhmmss
                        lat = msg[2] # Latitude in format ddmm.mmmm
                        lathemi = msg[3] # Latitude hemisphere in N/S
                        lon = msg[4] # Longitude in format dddmm.mmmm
                        lonhemi = msg[5] # Longitude hemisphere in E/W
                        brgtrue = msg[6] # bearing to next waypoint degrees true xx.x
                        brgmag = msg[8] # bearing to next waypoint degrees magnetic xx.x 
                        distwpt = msg[10] # Distance to next waypoint in nautical miles xx.x
                        nextwpt = msg[12] # Next waypoint ID XXXX
                        mode = msg[13] # FAA Mode, explained at top of file
                        aircraft.sys_time_string = "%d:%d:%d"%(int(utctime[0:1]),int(utctime[2:3]),int(utctime[4:5]))
                        self.time_stamp_string = aircraft.sys_time_string
                        self.time_stamp_min = int(utctime[2:3])
                        self.time_stamp_sec = int(utctime[4:5])
                        aircraft.gps.LatHemi = lathemi
                        aircraft.gps.LatDeg = int(lat[0:1])
                        aircraft.gps.LatMin = float(lat[2:8])
                        aircraft.gps.LonHemi = lonhemi
                        aircraft.gps.LonDeg = int(lon[0:2])
                        aircraft.gps.LonMin = int(lon[3:9])
                        aircraft.nav.WPName = nextwpt
                        aircraft.nav.WPDist = float(distwpt)
                        aircraft.nav.WPTrack = float(brgmag)
                    case "GPVTG": # GPS Track made good and ground speed, Intentionally omitted KM/H Ground speed
                        coursetrue = msg[1] # GPS Course over ground degrees true xxx.x
                        coursemag = msg[3] # GPS Course over ground degrees magnetic xxx.x
                        gs = msg[5] # GPS Groundspeed, knots xxx.x
                        mode = msg[9] # FAA Mode, explained at top of file
                        aircraft.groundspeed = float(gs)
                        aircraft.gps.GndSpeed = float(gs)
                        aircraft.gps.GndTrack = float(coursemag)
                    case "GPXTE": # GPS Cross-track error, measured
                        status1 = msg[1] # GPS Status, A = Valid, V = Invalid
                        xtkerror = msg[3] # Cross track distance NM xx.x
                        steerdir = msg[4] # Cross track direction to steer, L/R
                        mode = msg[6] # FAA Mode, explained at top of file
                    case "PGRMZ": # Garmin-proprietary altitude in feet. Pressure altitude, or GPS if unavailable
                        alt = msg[1] # Altitude in feet
                        alttype = msg[3] # 2 if Pressure altitude, 3 if GPS altitude
            return aircraft

        except:
            print("NMEA serial exception")
            aircraft.errorFoundNeedToExit = True

        return aircraft




# vi: modeline tabstop=8 expandtab shiftwidth=4 softtabstop=4 syntax=python
