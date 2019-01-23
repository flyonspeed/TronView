#!/usr/bin/env python

import math, os, sys, random
import argparse, pygame

#############################################
## Function: initDisplay
def initDisplay(debug):
    pygame.init()
    disp_no = os.getenv('DISPLAY')
    if disp_no:
    #if False:
        print "default to XDisplay {0}".format(disp_no)
        size = 640, 480
        #size = 320, 240
        screen = pygame.display.set_mode(size)
    else:
        drivers = ['directfb', 'fbcon', 'svgalib']
        found = False
        for driver in drivers:
            if not os.getenv('SDL_VIDEODRIVER'):
                os.putenv('SDL_VIDEODRIVER', driver)
            try:
                pygame.display.init()
            except pygame.error:
                print 'Driver: {0} failed.'.format(driver)
                continue

            found = True
            break

        if not found:
            raise Exception('No video driver found.  Exiting.')

        size = pygame.display.Info().current_w, pygame.display.Info().current_h
        screen = pygame.display.set_mode(size, pygame.FULLSCREEN)

    return screen, size

#############################################
## Function: generateHudReferenceLineArray
## create array of horz lines based on pitch, roll, etc.
def hud_generateHudReferenceLineArray(screen_width, screen_height, ahrs_center, pitch=0, roll=0, deg_ref=0,line_mode=1):

    if line_mode == 1:
        if deg_ref == 0:
            length = screen_width*.9
        elif (deg_ref%10) == 0:
           length = screen_width*.2
        elif (deg_ref%5) == 0:
           length = screen_width*.1
    else:
        if deg_ref == 0:
            length = screen_width*.6
        elif (deg_ref%10) == 0:
           length = screen_width*.1
        elif (deg_ref%5) == 0:
           length = screen_width*.05

    ahrs_center_x, ahrs_center_y = ahrs_center
    px_per_deg_y = screen_height / 60
    pitch_offset = px_per_deg_y * (-pitch + deg_ref)

    center_x = ahrs_center_x - (pitch_offset * math.cos(math.radians(90 - roll)))
    center_y = ahrs_center_y - (pitch_offset * math.sin(math.radians(90 - roll)))

    x_len = length * math.cos(math.radians(roll))
    y_len = length * math.sin(math.radians(roll))

    start_x = center_x - (x_len / 2)
    end_x = center_x + (x_len / 2)
    start_y = center_y + (y_len / 2)
    end_y = center_y - (y_len / 2)

    return [[start_x, start_y], [end_x, end_y]]

#############################################
## Class: Point
## used for graphical points.
class Point:
    # constructed using a normal tupple
    def __init__(self, point_t = (0,0)):
        self.x = float(point_t[0])
        self.y = float(point_t[1])
    # define all useful operators
    def __add__(self, other):
        return Point((self.x + other.x, self.y + other.y))
    def __sub__(self, other):
        return Point((self.x - other.x, self.y - other.y))
    def __mul__(self, scalar):
        return Point((self.x*scalar, self.y*scalar))
    def __div__(self, scalar):
        return Point((self.x/scalar, self.y/scalar))
    def __len__(self):
        return int(math.sqrt(self.x**2 + self.y**2))
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
    slope = displacement/length

    for index in range(0, length/dash_length, 2):
        start = origin + (slope *    index    * dash_length)
        end   = origin + (slope * (index + 1) * dash_length)
        pygame.draw.line(surf, color, start.get(), end.get(), width)

#############################################
## Function: hud_draw_text
def hud_draw_text(screen,font,text,color,x,y):
    screen.blit(font.render(text, 1, color), (x, y))

#############################################
## Function: hud_draw_box_text
def hud_draw_box_text(screen,font,text,textcolor,x,y,width,height,linecolor,thickness):
    pygame.draw.rect(screen,linecolor,(x,y,width,height), thickness )
    screen.blit(font.render(text, 1, textcolor), (x, y))

#############################################
## Function draw horz lines
def hud_draw_horz_lines(pygamescreen,surface,width,height,ahrs_center,ahrs_line_deg,aircraft,color,line_thickness,line_mode,font):

    for l in range(-60, 61, ahrs_line_deg):
        line_coords = hud_generateHudReferenceLineArray(width, height, ahrs_center, pitch=aircraft.pitch, roll=aircraft.roll, deg_ref=l, line_mode=line_mode)

        if abs(l)>45:
            if l%5 == 0 and l%10 != 0:
                continue

        # draw below or above the horz
        if(l<0):
            hud_draw_dashed_line(surface, color, line_coords[0], line_coords[1], width=line_thickness, dash_length=5)
        else:
            pygame.draw.lines(surface, color, False, line_coords, line_thickness)

        # draw degree text
        if l != 0 and l%10 == 0:
            text = font.render(str(l), False, color)
            text_width, text_height = text.get_size()
            left = int(line_coords[0][0]) - (text_width + int(width/100))
            top = int(line_coords[0][1]) - text_height / 2
            surface.blit(text, (left, top))

    top_left = (-(surface.get_width() - width)/2, -(surface.get_height() - height)/2)
    pygamescreen.blit(surface, top_left)

