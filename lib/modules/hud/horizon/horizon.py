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


class Horizon(Module):
    # called only when object is first created.
    def __init__(self):
        Module.__init__(self)
        self.name = "Horizon"  # set name

    # called once for setup
    def initMod(self, pygamescreen, width, height):
        Module.initMod(
            self, pygamescreen, width, height
        )  # call parent init screen.
        print(("Init Mod: %s %dx%d"%(self.name,self.width,self.height)))

        # fonts
        self.font = pygame.font.SysFont(
            None, int(self.height / 20)
        )
        self.surface = pygame.Surface((self.width * 2, self.height * 2))
        self.ahrs_bg_width = self.surface.get_width()
        self.ahrs_bg_height = self.surface.get_height()
        self.ahrs_bg_center = (self.ahrs_bg_width / 2 + 160, self.ahrs_bg_height / 2)
        self.MainColor = (0, 255, 0)  # main color of hud graphics
        self.line_thickness = hud_utils.readConfigInt("HUD", "line_thickness", 2)
        self.ahrs_line_deg = hud_utils.readConfigInt("HUD", "vertical_degrees", 5)
        self.pxy_div = 30  # Y axis number of pixels per degree divisor
        self.line_mode = hud_utils.readConfigInt("HUD", "line_mode", 1)
        self.caged_mode = 1 # default on
        self.center_circle_mode = hud_utils.readConfigInt("HUD", "center_circle", 4)

        # sampling for flight path.
        self.readings = []  # Setup moving averages to smooth a bit
        self.max_samples = 20 # FPM smoothing
        self.readings1 = []  # Setup moving averages to smooth a bit
        self.max_samples1 = 20 # Caged FPM smoothing

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
            if deg_ref == 0:
                length = screen_width * 0.5
            elif (deg_ref % 10) == 0:
                length = screen_width * 0.25
            elif (deg_ref % 5) == 0:
                length = screen_width * 0.11

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
    ):

        for l in range(-60, 61, ahrs_line_deg):
            line_coords = self.generateHudReferenceLineArray(
                width,
                height,
                ahrs_center,
                pxy_div,
                pitch=aircraft.pitch,
                roll=aircraft.roll,
                deg_ref=l,
                line_mode=line_mode,
            )

            if abs(l) > 45:
                if l % 5 == 0 and l % 10 != 0:
                    continue

            # draw below or above the horz
            if l < 0:
                z=1+1
                self.draw_dashed_line(
                    self.surface,
                    color,
                    line_coords[1],
                    line_coords[2],
                    width=line_thickness,
                    dash_length=5,
                )
                # draw winglets facing up
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

            # draw degree text
            if l != 0 and l % 5 == 0:
                text = font.render(str(l), False, color)
                text_width, text_height = text.get_size()
                left = int(line_coords[1][0]) - (text_width + int(width / 100))
                top = int(line_coords[1][1]) - text_height / 2
                self.surface.blit(text, (left, top))


    def draw_center(self,smartdisplay):
        if self.center_circle_mode == 1:
            pygame.draw.circle(
                smartdisplay.pygamescreen,
                self.MainColor,
                (smartdisplay.x_center + self.x_offset, smartdisplay.y_center),
                3,
                1,
            )
        elif self.center_circle_mode == 2:
            pygame.draw.circle(
                smartdisplay.pygamescreen,
                self.MainColor,
                (smartdisplay.x_center + self.x_offset, smartdisplay.y_center),
                15,
                1,
            )
        elif self.center_circle_mode == 3:
            pygame.draw.circle(
                smartdisplay.pygamescreen,
                self.MainColor,
                (smartdisplay.x_center + self.x_offset, smartdisplay.y_center),
                50,
                1,
            )
        # draw water line center.
        elif self.center_circle_mode == 4:
            pygame.draw.line(
                smartdisplay.pygamescreen,
                self.MainColor,
                [smartdisplay.x_center - 10 + self.x_offset, smartdisplay.y_center + 20],
                [smartdisplay.x_center + self.x_offset , smartdisplay.y_center],
                3,
            )
            pygame.draw.line(
                smartdisplay.pygamescreen,
                self.MainColor,
                [smartdisplay.x_center - 10 + self.x_offset, smartdisplay.y_center + 20],
                [smartdisplay.x_center - 20 + self.x_offset, smartdisplay.y_center],
                3,
            )
            pygame.draw.line(
                smartdisplay.pygamescreen,
                self.MainColor,
                [smartdisplay.x_center - 35 + self.x_offset, smartdisplay.y_center],
                [smartdisplay.x_center - 20 + self.x_offset, smartdisplay.y_center],
                3,
            )
            pygame.draw.line(
                smartdisplay.pygamescreen,
                self.MainColor,
                [smartdisplay.x_center + 10 + self.x_offset, smartdisplay.y_center + 20],
                [smartdisplay.x_center  + self.x_offset, smartdisplay.y_center],
                3,
            )
            pygame.draw.line(
                smartdisplay.pygamescreen,
                self.MainColor,
                [smartdisplay.x_center + 10 + self.x_offset, smartdisplay.y_center + 20],
                [smartdisplay.x_center + 20 + self.x_offset, smartdisplay.y_center],
                3,
            )
            pygame.draw.line(
                smartdisplay.pygamescreen,
                self.MainColor,
                [smartdisplay.x_center + 35 + self.x_offset, smartdisplay.y_center],
                [smartdisplay.x_center + 20 + self.x_offset, smartdisplay.y_center],
                3,
            )

    def draw_flight_path(self,aircraft,smartdisplay):
        def mean(nums):
            return int(sum(nums)) / max(len(nums), 1)

        # flight path indicator
        if self.caged_mode:
            fpv_x = 0.0
        else:
            fpv_x = ((((aircraft.mag_head - aircraft.gndtrack) + 180) % 360) - 180) * 1.5  - (
                aircraft.turn_rate * 5
            )
            self.readings.append(fpv_x)
            fpv_x = mean(self.readings)  # Moving average to smooth a bit
            if len(self.readings) == self.max_samples:
                self.readings.pop(0)
        gfpv_x = ((((aircraft.mag_head - aircraft.gndtrack) + 180) % 360) - 180) * 1.5  - (
            aircraft.turn_rate * 5
        )
        self.readings1.append(gfpv_x)
        gfpv_x = mean(self.readings1)  # Moving average to smooth a bit
        if len(self.readings1) == self.max_samples1:
            self.readings1.pop(0)
        self.draw_circle(
            smartdisplay.pygamescreen,
            (255, 0, 255),
            (
                (smartdisplay.width / 2 + self.x_offset) - (int(fpv_x) * 5),
                smartdisplay.y_center - (aircraft.vsi / 15),
            ),
            15,
            2,
        )
        self.draw_circle(
            smartdisplay.pygamescreen,
            (255, 0, 255),
            (
                (smartdisplay.width / 2 + self.x_offset +1) - (int(fpv_x) * 5),
                smartdisplay.y_center - (aircraft.vsi / 15),
            ),
            15,
            2,
        )
        pygame.draw.line(
            smartdisplay.pygamescreen,
            (255, 0, 255),
            [
                (smartdisplay.width / 2 + self.x_offset) - (int(fpv_x) * 5) - 15,
                smartdisplay.y_center - (aircraft.vsi / 15),
            ],
            [
                (smartdisplay.width / 2 + self.x_offset) - (int(fpv_x) * 5) - 30,
                smartdisplay.y_center - (aircraft.vsi / 15),
            ],
            2,
        )
        pygame.draw.line(
            smartdisplay.pygamescreen,
            (255, 0, 255),
            [
                (smartdisplay.width / 2 + self.x_offset) - (int(fpv_x) * 5) + 15,
                smartdisplay.y_center - (aircraft.vsi / 15),
            ],
            [
                (smartdisplay.width / 2 + self.x_offset) - (int(fpv_x) * 5) + 30,
                smartdisplay.y_center - (aircraft.vsi / 15),
            ],
            2,
        )
        pygame.draw.line(
            smartdisplay.pygamescreen,
            (255, 0, 255),
            [
                (smartdisplay.width / 2 + self.x_offset) - (int(fpv_x) * 5),
                smartdisplay.y_center - (aircraft.vsi / 15) - 15,
            ],
            [
                (smartdisplay.width / 2 + self.x_offset) - (int(fpv_x) * 5),
                smartdisplay.y_center - (aircraft.vsi / 15) - 30,
            ],
            2,
        )
        if self.caged_mode:
            pygame.draw.line(
                smartdisplay.pygamescreen,
                (255, 0, 255),
                [
                    (smartdisplay.width / 2 + self.x_offset) - (int(gfpv_x) * 5) - 15,
                    smartdisplay.y_center - (aircraft.vsi / 15),
                ],
                [
                    (smartdisplay.width / 2 + self.x_offset) - (int(gfpv_x) * 5) - 30,
                    smartdisplay.y_center - (aircraft.vsi / 15),
                ],
                2,
            )
            pygame.draw.line(
                smartdisplay.pygamescreen,
                (255, 0, 255),
                [
                    (smartdisplay.width / 2 + self.x_offset) - (int(gfpv_x) * 5) + 15,
                    smartdisplay.y_center - (aircraft.vsi / 15),
                ],
                [
                    (smartdisplay.width / 2 + self.x_offset) - (int(gfpv_x) * 5) + 30,
                    smartdisplay.y_center - (aircraft.vsi / 15),
                ],
                2,
            )
            pygame.draw.line(
                smartdisplay.pygamescreen,
                (255, 0, 255),
                [
                    (smartdisplay.width / 2 + self.x_offset) - (int(gfpv_x) * 5),
                    smartdisplay.y_center - (aircraft.vsi / 15) - 15,
                ],
                [
                    (smartdisplay.width / 2 + self.x_offset) - (int(gfpv_x) * 5),
                    smartdisplay.y_center - (aircraft.vsi / 15) - 30,
                ],
                2,
            )


    # called every redraw for the mod
    def draw(self, aircraft, smartdisplay):

        self.surface.fill((0, 0, 0))  # clear surface

        self.draw_horz_lines(
            smartdisplay.width,
            smartdisplay.height,
            (smartdisplay.x_center + self.x_offset,smartdisplay.y_center),
            self.ahrs_line_deg,
            aircraft,
            self.MainColor,
            self.line_thickness,
            self.line_mode,
            self.font,
            self.pxy_div,
        )
        self.pygamescreen.blit(self.surface, ( -(0), -(0)))

        self.draw_center(smartdisplay)
        self.draw_flight_path(aircraft,smartdisplay)

    # update a setting
    def setting(self,key,var):
        print("setting ",key,var)
        locals()[key] = var
        print("setting ",locals()[key])

    # called before screen draw.  To clear the screen to your favorite color.
    def clear(self):
        #self.ahrs_bg.fill((0, 0, 0))  # clear screen
        print("clear")

    # handle key events
    def processEvent(self, event):
        print("processEvent")

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