#!/usr/bin/env python

#################################################
# Module: Hud Horizon
# Topher 2021.
# Adapted from F18 HUD Screen code by Brian Chesteen.

from lib.modules._module import Module
from lib import hud_graphics
from lib import hud_utils
from lib import smartdisplay
from lib import aircraft
import pygame
import math


class horizon_v2(Module):
    # called only when object is first created.
    def __init__(self):
        Module.__init__(self)
        self.name = "HUD Horizon V2"  # set name
        self.flight_path_color = (255, 0, 255)  # Default color, can be changed via settings

    # called once for setup
    def initMod(self, pygamescreen, width=None, height=None):
        if width is None:
            width = pygamescreen.get_width() # default width
        if height is None:
            height = 640 # default height
        Module.initMod(
            self, pygamescreen, width, height
        )  # call parent init screen.
        print(("Init Mod: %s %dx%d"%(self.name,self.width,self.height)))
        target_font_size = hud_utils.readConfigInt("HUD", "target_font_size", 40)

        # fonts
        self.font = pygame.font.SysFont(None, 30)
        self.font_target = pygame.font.SysFont(None, target_font_size)

        self.surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        self.ahrs_bg_width = self.surface.get_width()
        self.ahrs_bg_height = self.surface.get_height()
        self.ahrs_bg_center = (self.ahrs_bg_width / 2 + 160, self.ahrs_bg_height / 2)
        self.MainColor = (0, 255, 0)  # main color of hud graphics
        self.line_thickness = hud_utils.readConfigInt("HUD", "line_thickness", 2)
        self.ahrs_line_deg = hud_utils.readConfigInt("HUD", "vertical_degrees", 5)
        self.pxy_div = hud_utils.readConfigInt("HUD", "vertical_pixels_per_degree", 30)  # Y axis number of pixels per degree divisor
        self.y_offset = hud_utils.readConfigInt("HUD", "Horizon_Offset", 0)  #  Horizon/Waterline Pixel Offset from HUD Center Neg Numb moves Up, Default=0

        self.line_mode = hud_utils.readConfigInt("HUD", "line_mode", 1)
        self.caged_mode = 1 # default on
        self.center_circle_mode = hud_utils.readConfigInt("HUD", "center_circle", 4)


        # sampling for flight path.
        self.readings = []  # Setup moving averages to smooth a bit
        self.max_samples = 30 # FPM smoothing
        self.readings1 = []  # Setup moving averages to smooth a bit
        self.max_samples1 = 30 # Caged FPM smoothing

        self.x_offset = 0

    #############################################
    ## Function: generateHudReferenceLineArray
    ## create array of horz lines based on pitch, roll, etc.
    def generateHudReferenceLineArray(
        self,screen_width, screen_height, ahrs_center, pxy_div, pitch=0, roll=0, deg_ref=0, line_mode=1,
    ):

        if line_mode == 1:
            if deg_ref == 0:
                length = screen_width * 0.9
            elif (deg_ref % 10) == 0:
                length = screen_width * 0.49
            elif (deg_ref % 5) == 0:
                length = screen_width * 0.25
            else:
                length = screen_width * 0.10
        else:
            if deg_ref == 0:
                length = screen_width * 0.5
            elif (deg_ref % 10) == 0:
                length = screen_width * 0.25
            elif (deg_ref % 5) == 0:
                length = screen_width * 0.11
            else:
                length = screen_width * 0.5

        ahrs_center_x, ahrs_center_y = ahrs_center
        px_per_deg_y = screen_height / pxy_div
        pitch_offset = px_per_deg_y * (-pitch + deg_ref)

        center_x = ahrs_center_x - (pitch_offset * math.cos(math.radians(90 - roll)))
        center_y = ahrs_center_y - (pitch_offset * math.sin(math.radians(90 - roll)))

        x_len = length * math.cos(math.radians(roll))
        y_len = length * math.sin(math.radians(roll))

        start_x = center_x - (x_len / 2)
        end_x = center_x + (x_len / 2)
        start_y = center_y + (y_len / 2)
        end_y = center_y - (y_len / 2)

        xRot = center_x + math.cos(math.radians(-10)) * (start_x - center_x) - math.sin(math.radians(-10)) * (start_y - center_y)
        yRot = center_y + math.sin(math.radians(-10)) * (start_x - center_x) + math.cos(math.radians(-10)) * (start_y - center_y)
        xRot1 = center_x + math.cos(math.radians(+10)) * (end_x - center_x) - math.sin(math.radians(+10)) * (end_y - center_y)
        yRot1 = center_y + math.sin(math.radians(+10)) * (end_x - center_x) + math.cos(math.radians(+10)) * (end_y - center_y)

        xRot2 = center_x + math.cos(math.radians(-10)) * (end_x - center_x) - math.sin(math.radians(-10)) * (end_y - center_y)
        yRot2 = center_y + math.sin(math.radians(-10)) * (end_x - center_x) + math.cos(math.radians(-10)) * (end_y - center_y)
        xRot3 = center_x + math.cos(math.radians(+10)) * (start_x - center_x) - math.sin(math.radians(+10)) * (start_y - center_y)
        yRot3 = center_y + math.sin(math.radians(+10)) * (start_x - center_x) + math.cos(math.radians(+10)) * (start_y - center_y)

        return [[xRot, yRot],[start_x, start_y],[end_x, end_y],[xRot1, yRot1],[xRot2, yRot2],[xRot3, yRot3]]


    #############################################
    ## Function: draw_dashed_line
    def draw_dashed_line(self,surf, color, start_pos, end_pos, width=1, dash_length=10):
        origin = Point(start_pos)
        target = Point(end_pos)
        displacement = target - origin
        length = len(displacement)
        slope = Point((displacement.x / length, displacement.y/length))

        for index in range(0, length // dash_length, 2):
            start = origin + (slope * index * dash_length)
            end = origin + (slope * (index + 1) * dash_length)
            pygame.draw.line(surf, color, start.get(), end.get(), width)

    def draw_circle(self,surface,color,center,radius,width):
        pygame.draw.circle(
            surface,
            color,
            (int(center[0]),int(center[1])),
            radius,
            width,
        )

    #############################################
    ## Function draw horz lines
    def draw_horz_lines(
        self,
        width,
        height,
        ahrs_center,
        ahrs_line_deg,
        aircraft,
        color,
        line_thickness,
        line_mode,
        font,
        pxy_div,
        pos
    ):
        # x_offset, y_offset = pos
        # center_x = x_offset + width // 2
        # center_y = y_offset + height // 2

        # Draw lines centered on the screen
        for l in range(-60, 61, ahrs_line_deg):
            line_coords = self.generateHudReferenceLineArray(
                width,
                height,
                ahrs_center,  # Use the new center point
                pxy_div,
                pitch=aircraft.pitch,
                roll=aircraft.roll,
                deg_ref=l,
                line_mode=line_mode,
            )

            # No need to adjust coordinates here, as we've centered them in generateHudReferenceLineArray

            if abs(l) > 45:
                if l % 5 == 0 and l % 10 != 0:
                    continue

            # Draw lines (already centered)
            if l < 0:
                self.draw_dashed_line(
                    self.surface,
                    color,
                    line_coords[1],
                    line_coords[2],
                    width=line_thickness,
                    dash_length=5,
                )
                pygame.draw.lines(self.surface,
                    color,
                    False,
                    (line_coords[2],
                    line_coords[4]),
                    line_thickness
                )
                pygame.draw.lines(self.surface,
                    color,
                    False,
                    (line_coords[1],
                    line_coords[5]),
                    line_thickness
                )
            else:
                pygame.draw.lines(
                    self.surface,
                    color,
                    False,
                    (line_coords[0],
                    line_coords[1],
                    line_coords[2],
                    line_coords[3]),
                    line_thickness
                )

            # Draw degree text (already centered)
            if l != 0 and l % 5 == 0:
                text = font.render(str(l), False, color)
                text_width, text_height = text.get_size()
                left = int(line_coords[1][0]) - (text_width + int(width / 100))
                top = int(line_coords[1][1]) - text_height / 2
                self.surface.blit(text, (left, top))


    def draw_center(self,smartdisplay, x_offset, y_offset):
        center_x = x_offset + self.width // 2
        center_y = y_offset + self.height // 2

        if self.center_circle_mode == 1:
            pygame.draw.circle(
                self.surface,
                self.MainColor,
                (center_x, center_y),
                3,
                1,
            )
        elif self.center_circle_mode == 2:
            pygame.draw.circle(
                self.surface,
                self.MainColor,
                (center_x, center_y),
                15,
                1,
            )
        # draw center + Gun Cross
        elif self.center_circle_mode == 3:
            pygame.draw.circle(
                self.surface,
                self.MainColor,
                (center_x, center_y),
                50,
                1,
            )
        # draw water line center.
        elif self.center_circle_mode == 5:
            pygame.draw.line(
                self.surface,
                self.MainColor,
                [center_x - 10, center_y + 20],
                [center_x, center_y],
                3,
            )
            pygame.draw.line(
                self.surface,
                self.MainColor,
                [center_x - 10, center_y + 20],
                [center_x - 20, center_y],
                3,
            )
            pygame.draw.line(
                self.surface,
                self.MainColor,
                [center_x - 35, center_y],
                [center_x - 20, center_y],
                3,
            )
            pygame.draw.line(
                self.surface,
                self.MainColor,
                [center_x + 10, center_y + 20],
                [center_x, center_y],
                3,
            )
            pygame.draw.line(
                smartdisplay.pygamescreen,
                self.MainColor,
                [center_x + 10, center_y + 20],
                [center_x + 20, center_y],
                3,
            )
            pygame.draw.line(
                smartdisplay.pygamescreen,
                self.MainColor,
                [center_x + 35, center_y],
                [center_x + 20, center_y],
                3,
            )

    def draw_flight_path(self,aircraft,smartdisplay, x_offset, y_offset):
        def mean(nums):
            return int(sum(nums)) / max(len(nums), 1)

        # flight path indicator  Default Caged Mode
        if self.caged_mode == 1:
            fpv_x = 0.0
        else:  #  changed the  "- (aircraft.turn_rate * 5" to a "+ (aircraft.turn_rate * 5" 
            fpv_x = ((((aircraft.mag_head - aircraft.gndtrack) + 180) % 360) - 180) * 1.5  + (
                aircraft.turn_rate * 5
            )
            self.readings.append(fpv_x)
            fpv_x = mean(self.readings)  # Moving average to smooth a bit
            if len(self.readings) == self.max_samples:
                self.readings.pop(0)
        gfpv_x = ((((aircraft.mag_head - aircraft.gndtrack) + 180) % 360) - 180) * 1.5  + (
            aircraft.turn_rate * 5
        )
        self.readings1.append(gfpv_x)
        gfpv_x = mean(self.readings1)  # Moving average to smooth a bit
        if len(self.readings1) == self.max_samples1:
            self.readings1.pop(0)

        center_x = self.width // 2
        center_y = self.height // 2

        self.draw_circle(
            self.surface,
            self.flight_path_color,  # Use flight_path_color instead of hardcoded color
            (
                center_x - (int(fpv_x) * 5),
                center_y - (aircraft.vsi / 2),
            ),
            15,
            4,
        )
        
        pygame.draw.line(
            self.surface,
            self.flight_path_color,  # Use flight_path_color
            [
                center_x - (int(fpv_x) * 5) - 15,
                center_y - (aircraft.vsi / 2),
            ],
            [
                center_x - (int(fpv_x) * 5) - 30,
                center_y - (aircraft.vsi / 2),
            ],
            2,
        )
        pygame.draw.line(
            self.surface,
            self.flight_path_color,  # Use flight_path_color
            [
                center_x - (int(fpv_x) * 5) + 15,
                center_y - (aircraft.vsi / 2),
            ],
            [
                center_x - (int(fpv_x) * 5) + 30,
                center_y - (aircraft.vsi / 2),
            ],
            2,
        )
        pygame.draw.line(
            self.surface,
            self.flight_path_color,  # Use flight_path_color
            [
                center_x - (int(fpv_x) * 5),
                center_y - (aircraft.vsi / 2) - 15,
            ],
            [
                center_x - (int(fpv_x) * 5),
                center_y - (aircraft.vsi / 2) - 30,
            ],
            2,
        )
        if self.caged_mode == 1:
            pygame.draw.line(
                self.surface,
                self.flight_path_color,  # Use flight_path_color
                [
                    center_x - (int(gfpv_x) * 5) - 15,
                    center_y - (aircraft.vsi / 2),
                ],
                [
                    center_x - (int(gfpv_x) * 5) - 30,
                    center_y - (aircraft.vsi / 2),
                ],
                2,
            )
            pygame.draw.line(
                self.surface,
                self.flight_path_color,  # Use flight_path_color
                [
                    center_x - (int(gfpv_x) * 5) + 15,
                    center_y - (aircraft.vsi / 2),
                ],
                [
                    center_x - (int(gfpv_x) * 5) + 30,
                    center_y - (aircraft.vsi / 2),
                ],
                2,
            )
            pygame.draw.line(
                self.surface,
                self.flight_path_color,  # Use flight_path_color
                [
                    center_x - (int(gfpv_x) * 5),
                    center_y - (aircraft.vsi / 2) - 15,
                ],
                [
                    center_x - (int(gfpv_x) * 5),
                    center_y - (aircraft.vsi / 2) - 30,
                ],
                2,
            )

            aircraft.flightPathMarker_x = fpv_x # save to aircraft object for other modules to use.


    # called every redraw for the mod
    def draw(self, aircraft, smartdisplay, pos=(0, 0)):
        x, y = pos
        
        # Clear the surface before drawing
        self.surface.fill((0, 0, 0, 0 ))
        
        # Draw horizon lines starting at the specified position
        self.draw_horz_lines(
            self.width,
            self.height,
            ((self.width // 2), self.height // 2),  # Use the center of the drawing area
            self.ahrs_line_deg,
            aircraft,
            self.MainColor,
            self.line_thickness,
            self.line_mode,
            self.font,
            self.pxy_div,
            (x, y)
        )

        # Draw center and flight path on the main screen (already adjusted for position)
        self.draw_center(smartdisplay, x, y)
        self.draw_flight_path(aircraft, smartdisplay, x, y)

        # Blit the entire surface to the screen at the specified position
        smartdisplay.pygamescreen.blit(self.surface, pos)


    # update a setting
    def setting(self,key,var):
        print("setting ",key,var)
        locals()[key] = var
        print("setting ",locals()[key])

    # cycle through the modes.
    def cyclecaged_mode(self):
        self.caged_mode = self.caged_mode + 1
        if self.caged_mode > 1:
            self.caged_mode = 0

    def clear(self):
        #self.ahrs_bg.fill((0, 0, 0))  # clear screen
        print("clear")

    # handle key events
    def processEvent(self, event):
        print("processEvent")

    # return a dict of objects that are used to configure the module.
    def get_module_options(self):
        # each item in the dict represents a configuration option.  These are variable in this class that are exposed to the user to edit.
        return {
            "line_mode": {
                "type": "bool",
                "default": False,
                "label": "Line Mode",
                "description": ""
            },
            "line_thickness": {
                "type": "int",
                "default": 2,
                "min": 1,
                "max": 4,
                "label": "Line Thickness",
                "description": ""
            },
            "MainColor": {
                "type": "color",
                "default": (255, 255, 255),
                "label": "Line Color", 
            },
            "flight_path_color": {
                "type": "color",
                "default": (255, 0, 255),
                "label": "Flight Path Color",
            }
        }

    def update_flight_path_color(self, new_color):
        self.flight_path_color = new_color


#############################################
## Class: Point
## used for graphical points.
class Point:
    # constructed using a normal tupple
    def __init__(self, point_t=(0, 0)):
        self.x = float(point_t[0])
        self.y = float(point_t[1])

    # define all useful operators
    def __add__(self, other):
        return Point((self.x + other.x, self.y + other.y))

    def __sub__(self, other):
        return Point((self.x - other.x, self.y - other.y))

    def __mul__(self, scalar):
        return Point((self.x * scalar, self.y * scalar))

    def __div__(self, scalar):
        return Point((self.x / scalar, self.y / scalar))

    def __len__(self):
        return int(math.sqrt(self.x ** 2 + self.y ** 2))

    # get back values in original tuple format
    def get(self):
        return (self.x, self.y)

# vi: modeline tabstop=8 expandtab shiftwidth=4 softtabstop=4 syntax=python
