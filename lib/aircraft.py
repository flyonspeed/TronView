#!/usr/bin/env python

from enum import Enum
import time
from geographiclib.geodesic import Geodesic
import math
from . import hud_utils
import inspect
from typing import List, Any

#############################################
## Class: Aircraft
## Store status and converted data from input modules into this class for use by screens.
## Data should be converted into a common format and store here.  Details for what is "standard" format is below.  If input data source is different then it should convert it before saving it here.
##
class Aircraft(object):
    # measurment data formats (static vars)
    MPH = 0
    KNOTS = 1
    METERS = 2
    TEMP_F = 0
    TEMP_C = 1

    def __init__(self):
        self.sys_time_string = None 
        self.pitch = 0.0 # degrees
        self.roll = 0.0  # degrees
        self.ias = 0 # in mph
        self.tas = 0 # mph
        self.alt = None # in Ft
        self.altUseGPS = False
        self.agl = None # ft ( if available )
        self.PALT = None # in ft
        self.BALT = None # in ft
        self.DA = None # in ft
        self.aoa = None # percentage 0 to 100 (if available)
        self.mag_head = 0 # 0 to 360
        self.gndtrack = 0 #TODO: Move to GPSData class?
        self.baro = 0 # inches of mercury
        self.baro_diff = 0
        self.vsi = 0 # ft/min
        self.gndspeed = 0 # mph
        self.oat = 0 # outside air temp in F
        self.vert_G = 0
        self.slip_skid = None # -99 to +99.  (-99 is full right)
        self.turn_rate = 0 # Turn rate in 10th of a degree per second
        self.wind_speed = None
        self.wind_dir = None
        self.norm_wind_dir = None #corrected for aircraft heading for wind direction pointer
        self.mag_decl = None #magnetic declination

        self.gps = GPSData()
        self.engine = EngineData()
        self.nav = NavData()
        self.traffic: TrafficData = TrafficData()
        self.fuel = FuelData()
        self.internal = InteralData()
        self.inputs = [InputDetails(),InputDetails(),InputDetails()]
        self.alerts = []
        self.analog = AnalogData()
        self.imus = []
        self.debug1 = ""
        self.debug2 = ""
        self.debug3 = ""
        self.debug_mode = 0

        self.msg_count = 0
        self.msg_bad = 0
        self.msg_unknown = 0
        self.msg_last = ""
        self.errorFoundNeedToExit = False
        self.textMode = False
        self.editMode = False
        self.show_FPS = False #show screen refresh rate in frames per second for performance tuning
        self.fps = 0

        self.data_format = 0 # 0 is ft/in
        self.data_format_temp = 0 # 0 is F, 1 is C

    # set set measurement to use for data.
    # 0 is US standard. (mph, ft)
    # 1 is knots
    # 2 is metric
    def setDataMeasurementFormat(self,format):
        self.data_format = format

    # get IAS in converted format.
    def get_ias(self):
        if(self.data_format==0):
            return self.ias # mph
        if(self.data_format==1):
            return self.ias * 0.8689758 #knots
        if(self.data_format==2):
            return self.ias * 1.609 #km/h

    # get ground speed in converted format.
    def get_gs(self):
        if(self.gps.GndSpeed != None):
            useSpeed = self.gps.GndSpeed
        else:
            useSpeed = self.gndspeed
        if(self.data_format==0):
            return useSpeed # mph
        if(self.data_format==1):
            return useSpeed * 0.8689758 #knots
        if(self.data_format==2):
            return useSpeed* 1.609 #km/h

    # get true airspeed in converted format.
    def get_tas(self):
        if(self.data_format==0):
            return self.tas # mph
        if(self.data_format==1):
            return self.tas * 0.8689758 #knots
        if(self.data_format==2):
            return self.tas * 1.609 #km/h

    # get speed format description
    def get_speed_description(self):
        if(self.data_format==0):
            return "mph"
        if(self.data_format==1):
            return "kts"
        if(self.data_format==2):
            return "km/h"

    # get ALT in converted format.
    def get_alt(self):
        #use GPS Alt?
        if(self.data_format==0):
            return self.alt # ft
        if(self.data_format==1):
            return self.alt #ft
        if(self.data_format==2):
            return self.alt * 0.3048 #meters

    # get Baro Alt in converted format.
    def get_balt(self):
        if((self.BALT == None and self.gps.GPSAlt != None) or self.altUseGPS == True):
            self.BALT = self.gps.GPSAlt
            self.altUseGPS = True
        elif(self.BALT == None):
            return 0
        if(self.data_format==0):
            return self.BALT # ft
        if(self.data_format==1):
            return self.BALT #ft
        if(self.data_format==2):
            return self.BALT * 0.3048 #meters

    # get distance format description
    def get_distance_description(self):
        if(self.data_format==0):
            return "ft"
        if(self.data_format==1):
            return "ft"
        if(self.data_format==2):
            return "m"

    # get baro in converted format.
    def get_baro(self):
        if(self.data_format==0):
            return self.baro # inHg
        if(self.data_format==1):
            return self.baro #inHg
        if(self.data_format==2):
            return self.baro * 33.863886666667 #mbars

    # get baro format description
    def get_baro_description(self):
        if(self.data_format==0):
            return "in"
        if(self.data_format==1):
            return "in"
        if(self.data_format==2):
            return "mb"

    # get oat in converted format.
    def get_oat(self):
        if(self.data_format_temp==0):
            return self.oat # f
        if(self.data_format_temp==1):
            return  ((self.oat - 32) / 1.8)

    # get temp format description
    def get_temp_description(self):
        if(self.data_format_temp==0):
            return "\xb0f"
        if(self.data_format_temp==1):
            return "\xb0c"

    # get Vertical speed in converted format.
    def get_vsi_string(self):
        if(self.data_format==0):
            v = self.vsi # ft
            d = "fpm"
        elif(self.data_format==1):
            v = self.vsi #ft
            d = "fpm"
        elif(self.data_format==2):
            v = round(self.vsi * 0.00508) #meters per second
            d = "mps"

        if v == 0:
            return " %d %s" % (v,d)
        elif v < 0:
            return "%d %s" % (v,d)
        else:
            return "+%d %s" % (v,d)
    
    # get a list of all fields and functions in the aircraft object
    def _get_all_fields(self, prefix: str = '', force_rebuild: bool = False) -> List[str]:
        """
        Get a list of all fields in the aircraft object.
        
        Args:
            prefix (str): Prefix for nested object fields.
            force_rebuild (bool): If True, rebuild the field list even if cached.
        
        Returns:
            List[str]: List of all fields in the aircraft object.
        """
        if not force_rebuild and hasattr(self, '_all_fields'):
            #print(f"Using cached aircraft field list. len: {len(self._all_fields)}")
            return self._all_fields

        fields = []

        def add_field(name: str, value: Any, current_prefix: str):
            full_name = f"{current_prefix}{name}" if current_prefix else name
            #print(f"Checking field: {full_name} with type: {type(value).__name__}", end=' ')

            if isinstance(value, (str, int, float, bool, list, tuple, dict)):
                fields.append(full_name)
                #print("(added)")
            elif inspect.ismethod(value) or inspect.isfunction(value):
                fields.append(f"{full_name}()")
                #print("(added as method)")
            #elif inspect.isclass(value):
                #print("(skipped class)")
            elif hasattr(value, '__dict__'):
                #print("(recursing)")
                for attr, attr_value in inspect.getmembers(value):
                    if not attr.startswith('_'):
                        add_field(attr, attr_value, f"{full_name}.")
            else:
                fields.append(full_name)
                #print("(added as unknown type)")

        for name, value in inspect.getmembers(self):
            if not name.startswith('_'):
                add_field(name, value, prefix)

        self._all_fields = fields
        #print(f"Built field list with {len(fields)} items")
        return fields


#############################################
## Class: IMU Gyro Input Data 
class IMUData(object):
    def __init__(self):
        self.Name = None
        self.Purpose = None # Aircraft, HeadTracker
        self.x = 0
        self.y = 0
        self.z = 0
        self.Errors = None   

#############################################
## Class: Analog Input Data 
class AnalogData(object):
    def __init__(self):
        self.Name = None
        self.Num = 0
        self.Data = [0,0,0,0,0,0,0,0]


#############################################
## Class: AlertData
class AlertData(object):
    def __init__(self):
        self.Priority = 0 # 0 to 10.  where 10 is top priorty.
        self.Message = None


#############################################
## Class: InteralData
class InteralData(object):
    def __init__(self):
        self.Temp = 0 # internal temp of cpu
        self.LoadAvg = None
        self.MemFree = None
        self.OS = None
        self.OSVer = None
        self.Hardware = None
        self.PythonVer = None
        self.PyGameVer = None

#############################################
## Class: InputDetails
class InputDetails(object):
    def __init__(self):
        self.Name = None # Name of input
        self.Ver = None
        self.InputType = None # Connect Type.. IE serial, wifi
        self.Battery = None
        self.PlayFile = None
        self.RecFile = None
        self.time_stamp = None
        self.time_diff_secs = None

#############################################
## Class: GPSData
class GPSData(object):
    def __init__(self):
        self.Source = None
        self.LatHemi = None # North or South
        self.LatDeg = None
        self.LatMin = None  # x.xxx
        self.LonHemi = None # East or West
        self.LonDeg = None
        self.LonMin = None  # x.xxx
        self.GPSAlt = None  # ft MSL
        self.GndTrack = None # True track from GPS.
        self.GndSpeed = None
        self.EWVelDir = None  # E or W
        self.EWVelmag = None  # x.x m/s
        self.NSVelDir = None  # N or S
        self.NSVelmag = None  # x.x m/s
        self.VVelDir = None  # U or D
        self.VVelmag = None  # x.xx m/s
        self.SatsTracked = None
        self.SatsVisible = None
        self.GPSStatus = None # GPS status. 0=Acquiring, 1=dead reckoning,2=2d fix,3=3dfix,4=2dfix(imu),5=3dfix(imu)
        self.GPSWAAS = None # GPS waas.  0 = no, 1 = yes.
        self.msg_count = 0
        self.msg_last = None
        self.msg_bad = 0
        
    def get_status_string(self):
        if(self.GPSStatus==None): 
            return "NA"
        elif(self.GPSStatus==0):
            return "Acquiring"
        elif(self.GPSStatus==1):
            return "Acquiring" #GPS internal dead reckoning
        elif(self.GPSStatus==2):
            return "2D fix"
        elif(self.GPSStatus==3):
            return "3D fix"
        elif(self.GPSStatus==4):
            return "2D fix+" #2D fix EFIS dead reckoning (IMU)
        elif(self.GPSStatus==5):
            return "3D fix+" #3D fix EFIS dead reckoning (IMU)

#############################################
## Class: NavData
class NavData(object):
    def __init__(self):
        self.NavStatus = ""
        self.HSISource = 0
        self.VNAVSource = 0
        self.SourceDesc = ""
        self.AP = 0
        self.HSINeedle = 0
        self.HSIRoseHeading = 0
        self.HSIHorzDev = 0
        self.HSIVertDev = 0

        self.HeadBug = 0
        self.AltBug = 0
        self.ASIBug = 0
        self.VSBug = 0

        self.WPDist = 0
        self.WPTrack = 0
        self.WPName = None

        self.ILSDev = 0
        self.GSDev = 0
        self.GLSHoriz = 0
        self.GLSVert = 0

        self.msg_count = 0
        self.msg_last = ""


#############################################
## Class: EngineData
class EngineData(object):
    def __init__(self):
        self.NumberOfCylinders = 0
        self.RPM = 0
        self.ManPress = 0
        self.OilPress = 0
        self.OilPress2 = 0
        self.OilTemp = 0
        self.OilTemp2 = 0
        self.CoolantTemp = 0
        self.FuelFlow = 0
        self.FuelPress = 0
        self.EGT = [0,0,0,0,0,0,0,0]
        self.CHT = [0,0,0,0,0,0,0,0]

        self.msg_count = 0
        self.msg_last = ""

#############################################
## Class: FuelData
class FuelData(object):
    def __init__(self):

        self.FuelLevels = [0,0,0,0]

        self.msg_count = 0
        self.msg_last = ""


#############################################
## Class: TrafficData
class TrafficData(object):
    def __init__(self):
        self.count = 0
        self.src_lat = None     # traffic source lat/lon.. 
        self.src_lon = None
        self.src_alt = None
        self.src_gndtrack = None
        self.src_gndspeed = None
        self.lcl_time_string = ""

        self.targets = []
        self.buoyCount = 0

        self.msg_count = 0
        self.msg_last = ""
        self.msg_bad = 0

        # check if we should ignore traffic beyond a certain distance (in miles.)
        self.ignore_traffic_beyond_distance = hud_utils.readConfigInt("Main", "ignore_traffic_beyond_distance", 0)


    def contains(self, target): # search for callsign
        for x in self.targets:
            if x.callsign == target.callsign:
                return True
        return False

    def remove(self, callsign): # callsign to remove
        for i, t in enumerate(self.targets):
            if t.callsign == callsign:
                del self.targets[i]
                return

    def replace(self,target): # replace target with new one..
        for i, t in enumerate(self.targets):
            if t.callsign == target.callsign:
                self.targets[i] = target
                return

    # add or replace a target.
    def addTarget(self, target, aircraft):
        target.time = int(time.time()) # always update the time when this target was added/updated..

        # if dist&brng was not calculated... check distance and brng to target. if we know our location..
        # use geographiclib to solve this.
        # https://geographiclib.sourceforge.io/1.46/python/code.html#geographiclib.geodesic.Geodesic.Direct
        # use lat/lon from traffic source. 
        if(self.src_lat != None and self.src_lon != None and target.lat != 0 and target.lon != 0):
            solve = Geodesic.WGS84.Inverse(self.src_lat,self.src_lon,target.lat,target.lon)
            brng = solve['azi1'] # forward azimuth.
            dist = solve['s12'] * 0.0006213712 # convert to miles.
            if(dist!=dist):
                # NaN. no distance found.  
                pass
            elif(dist<500):
                target.dist = dist
                if(brng<0): target.brng = 360 - (abs(brng)) # convert foward azimuth to bearing to.
                elif(brng!=brng):
                    #its NaN.
                    target.brng = None
                else: target.brng = brng

        # target is beyond distance that we want to listen to.. so bye bye baby!
        if(self.ignore_traffic_beyond_distance != 0):
            if(target.dist == None or target.dist > self.ignore_traffic_beyond_distance):
                # remove it.
                if(self.contains(target)):
                    self.remove(target.callsign)
                self.count = len(self.targets)
                return
            
        # check difference in altitude from self.
        if(target.alt != None):
            if(self.src_alt != None ):  # default to using alt from traffic source...
                target.altDiff = target.alt - self.src_alt
            elif(aircraft.PALT != None ):
                target.altDiff = target.alt - aircraft.PALT
            elif(aircraft.gps.GPSAlt != None):
                target.altDiff = target.alt - aircraft.gps.GPSAlt

        if(self.contains(target)==False):
            self.targets.append(target)
        else:
            self.replace(target)

        self.count = len(self.targets)

    # get nearest target (if any)
    def getNearestTarget(self,lessThenMilage=5):
        nearest = None
        for i, t in enumerate(self.targets):
            if(self.targets[i].dist != None and self.targets[i].dist <= lessThenMilage):
                if(nearest != None):
                    if (self.targets[i].dist < nearest.dist):
                        nearest = self.targets[i]
                else:
                    nearest = self.targets[i]
        
        return nearest

    # go through targets, update,  and remove old ones.
    def cleanUp(self,aircraft):
        for i, t in enumerate(self.targets):
            self.targets[i].age = int(time.time() - self.targets[i].time) # track age last time this target was updated.
            # check if it's a buoy we dropped.. if so update it.
            if(self.targets[i].buoyNum != None):
                self.addTarget(self.targets[i],aircraft) # update it by adding it again.
            # if old target then remove it...    
            if(self.targets[i].age > 100):
                self.targets[i].old = True
                self.remove(self.targets[i].callsign)

    # clear all buoy targets
    def clearBuoyTargets(self):
        numCleared = 0
        for i, t in enumerate(self.targets):
            if(self.targets[i].buoyNum != None):
                numCleared += 1
                del self.targets[i]
        if(numCleared>0): self.clearBuoyTargets()

    def dropTargetBuoy(self,aircraft,name=None,speed=None,direction=None,distance=None,alt=None):
        self.buoyCount += 1
        if(name==None): name = "Buoy"+str(self.buoyCount)
        t = Target(name)
        t.buoyNum  = self.buoyCount
        t.address = self.buoyCount
        t.type = 15 # space craft and aliens!
        t.cat = 1
        if(direction=="ahead"):
            if(distance!=None): distance = distance * 1609.344 # convert to meters.
            else: distance = 1 * 1609.344 # default to 1 mile. (1609.344 meters)
            solve = Geodesic.WGS84.Direct(aircraft.gps.LatDeg,aircraft.gps.LonDeg,aircraft.mag_head,distance)  
            t.lat = solve['lat2']
            t.lon = solve['lon2']
        else:
            t.lat = aircraft.gps.LatDeg
            t.lon = aircraft.gps.LonDeg
        # if alt was passed in then add it to the altitude of the aircraft.
        if(alt != None): t.alt = aircraft.gps.GPSAlt + alt
        else: t.alt = aircraft.gps.GPSAlt

        if(aircraft.mag_head): t.track = aircraft.mag_head
        elif(aircraft.gps.GndTrack): t.track = aircraft.gps.GndTrack
        if(speed != None and speed != -1): t.speed = speed
        elif(speed == -1 ):  # if they pass in -1 then use the current speed of aircraft. 
            if(aircraft.ias != None and aircraft.ias != 0 ): t.speed = int(aircraft.ias)
            elif(aircraft.gps.GndSpeed != None and aircraft.gps.GndSpeed != 0 ): t.speed = int(aircraft.gps.GndSpeed)
            else: t.speed = 0
        else:
            t.speed = 100 # default speed?
        self.addTarget(t,aircraft)
        pass


class Target(object):
    def __init__(self, callsign):
        self.callsign = callsign
        self.aStat = None
        self.type = None
        self.address = None # icao address of ads-b
        self.cat = None # Emitter Category - one of the following values to describe type/weight of aircraft
        self.buoyNum = None
        # 0 = unknown
        # 1 = Light (ICAO) < 15 500 lbs
        # 2 = Small - 15 500 to 75 000 lbs
        # 3 = Large - 75 000 to 300 000 lbs
        # 4 = High Vortex Large (e.g., aircraft 24 such as B757)
        # 5 = Heavy (ICAO) - > 300 000 lbs
        # 7 = Rotor craft
        # 9 = Glider
        # 10 = lighter then air
        # 11 = sky diver
        # 12 = ultra light
        # 14 = drone Unmanned aerial vehicle
        # 15 = space craft and aliens!
        # plus more...
        self.misc = None # 4 bit field
        self.NIC = None # Containment Radius (typically HPL).
        self.NACp = None # encoded using the Estimated Position Uncertainty (typically HFOM).
        # Targets with either a NIC or NACp value that is 4 or lower (HPL >= 1.0 NM, or HFOM >= 0.5 NM) should be depicted using an icon that denotes a degraded target.

        self.lat = 0
        self.lon = 0
        self.alt = None      # altitude above ground in ft.
        self.track = 0  # The resolution is in units of 360/256 degrees (approximately 1.4 degrees).
                        # if misc field tt says track is unknown then track should not be used.
        self.speed = 0 # 0xFFF is reserved to convey that no horizontal velocity information is available.
        self.vspeed = 0 # +/- 32,576 FPM, in units of 64 feet per minute (FPM)
                        # The value 0x800 is reserved to convey that no vertical velocity information is available. The values 0x1FF through 0x7FF and 0x801 through 0xE01 are not used.

        # the following are values that this software calculates per target received.
        self.time = 0        # unix time stamp of time last heard.
        self.dist = None     # distance in miles to target from self.
        self.brng = None     # bearing to target from self
        self.altDiff = None  # difference in alt from self.

# def _distance(la1,lo1, la2,lo2):
#     R = 6370 # in KM.
#     lat1 = math.radians(la1)  #insert value
#     lon1 = math.radians(lo1)
#     lat2 = math.radians(la2)
#     lon2 = math.radians(lo2)
#     dlon = lon2 - lon1
#     dlat = lat2 - lat1

#     a = math.sin(dlat / 2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2)**2
#     c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
#     distance = (R * c) * 0.6213712 # convert to miles.
#     return distance


# vi: modeline tabstop=8 expandtab shiftwidth=4 softtabstop=4 syntax=python
