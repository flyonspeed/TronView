#!/usr/bin/env python

#################################################
# Module: Traffic Scope
# Topher 2021.
# 

from lib.modules._module import Module
from lib import hud_graphics
from lib import hud_utils
from lib import smartdisplay
from lib import aircraft
import pygame
import math
import time
#from osgeo import osr

class trafficscope(Module):
    # called only when object is first created.
    def __init__(self):
        Module.__init__(self)
        self.name = "Traffic Scope"  # set name
        self.show_callsign = False
        self.show_details = False
        self.scope_scale = 0
        self.scope_scale_miles = 10
        self.target_show_lat_lon = hud_utils.readConfigBool("TrafficScope", "target_show_lat_lon", False)
        self.draw_aircraft_icon = hud_utils.readConfigBool("TrafficScope", "draw_aircraft_icon", True)
        self.aircraft_icon_scale = hud_utils.readConfigInt("TrafficScope", "aircraft_icon_scale", 10)
        self.details_offset = hud_utils.readConfigInt("TrafficScope", "details_offset", 5)

    # called once for setup
    def initMod(self, pygamescreen, width=None, height=None):
        if width is None:
            width = 500 # default width
        if height is None:
            height = 500 # default height
        Module.initMod(
            self, pygamescreen, width, height
        )  # call parent init screen.
        print(("Init Mod: %s %dx%d"%(self.name,self.width,self.height)))

        self.xCenter = self.width/2
        self.yCenter = self.height/2

        target_font_size = hud_utils.readConfigInt("TrafficScope", "target_font_size", 16)
        self.font = pygame.font.SysFont("monospace", 12, bold=False)
        self.font_target = pygame.font.SysFont("monospace", target_font_size, bold=False)

        self.setScaleInMiles()


    def buildBaseSurface(self):
        self.surfaceBase = pygame.Surface((self.width, self.height),pygame.SRCALPHA)
        self.surface2= pygame.Surface((self.width, self.height),pygame.SRCALPHA)
        #self.surface.set_alpha(128)
        #self.surface2.set_alpha(128)
        #self.surface.fill((0,0,0))
        self.darkGrey = (40,40,40)

        # fill background black
        hud_graphics.hud_draw_circle(
            self.surfaceBase, 
            (0,0,0,0), 
            (self.xCenter, self.yCenter), 
            int(self.width/2), 
            0,
        )  

        # draw cross lines
        pygame.draw.line(
            self.surfaceBase,
            self.darkGrey,  # color orange
            (0, self.height/2), 
            (self.width,self.height/2),
            1,
        )

        pygame.draw.line(  # 
            self.surfaceBase,
            self.darkGrey,
            (self.width/2,0), 
            (self.width/2, self.height),
            1,
        )
        # draw outter circle
        hud_graphics.hud_draw_circle(
            self.surfaceBase, 
            self.darkGrey, 
            (self.xCenter, self.yCenter), 
            int(self.width/2), 
            1,
        ) 
        hud_graphics.hud_draw_circle(
            self.surfaceBase, 
            self.darkGrey, 
            (self.xCenter, self.yCenter), 
            int(self.width/4), 
            1,
        )

        # show scale.
        labelScale = self.font.render(str(self.scope_scale_miles)+" mi.", False, (200,255,255), (0,0,0))
        labelScale_rect = labelScale.get_rect()
        self.surfaceBase.blit(labelScale, (self.xCenter-labelScale_rect.width, 5))

        # show scale.
        labelScale = self.font.render("%.1f mi."%(self.scope_scale_miles/2), False, (200,255,255), (0,0,0))
        labelScale_rect = labelScale.get_rect()
        self.surfaceBase.blit(labelScale, (self.xCenter-labelScale_rect.width, int(self.height/4)+5 ))


    def setScaleInMiles(self,miles = None ):
        if miles is not None:
            self.scope_scale_miles = miles
        self.scope_scale = (self.width/2) / self.scope_scale_miles 
        self.buildBaseSurface()

    # called every redraw for the mod
    def draw(self, aircraft, smartdisplay, pos):
        # clear the surface
        self.surface2.fill((0,0,0,0))
        # Clear using the base surface.
        self.surface2.blit(self.surfaceBase, (0, 0))

        # Get aircraft heading or ground track
        aircraft_heading = aircraft.mag_head if aircraft.mag_head is not None else aircraft.gps.GndTrack

        def draw_target(t):
            if t.dist is None or t.dist >= 100 or t.brng is None:
                return

            brngToUse = (t.brng - aircraft_heading) % 360
            radianAngle = math.radians(brngToUse - 90)
            d = t.dist * self.scope_scale
            xx = self.xCenter + (d * math.cos(radianAngle))
            yy = self.yCenter + (d * math.sin(radianAngle))

            if self.draw_aircraft_icon:
                direction_of_aircraft = ((t.track or brngToUse) - aircraft_heading) % 360
                t.targetDirection = math.radians(direction_of_aircraft - 90)
                self.drawAircraftIcon(self.surface2, t, xx, yy, self.aircraft_icon_scale)
            else:
                hud_graphics.hud_draw_circle(self.surface2, (0, 255, 129), (xx, yy), 4, 0)

            x_text = xx + self.details_offset
            y_text = yy + self.details_offset

            if self.show_callsign:
                label = self.font_target.render(t.callsign, False, (200,255,255), (0,0,0))
                self.surface2.blit(label, (x_text, y_text))
                label_rect = label.get_rect()
            else:
                label_rect = pygame.Rect(0, 0, 0, 0)

            if self.show_details:
                self.draw_target_details(t, xx, yy, x_text, y_text, label_rect, aircraft_heading)

        # Use map() to apply draw_target to all targets
        list(map(draw_target, filter(lambda t: t.dist is not None and t.dist < 100 and t.brng is not None, aircraft.traffic.targets)))

        self.pygamescreen.blit(self.surface2, pos)

    def draw_target_details(self, t, xx, yy, x_text, y_text, label_rect, aircraft_heading):
        if t.speed is not None and t.speed > -1 and t.track is not None:
            t.targetBrngToUse = (t.track - aircraft_heading) % 360
            radianTargetTrack = math.radians(t.targetBrngToUse - 90)
            d = min(t.speed / 3, 60)
            
            lineX, lineY = xx + d * math.cos(radianTargetTrack), yy + d * math.sin(radianTargetTrack)
            arrowX, arrowY = xx + (d-2) * math.cos(math.radians(t.targetBrngToUse - 82)), yy + (d-2) * math.sin(math.radians(t.targetBrngToUse - 82))
            arrowX2, arrowY2 = xx + (d-2) * math.cos(math.radians(t.targetBrngToUse - 98)), yy + (d-2) * math.sin(math.radians(t.targetBrngToUse - 98))

            pygame.draw.line(self.surface2, (200,255,255), (xx,yy), (lineX, lineY), 1)
            pygame.draw.line(self.surface2, (200,255,255), (lineX,lineY), (arrowX, arrowY), 1)
            pygame.draw.line(self.surface2, (200,255,255), (lineX,lineY), (arrowX2, arrowY2), 1)

            labelSpeed = self.font_target.render(f"{t.speed}mph", False, (200,255,255), (0,0,0))
            labelSpeed_rect = labelSpeed.get_rect()
            self.surface2.blit(labelSpeed, (x_text, y_text + label_rect.height))

            if t.altDiff is not None:
                prefix = "+" if t.altDiff > 0 else ""
                labelAlt = self.font_target.render(f"{prefix}{t.altDiff:,}ft", False, (200,255,255), (0,0,0))
                self.surface2.blit(labelAlt, (x_text + labelSpeed_rect.width + 10, y_text + label_rect.height))

            labelDist = self.font_target.render(f"{t.dist:.1f} mi.", False, (200,255,255), (0,0,0))
            self.surface2.blit(labelDist, (x_text + label_rect.width + 10, y_text))

            # Add time since last update
            if hasattr(t, 'time'):
                time_since_update = int(time.time() - t.time)
                labelUpdate = self.font_target.render(f"{time_since_update}s ago", False, (200,255,255), (0,0,0))
                self.surface2.blit(labelUpdate, (x_text, y_text + label_rect.height + labelSpeed_rect.height))

            if self.target_show_lat_lon:
                y_offset = label_rect.height + labelSpeed_rect.height + (self.font_target.get_height() if hasattr(t, 'time') else 0)
                labelLat = self.font_target.render(f"{t.lat:.6f}", False, (200,255,255), (0,0,0))
                self.surface2.blit(labelLat, (x_text, y_text + y_offset))
                labelLat_rect = labelLat.get_rect()
                labelLon = self.font_target.render(f"{t.lon:.6f}", False, (200,255,255), (0,0,0))
                self.surface2.blit(labelLon, (x_text, y_text + y_offset + labelLat_rect.height))


    # draw aircraft icon based on the type of aircraft
    def drawAircraftIcon(self, surface, target, xx, yy, scale):

        direction_of_aircraft = target.targetDirection
        # types of aircraft
        # 0 = unkown
        # 1 = Light (ICAO) < 15 500 lbs
        # 2 = Small - 15 500 to 75 000 lbs
        # 3 = Large - 75 000 to 300 000 lbs
        # 4 = High Vortex Large (e.g., aircraft 24 such as B757)
        # 5 = Heavy (ICAO) - > 300 000 lbs
        # 7 = Rotorcraft
        # 9 = Glider
        # 10 = lighter then air
        # 11 = sky diver
        # 12 = ultra light
        # 14 = drone Unmanned aerial vehicle
        # 15 = space craft and aliens!
        nose = (xx + scale * math.cos(direction_of_aircraft), 
            yy + scale * math.sin(direction_of_aircraft))
        tail = (xx - scale * math.cos(direction_of_aircraft), 
                yy - scale * math.sin(direction_of_aircraft))
                
        # if type is 0 through 5 then draw a simple aircraft icon
        if(target.type >= 0 and target.type <= 5):
            # Calculate points for the target aircraft outline

            wing_left = (xx + scale * 0.7 * math.cos(direction_of_aircraft + math.pi/2), 
                            yy + scale * 0.7 * math.sin(direction_of_aircraft + math.pi/2))
            wing_right = (xx + scale * 0.7 * math.cos(direction_of_aircraft - math.pi/2), 
                            yy + scale * 0.7 * math.sin(direction_of_aircraft - math.pi/2))
            elevator_left = (tail[0] + scale * 0.3 * math.cos(direction_of_aircraft + math.pi/2), 
                                tail[1] + scale * 0.3 * math.sin(direction_of_aircraft + math.pi/2))
            elevator_right = (tail[0] + scale * 0.3 * math.cos(direction_of_aircraft - math.pi/2), 
                                tail[1] + scale * 0.3 * math.sin(direction_of_aircraft - math.pi/2))

            # Draw the aircraft outline
            pygame.draw.line(surface, (0, 255, 129), nose, tail, 1)
            pygame.draw.line(surface, (0, 255, 129), wing_left, wing_right, 1)
            pygame.draw.line(surface, (0, 255, 129), elevator_left, elevator_right, 1)
        elif(target.type == 7):
            # draw a helicopter. which will look like a X with a line through it. use nose and tail to draw it.
            # calculate the angle of the helicopter blades.
            # calculate the angle of the helicopter blades.
            blade_angle = math.atan2(tail[1] - nose[1], tail[0] - nose[0])
            # calculate the length of the blades.
            blade_length = scale * 0.7
            # calculate the position of the blades.
            blade_pos = (nose[0] + blade_length * math.cos(blade_angle), 
                            nose[1] + blade_length * math.sin(blade_angle))
            # also draw a light circle around the helicopter.
            pygame.draw.circle(surface, (0, 255, 129), tail, scale * 0.2, 1)
            pygame.draw.circle(surface, (0, 255, 129), blade_pos, scale * 0.8, 1)

            # draw the blades.
            pygame.draw.line(surface, (0, 255, 129), nose, blade_pos, 1)
            pygame.draw.line(surface, (0, 255, 129), tail, blade_pos, 1)
            # draw a line through the middle of the helicopter.
            pygame.draw.line(surface, (0, 255, 129), nose, tail, 1)
        else:
            # Draw a smiley face as the default
            # Main circle (face)
            pygame.draw.circle(surface, (70,150,255), (xx, yy), scale, 1)
            
            # Eyes
            eye_offset = scale * 0.3
            eye_size = max(1, int(scale * 0.15))
            pygame.draw.circle(surface, (70,150,255), (int(xx - eye_offset), int(yy - eye_offset)), eye_size, 0)
            pygame.draw.circle(surface, (70,150,255), (int(xx + eye_offset), int(yy - eye_offset)), eye_size, 0)
            
            # Smile
            smile_rect = pygame.Rect(xx - scale * 0.5, yy, scale, scale * 0.5)
            pygame.draw.arc(surface, (70,150,255), smile_rect, math.pi * 0.1, math.pi * 0.9, 1)



    # called before screen draw.  To clear the screen to your favorite color.
    def clear(self):
        #self.ahrs_bg.fill((0, 0, 0))  # clear screen
        #print("clear")
        pass
    
    # return a dict of objects that are used to configure the module.
    def get_module_options(self):

        # each item in the dict represents a configuration option.  These are variable in this class that are exposed to the user to edit.
        return {
            "show_callsign": {
                "type": "bool",
                "default": False,
                "label": "Show Callsign",
                "description": "Show the callsign of the targets on the scope."
            },
            "show_details": {
                "type": "bool",
                "default": False,
                "label": "Show Details",
                "description": "Show the details of the targets on the scope."
            },
            "details_offset": {
                "type": "int",
                "default": self.details_offset,
                "min": 0,
                "max": 20,
                "label": "Details Offset",
                "description": "Set the offset of the details from the target in pixels."
            },
            "target_show_lat_lon": {
                "type": "bool",
                "default": False,
                "label": "Show Lat/Lon",
                "description": "Show the latitude and longitude of the targets on the scope."
            },
            "scope_scale_miles": {
                "type": "int",
                "default": self.scope_scale_miles,
                "min": 1,
                "max": 50,
                "label": "Scope Scale",
                "description": "Set the scale of the scope in miles.",
                "post_change_function": "setScaleInMiles"
            },
            "draw_aircraft_icon": {
                "type": "bool",
                "default": True,
                "label": "Draw Aircraft Icon",
                "description": "Draw a simple aircraft outline instead of a dot for targets."
            },
            "aircraft_icon_scale": {
                "type": "int",
                "default": 10,
                "min": 10,
                "max": 30,
                "label": "Aircraft Icon Scale",
                "description": "Set the scale of the aircraft icon."
            },
        }

    # handle events
    def processEvent(self,event,aircraft,smartdisplay):
        if(event.type=="modechange"):
            if(event.key=="traffic"):
                if(event.value==2):
                    self.show_callsign = True
                    print("TrafficScope showing callsigns. 5mi.")
                    self.setScaleInMiles(5)
                    self.show_details = True
                elif(event.value==3):
                    print("TrafficScope showing callsigns & details. 2mi.")
                    self.show_details = True
                    self.show_callsign = True
                    self.setScaleInMiles(2)
                else:
                    self.setScaleInMiles(10)
                    self.show_callsign = False
                    self.show_details = False

        pass


    # def draw_triangle(screen,color,center, radius, mouse_position):
    #     # calculate the normalized vector pointing from center to mouse_position
    #     length = math.hypot(mouse_position[0] - center[0], mouse_position[1] - center[1])
    #     # (note we only need the x component since y falls 
    #     # out of the dot product, so we won't bother to calculate y)
    #     angle_vector_x = (mouse_position[0] - center[0]) / length

    #     # calculate the angle between that vector and the x axis vector (aka <1,0> or i)
    #     angle = math.acos(angle_vector_x)

    #     # list of un-rotated point locations
    #     t = [0, (3 * math.pi / 4), (5 * math.pi / 4)]

    #     # apply the circle formula
    #     x1 = center[0] + radius * math.cos(t[0] + angle)
    #     y1 = center[1] + radius * math.sin(t[0] + angle)

    #     x2 = center[0] + radius * math.cos(t[1] + angle)
    #     y2 = center[1] + radius * math.sin(t[1] + angle)

    #     x3 = center[0] + radius * math.cos(t[2] + angle)
    #     y3 = center[1] + radius * math.sin(t[2] + angle)

    #     pygame.draw.polygon(screen, color, [(x1,y1),(x2,y2),(x3,y3)], 1)

    #     return


'''
        (boxLat1,boxLon2),(boxLat2,boxLon2) = getLatLonAreaAroundPoint(aircraft.gps.LatDeg, aircraft.gps.LonDeg, 50)

        # Calculate global X and Y for top-left reference point        
        p0 = referencePoint(0, 0, boxLat1, boxLon2)
        # Calculate global X and Y for bottom-right reference point
        p1 = referencePoint(self.width, self.height, boxLat2, boxLon2) 

        pos = latlngToScreenXY(p0,p1,52.525607, 13.404572);
'''

'''
        #draw center circle.
        hud_graphics.hud_draw_circle(
            newSurface, 
            ( 0, 155, 79), 
            (self.xCenter, self.yCenter), 
            50, 
            8,
        )
'''


    
'''
class referencePoint:
    def __init__(self, scrX, scrY, lat, lng):
        self.scrX = scrX
        self.scrY = scrY
        self.lat = lat
        self.lng = lng
        self.pos = latlngToGlobalXY(lat,lng)


# This function converts lat and lng coordinates to GLOBAL X and Y positions
def latlngToGlobalXY(p0,p1,lat, lng):
    radius = 6371    #Earth Radius in KM
    # Calculates x based on cos of average of the latitudes
    x = radius*lng*math.cos((p0.lat + p1.lat)/2)
    # Calculates y based on latitude
    y = radius*lat
    return {'x': x, 'y': y}


# This function converts lat and lng coordinates to SCREEN X and Y positions
def latlngToScreenXY(p0,p1, lat, lng):
    # Calculate global X and Y for projection point
    pos = latlngToGlobalXY(p0,p1,lat, lng)
    # Calculate the percentage of Global X position in relation to total global width
    perX = ((pos['x']-p0.pos['x'])/(p1.pos['x'] - p0.pos['x']))
    # Calculate the percentage of Global Y position in relation to total global height
    perY = ((pos['y']-p0.pos['y'])/(p1.pos['y'] - p0.pos['y']))

    # Returns the screen position based on reference points
    return {
        'x': p0.scrX + (p1.scrX - p0.scrX)*perX,
        'y': p0.scrY + (p1.scrY - p0.scrY)*perY
    }



# get square milage around a lat lon point
def getLatLonAreaAroundPoint(lat,lon,distanceMile):
    coords =  (lat, lon)
    # convert point to albers so we can add a distance to the point.
    albersXY = convertCoords(coords, 4326, 5070) # 4326 is WGS84 http://spatialreference.org/ref/epsg/4326/ ,  5070 is albers https://epsg.io/5070

    # add subtract distance after in albers format
    distanceKM = distanceMile * 1609.344
    albersXMax = albersXY[0] + distanceKM
    albersYMax = albersXY[1] + distanceKM
    albersXMin = albersXY[0] - distanceKM
    albersYMin = albersXY[1] - distanceKM

    # convert back to WGS84
    newlonlatMax = convertCoords((albersXMax,albersYMax), 5070, 4326) 
    newlonlatMin = convertCoords((albersXMin,albersYMin), 5070, 4326) 

    return(newlonlatMin,newlonlatMax)

def convertCoords(xy, src='', targ=''):
    srcproj = osr.SpatialReference()
    srcproj.ImportFromEPSG(src)
    targproj = osr.SpatialReference()
    if isinstance(targ, str):
        targproj.ImportFromProj4(targ)
    else:
        targproj.ImportFromEPSG(targ)
    transform = osr.CoordinateTransformation(srcproj, targproj)

    pt = ogr.Geometry(ogr.wkbPoint)
    pt.AddPoint(xy[0], xy[1])
    pt.Transform(transform)

    return([pt.GetX(), pt.GetY()])
'''

# vi: modeline tabstop=8 expandtab shiftwidth=4 softtabstop=4 syntax=python
