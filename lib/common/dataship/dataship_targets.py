import time
import math
from geographiclib.geodesic import Geodesic
# Target class
class Target(object):
    def __init__(self, callsign):
        self.inputSrcName = None
        self.inputSrcNum = None

        self.callsign = callsign
        self.source = None
        self.aStat = None
        self.type = None
        self.address = None # icao address of ads-b, or meshtastic node id
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
        # 100 = buoy
        # 101 = meshtastic node
        # plus more...
        self.misc = None # 4 bit field
        self.NIC = None # Containment Radius (typically HPL).
        self.NACp = None # encoded using the Estimated Position Uncertainty (typically HFOM).
        # Targets with either a NIC or NACp value that is 4 or lower (HPL >= 1.0 NM, or HFOM >= 0.5 NM) should be depicted using an icon that denotes a degraded target.

        self.lat = None
        self.lon = None
        self.alt = None      # altitude above ground in ft.
        self.track = None  # The resolution is in units of 360/256 degrees (approximately 1.4 degrees).
                        # if misc field tt says track is unknown then track should not be used.
        self.speed = 0 # 0xFFF is reserved to convey that no horizontal velocity information is available.
        self.vspeed = 0 # +/- 32,576 FPM, in units of 64 feet per minute (FPM)
                        # The value 0x800 is reserved to convey that no vertical velocity information is available. The values 0x1FF through 0x7FF and 0x801 through 0xE01 are not used.

        # the following are values that this software calculates per target received.
        self.time = 0        # unix time stamp of time last heard.
        self.dist = None     # distance in miles to target from self.
        self.brng = None     # bearing to target from self
        self.altDiff = None  # difference in alt from self. (in feet MSL)

        self.age = 0

    def get_cat_name(self):
        if self.cat == 1:
            return "Light"
        elif self.cat == 2:
            return "Small"
        elif self.cat == 3:
            return "Large"
        elif self.cat == 4:
            return "High Vortex Large"
        elif self.cat == 5:
            return "Heavy"
        elif self.cat == 7:
            return "Rotor craft"
        elif self.cat == 9:
            return "Glider"
        elif self.cat == 10:
            return "Lighter than air"
        elif self.cat == 11:
            return "Sky diver"
        elif self.cat == 12:
            return "Ultralight"
        elif self.cat == 14:
            return "Drone"
        elif self.cat == 15:
            return "Spacecraft"
        elif self.cat == 100:
            return "Buoy"
        elif self.cat == 101:
            return "Meshtastic Node"
        else:
            return "Unknown"

# def _distance(la1,lo1, la2,lo2):
#     R = 6370 # in KM.
#     lat1 = math.radians(la1)  #insert value
#     lon1 = math.radians(lo1)
#     lon2 = math.radians(lo2)
#     dlon = lon2 - lon1
#     dlat = lat2 - lat1

#     a = math.sin(dlat / 2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2)**2
#     c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
#     distance = (R * c) * 0.6213712 # convert to miles.
#     return distance


#############################################
## Class: TargetData
class TargetData(object):
    def __init__(self):
        self.id = None
        self.name = None

        self.count = 0
        self.src_lat = None     # traffic source lat/lon.. 
        self.src_lon = None
        self.src_alt = None
        self.src_gndtrack = None
        self.src_gndspeed = None
        self.lcl_time_string = ""

        self.targets: list[Target] = [] # list of targets
        self.buoyCount = 0
        self.selected_target = None

        # messages count (number of messages received from this source)
        self.msg_count = 0
        self.msg_last = None
        self.msg_bad = 0

        # meshtastic node id
        self.meshtastic_node_id = None

        # check if we should ignore traffic beyond a certain distance (in miles.)
        self.ignore_traffic_beyond_distance = 30

    def get_selected_target(self) -> Target | None:
        # find the target that has the same address as the selected target.
        for target in self.targets:
            if target.callsign == self.selected_target:
                return target
        return None

    def contains(self, target: Target): # search for callsign
        for x in self.targets:
            if x.callsign == target.callsign:
                return True
        return False

    def remove(self, callsign): # callsign to remove
        for i, t in enumerate(self.targets):
            if t.callsign == callsign:
                del self.targets[i]
                return

    def replace(self,target:Target): # replace target with new one..
        for i, t in enumerate(self.targets):
            if t.callsign == target.callsign:
                self.targets[i] = target
                return

    # add or replace a target.
    def addTarget(self, target:Target):
        target.time = int(time.time()) # always update the time when this target was added/updated..

        # check if the target.callsign is set.. if not then set it to the address.
        if target.callsign == None or target.callsign == "":
            target.callsign = str(target.address)

        # if dist&brng was not calculated... check distance and brng to target. if we know our location..
        # use geographiclib to solve this.
        # https://geographiclib.sourceforge.io/1.46/python/code.html#geographiclib.geodesic.Geodesic.Direct
        # use lat/lon from traffic source. 
        if(self.src_lat != None and self.src_lon != None and target.lat != None and target.lon != None):
            solve = Geodesic.WGS84.Inverse(self.src_lat,self.src_lon,target.lat,target.lon)
            brng = solve['azi1'] # forward azimuth.
            dist = solve['s12'] * 0.0006213712 # convert to miles.
            #print(f"{target.callsign} dist:{dist} brng:{brng}")
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
            # elif(aircraft.PALT != None ):
            #     target.altDiff = target.alt - aircraft.PALT
            # elif(aircraft.gps.GPSAlt != None):
            #     target.altDiff = target.alt - aircraft.gps.GPSAlt

        if(self.contains(target)==False):
            self.targets.append(target)
        else:
            self.replace(target)

        self.count = len(self.targets)

    # get nearest target (if any)
    def getNearestTarget(self,lessThenMilage=15) -> Target | None: 
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
    def cleanUp(self,dataship):
        for i, t in enumerate(self.targets):
            self.targets[i].age = int(time.time() - self.targets[i].time) # track age last time this target was updated.
            # check if it's a buoy we dropped.. if so update it.
            if(self.targets[i].buoyNum != None):
                self.addTarget(self.targets[i]) # update it by adding it again.
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

    def dropTargetBuoy(self,dataship,name=None,speed=None,direction=None,distance=None,alt=None):
        self.buoyCount += 1
        if(name==None): name = "Buoy"+str(self.buoyCount)
        t = Target(name)
        t.buoyNum  = self.buoyCount
        t.address = self.buoyCount
        t.type = 100 # buoy
        t.cat = 100
        if(direction=="ahead"):
            if(distance!=None): distance = distance * 1609.344 # convert to meters.
            else: distance = 1 * 1609.344 # default to 1 mile. (1609.344 meters)
            # check if we have a gpsData object in the dataship object.
            if(len(dataship.gpsData) > 0):
                solve = Geodesic.WGS84.Direct(dataship.gpsData[0].Lat,dataship.gpsData[0].Lon,dataship.gpsData[0].GndTrack,distance)  
                t.lat = solve['lat2']
                t.lon = solve['lon2']
            else:
                print("no gpsData object in dataship")
                return
        else:
            if(len(dataship.gpsData) > 0):
                t.lat = dataship.gpsData[0].Lat
                t.lon = dataship.gpsData[0].Lon
            else:
                print("no gpsData object in dataship")
                return
            
        # if alt was passed in then add it to the altitude of the aircraft.
        if(alt != None): t.alt = dataship.gpsData[0].Alt + alt
        else: t.alt = dataship.gpsData[0].Alt

        # check if mag_head is set.  if not then use the gndTrack from the gpsData object.
        if(len(dataship.imuData) > 0): t.track = dataship.imuData[0].mag_head
        elif(dataship.gpsData[0].GndTrack): t.track = dataship.gpsData[0].GndTrack

        if(speed != None and speed != -1): t.speed = speed
        elif(speed == -1 ):  # if they pass in -1 then use the current speed of aircraft. 
            if(len(dataship.airspeedData) > 0): t.speed = int(dataship.airspeedData[0].IAS)
            elif(dataship.gpsData[0].GndSpeed != None and dataship.gpsData[0].GndSpeed != 0 ): t.speed = int(dataship.gpsData[0].GndSpeed)
            else: t.speed = 0
        else:
            t.speed = 100 # default speed?
        self.addTarget(t)
        pass

