#!/usr/bin/env python

import math, os, sys, random
import argparse, pygame
from operator import add
from . import hud_utils
from lib import drawpos

#############################################
## Function: initDisplay
def initDisplay(debug):
    pygame.init()
    disp_no = os.getenv("DISPLAY")
    print(("sys.platform:%s"%(sys.platform)))
    if disp_no:
        # assume we are in xdisplay. in xwindows on linux/rpi
        print(("default to XDisplay {0}".format(disp_no)))
        inWindow = hud_utils.readConfig("HUD", "window", "false")  # default screen to load
        if inWindow == "true":
            # if they want a windowed version..
            size = 640, 480
            screen = pygame.display.set_mode(size)
            pygame.display.set_caption('efis')
        else:
            # Go full screen with no frame.
            size = pygame.display.Info().current_w, pygame.display.Info().current_h
            screen = pygame.display.set_mode((0,0), pygame.NOFRAME)
    else:
        drivers = ["directfb", "fbcon", "svgalib"]
        found = False
        for driver in drivers:
            if not os.getenv("SDL_VIDEODRIVER"):
                os.putenv("SDL_VIDEODRIVER", driver)
            try:
                pygame.display.init()
            except pygame.error:
                print(("Driver: {0} failed.".format(driver)))
                continue

            found = True
            break

        if not found:
            raise Exception("No video driver found.  Exiting.")

        # check if we are in windows or macosx
        if sys.platform.startswith('win') or sys.platform.startswith('darwin'):
            size = 640, 480
            screen = pygame.display.set_mode(size, pygame.RESIZABLE)
            pygame.display.set_caption('efis')
        else:
            size = pygame.display.Info().current_w, pygame.display.Info().current_h
            screen = pygame.display.set_mode(size, pygame.FULLSCREEN)

    return screen, size


#############################################
## Function: generateHudReferenceLineArray
## create array of horz lines based on pitch, roll, etc.
def hud_generateHudReferenceLineArray(
    screen_width, screen_height, ahrs_center, pxy_div, pitch=0, roll=0, deg_ref=0, line_mode=1,
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


#############################################
## Function: draw_dashed_line
def hud_draw_dashed_line(surf, color, start_pos, end_pos, width=1, dash_length=10):
    origin = Point(start_pos)
    target = Point(end_pos)
    displacement = target - origin
    length = len(displacement)
    slope = Point((displacement.x / length, displacement.y/length))

    for index in range(0, length // dash_length, 2):
        start = origin + (slope * index * dash_length)
        end = origin + (slope * (index + 1) * dash_length)
        pygame.draw.line(surf, color, start.get(), end.get(), width)


#############################################
## Function: hud_draw_text
def hud_draw_text(screen, font, text, color, x, y):
    screen.blit(font.render(text, 1, color), (x, y))


#############################################
## Function: hud_draw_box_text
def hud_draw_box_text(
    screen, font, text, textcolor, x, y, width, height, linecolor, thickness
):
    pygame.draw.rect(screen, linecolor, (x, y, width, height), thickness)
    screen.blit(font.render(text, 1, textcolor), (x, y))


#############################################
## Function draw horz lines
def hud_draw_horz_lines(
    pygamescreen,
    surface,
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
        line_coords = hud_generateHudReferenceLineArray(
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
            hud_draw_dashed_line(
                surface,
                color,
                line_coords[1],
                line_coords[2],
                width=line_thickness,
                dash_length=5,
            )
            # draw winglets facing up
            pygame.draw.lines(surface,
                color,
                False,
                (line_coords[2],
                line_coords[4]),
                line_thickness
            )
            pygame.draw.lines(surface,
                color,
                False,
                (line_coords[1],
                line_coords[5]),
                line_thickness
            )
        else:
            pygame.draw.lines(
                surface,
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
            surface.blit(text, (left, top))

        # draw center circle.
        hud_draw_circle(
                 surface,
                 color,
                 ahrs_center,
                 15,
                 1,
             )


def hud_draw_circle(pygamescreen,color,center,radius,width):
    pygame.draw.circle(
        pygamescreen,
        color,
        (int(center[0]),int(center[1])),
        radius,
        width,
    )

def hud_draw_debug(aircraft,smartdisplay,font):
    # render debug text
    label = font.render("pitch: %d" % (aircraft.pitch), 1, (255, 255, 0))
    smartdisplay.pygamescreen.blit(label, (smartdisplay.x_start, smartdisplay.y_start))
    label = font.render("Roll: %d" % (aircraft.roll), 1, (255, 255, 0))
    smartdisplay.pygamescreen.blit(label, (smartdisplay.x_start, smartdisplay.y_start+20))
    label = font.render(
        "IAS: %d  VSI: %d" % (aircraft.ias, aircraft.vsi), 1, (255, 255, 0)
    )
    smartdisplay.pygamescreen.blit(label, (smartdisplay.x_start, smartdisplay.y_start+40))
    label = font.render(
        "Alt: %d  PresALT:%d  BaroAlt:%d   AGL: %d"
        % (aircraft.alt, aircraft.PALT, aircraft.BALT, aircraft.agl),
        1,
        (255, 255, 0),
    )
    smartdisplay.pygamescreen.blit(label, (smartdisplay.x_start, smartdisplay.y_start+60))
    if aircraft.aoa != None:
        label = font.render("AOA: %d" % (aircraft.aoa), 1, (255, 255, 0))
        smartdisplay.pygamescreen.blit(label, (smartdisplay.x_start, smartdisplay.y_start+80))
    else:
        label = font.render("AOA: NA", 1, (255, 255, 0))
        smartdisplay.pygamescreen.blit(label, (smartdisplay.x_start, smartdisplay.y_start+80))
    # Mag heading
    label = font.render(
        "MagHead: %d  TrueTrack: %d" % (aircraft.mag_head, aircraft.gndtrack),
        1,
        (255, 255, 0),
    )
    smartdisplay.pygamescreen.blit(label, (smartdisplay.x_start, smartdisplay.y_start+100))
    label = font.render(
        "Baro: %0.2f diff: %0.4f" % (aircraft.baro, aircraft.baro_diff),
        1,
        (20, 255, 0),
    )
    smartdisplay.pygamescreen.blit(label, (smartdisplay.x_start, smartdisplay.y_start+120))

    label = font.render(
        "size: %d,%d" % (smartdisplay.width, smartdisplay.height), 1, (20, 255, 0)
    )
    smartdisplay.pygamescreen.blit(label, (smartdisplay.x_start+70, smartdisplay.y_start))

    label = font.render(
        "msgcount: %d" % (aircraft.msg_count), 1, (20, 255, 0)
    )
    smartdisplay.pygamescreen.blit(label, (smartdisplay.x_start+200, smartdisplay.y_start))

    smartdisplay.draw_text(drawpos.DrawPos.BOTTOM_RIGHT, font, "%0.2f FPS" % (aircraft.fps), (255, 255, 0))
