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
#from osgeo import osr

class TrafficScope(Module):
    # called only when object is first created.
    def __init__(self):
        Module.__init__(self)
        self.name = "Traffic Scope"  # set name

    # called once for setup
    def initMod(self, pygamescreen, width, height):
        Module.initMod(
            self, pygamescreen, width, height
        )  # call parent init screen.
        print(("Init Mod: %s %dx%d"%(self.name,self.width,self.height)))

        self.show_callsign = False
        self.show_details = False
        self.scope_scale = 0
        self.scope_scale_miles = 0

        self.xCenter = self.width/2
        self.yCenter = self.height/2

        target_font_size = hud_utils.readConfigInt("TrafficScope", "target_font_size", 16)
        self.font = pygame.font.SysFont("monospace", 12, bold=False)
        self.font_target = pygame.font.SysFont("monospace", target_font_size, bold=False)

        self.setScaleInMiles(10)


    def buildBaseSurface(self):
        self.surface = pygame.Surface((self.width, self.height))
        self.surface2= pygame.Surface((self.width, self.height),pygame.SRCALPHA)
        #self.surface.set_alpha(128)
        #self.surface2.set_alpha(128)
        #self.surface.fill((0,0,0))
        self.darkGrey = (40,40,40)

        # fill background black
        hud_graphics.hud_draw_circle(
            self.surface, 
            (0,0,0), 
            (self.xCenter, self.yCenter), 
            int(self.width/2), 
            0,
        )  

        # draw cross lines
        pygame.draw.line(
            self.surface,
            self.darkGrey,  # color orange
            (0, self.height/2), 
            (self.width,self.height/2),
            1,
        )

        pygame.draw.line(  # 
            self.surface,
            self.darkGrey,
            (self.width/2,0), 
            (self.width/2, self.height),
            1,
        )
        # draw outter circle
        hud_graphics.hud_draw_circle(
            self.surface, 
            self.darkGrey, 
            (self.xCenter, self.yCenter), 
            int(self.width/2), 
            1,
        ) 
        hud_graphics.hud_draw_circle(
            self.surface, 
            self.darkGrey, 
            (self.xCenter, self.yCenter), 
            int(self.width/4), 
            1,
        )

        # show scale.
        labelScale = self.font.render(str(self.scope_scale_miles)+" mi.", False, (200,255,255), (0,0,0))
        labelScale_rect = labelScale.get_rect()
        self.surface.blit(labelScale, (self.xCenter-labelScale_rect.width, 5))

        # show scale.
        labelScale = self.font.render("%.1f mi."%(self.scope_scale_miles/2), False, (200,255,255), (0,0,0))
        labelScale_rect = labelScale.get_rect()
        self.surface.blit(labelScale, (self.xCenter-labelScale_rect.width, int(self.height/4)+5 ))


    def setScaleInMiles(self,miles):
        self.scope_scale = (self.width/2) / miles 
        #self.scope_scale = miles * 16
        self.scope_scale_miles = miles
        self.buildBaseSurface()

    # called every redraw for the mod
    def draw(self, aircraft, smartdisplay, pos):

        # Clear using the base surface.
        self.surface2.blit(self.surface, (0, 0))

        # go through all targets and draw them
        for i, t in enumerate(aircraft.traffic.targets):
            if(t.dist!=None and t.dist<100 and t.brng !=None):
                brngToUse = t.brng
                # adjust bearing to target based on the aircraft heading.
                if(aircraft.mag_head != None):
                    brngToUse = brngToUse - aircraft.mag_head
                elif(aircraft.gps.GndTrack != None): # else use gps ground track if we have it.
                    brngToUse = brngToUse - aircraft.gps.GndTrack
                if(brngToUse<0): brngToUse = 360 - abs(brngToUse)

                radianAngle = (brngToUse-90) * math.pi / 180 # convert to radians
                d = t.dist * self.scope_scale
                xx = self.xCenter + (d * math.cos(radianAngle))
                yy = self.yCenter + (d * math.sin(radianAngle))
                hud_graphics.hud_draw_circle(
                    self.surface2, 
                    ( 0, 255, 129), 
                    (xx, yy), 
                    4, 
                    0,
                )
                # show callsign?
                if(self.show_callsign==True):
                    label = self.self.font_target.render(t.callsign, False, (200,255,255), (0,0,0))
                    label_rect = label.get_rect()
                    self.surface2.blit(label, (xx, yy))
                # show details?
                if(self.show_details==True):
                    if(t.speed != None and t.speed > -1 and t.track != None):
                        # generate line in direct aircraft is flying..
                        radianTargetTrack = (t.track-90) * math.pi / 180
                        radianArrowPt = (t.track-82) * math.pi / 180
                        radianArrowPt2 = (t.track-98) * math.pi / 180
                        d = t.speed / 3
                        #print("line speed:"+str(d))
                        lineX = xx + (d * math.cos(radianTargetTrack))
                        lineY = yy + (d * math.sin(radianTargetTrack))
                        arrowX = xx + ((d-2) * math.cos(radianArrowPt))
                        arrowY = yy + ((d-2) * math.sin(radianArrowPt))
                        arrowX2 = xx + ((d-2) * math.cos(radianArrowPt2))
                        arrowY2 = yy + ((d-2) * math.sin(radianArrowPt2))
                        # draw speed line
                        pygame.draw.line(  # 
                            self.surface2,
                            (200,255,255),
                            (xx,yy), 
                            (lineX, lineY),
                            1,
                        )
                        #draw_triangle(self.surface2,(200,255,255),(lineX,lineY), 4, (xx,yy))

                        pygame.draw.line(  # arrow head 1
                           self.surface2,
                           (200,255,255),
                           (lineX,lineY),
                           (arrowX, arrowY),
                           1,
                        )
                        pygame.draw.line(  # arrow head 2
                           self.surface2,
                           (200,255,255),
                           (lineX,lineY),
                           (arrowX2, arrowY2),
                           1,
                        )
                        # show speed info
                        labelSpeed = self.self.font_target.render(str(t.speed)+"mph", False, (200,255,255), (0,0,0))
                        labelSpeed_rect = labelSpeed.get_rect()
                        self.surface2.blit(labelSpeed, (xx, yy+label_rect.height))
                        # show altitude diff
                        if(t.altDiff != None):
                            if(t.altDiff>0): prefix = "+"
                            else: prefix = ""
                            labelAlt = self.self.font_target.render(prefix+'{:,}ft'.format(t.altDiff), False, (200,255,255), (0,0,0))
                            self.surface2.blit(labelAlt, (xx+labelSpeed_rect.width+10, yy+label_rect.height))
                        # distance
                        labelDist = self.self.font_target.render("%.1f mi."%(t.dist), False, (200,255,255), (0,0,0))
                        self.surface2.blit(labelDist, (xx+label_rect.width+10, yy))

        self.pygamescreen.blit(self.surface2, pos)



    # called before screen draw.  To clear the screen to your favorite color.
    def clear(self):
        #self.ahrs_bg.fill((0, 0, 0))  # clear screen
        #print("clear")
        pass

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
