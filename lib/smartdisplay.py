#!/usr/bin/env python


import pygame

#############################################
## Class: smartdisplay
## Store display information for viewable display.
##
class SmartDisplay(object):

    LEFT = 7
    LEFT_TOP = 8
    LEFT_MID = 9
    LEFT_MID_UP = 10
    LEFT_MID_DOWN = 11
    LEFT_BOTTOM = 12

    RIGHT = 30
    RIGHT_TOP = 31
    RIGHT_MID = 32
    RIGHT_MID_UP = 33
    RIGHT_MID_DOWN = 34
    RIGHT_BOTTOM = 35

    TOP = 50
    TOP_MID = 51
    TOP_RIGHT = 52

    BOTTOM = 70
    BOTTOM_MID = 71
    BOTTOM_RIGHT = 72

    CENTER_LEFT = 80
    CENTER_CENTER = 81
    CENTER_RIGHT = 82

    def __init__(self):
        print("SmartDisplay Init")
        self.org_width = 0
        self.org_height = 0
        self.x_start = 0
        self.y_start = 0
        self.x_end = 0
        self.y_end = 0
        self.x_center = 0
        self.y_center = 0
        self.width = 0
        self.height = 0
        self.widthCenter = (self.width / 2) 
        self.heightCenter = (self.height / 2)
        self.pygamescreen = 0
        self.drawBorder = False

        self.pos_next_left_up = 0
        self.pos_next_left_down = 0

        self.pos_next_right_up = 0
        self.pos_next_right_down = 0
        self.pos_next_right_padding = 0

        self.pos_next_bottom_padding = 0

        self.pos_horz_padding = 25

    def setDisplaySize(self,width,height):
        self.org_width = width
        self.org_height = height

    def setDrawableArea(self,x_start,y_start,x_end,y_end):
        self.x_start = x_start
        self.y_start = y_start
        self.x_end = x_end
        self.y_end = y_end
        self.width = x_end - x_start
        self.height = y_end - y_start
        self.widthCenter = (self.width / 2) 
        self.heightCenter = (self.height / 2) 

        self.x_center = x_start + self.widthCenter
        self.y_center = y_start + self.heightCenter

        print(("SmartDisplay drawable offset: %d,%d to %d,%d"%(self.x_start,self.y_start,self.x_end,self.y_end)))
        print(("SmartDisplay New screen width/height: %d,%d"%(self.width,self.height)))
        print(("SmartDisplay center x/y: %d,%d"%(self.widthCenter,self.heightCenter)))
        print(("SmartDisplay real center x/y: %d,%d"%(self.x_center,self.y_center)))

    def setPyGameScreen(self,pygamescreen):
        self.pygamescreen = pygamescreen

    # this resets the counters in this object to keep track of where to draw things.
    def draw_loop_start(self):
        self.pos_next_left_up = 0
        self.pos_next_left_down = 0
        self.pos_next_right_up = 0
        self.pos_next_right_down = 0
        self.pos_next_right_padding = 0
        self.pos_next_bottom_padding = 0

    # called last after the draw loop is done.
    def draw_loop_done(self):
        # draw a border if it's smaller.
        if(self.drawBorder==True):
            pygame.draw.rect(self.pygamescreen, (255,255,255), (self.x_start, self.y_start, self.width, self.height), 1)


    # smart blit the next surface to the display given a location.
    # this automatically pads space from the last item that was displayed.
    def blit_next(self,surface,drawAtPos,posAdjustment=(0,0)):

        posAdjustmentX, posAdjustmentY = posAdjustment

        # LEFT SIDE
        if drawAtPos == SmartDisplay.LEFT_MID:
            self.pygamescreen.blit(surface, (self.x_start + self.pos_horz_padding+posAdjustmentX, (self.heightCenter-(surface.get_height()/2)+self.y_start+posAdjustmentY)))
            self.pos_next_left_up += surface.get_height()/2
            self.pos_next_left_down += surface.get_height()/2

        elif drawAtPos == SmartDisplay.LEFT_MID_UP:
            self.pygamescreen.blit(surface, (self.x_start + self.pos_horz_padding+posAdjustmentX, (self.heightCenter-surface.get_height()+self.y_start-self.pos_next_left_up+posAdjustmentY) ))
            self.pos_next_left_up += surface.get_height() # first get the new postion..

        elif drawAtPos == SmartDisplay.LEFT_MID_DOWN:
            self.pygamescreen.blit(surface, (self.x_start + self.pos_horz_padding+posAdjustmentX, (self.heightCenter+self.y_start+self.pos_next_left_down+posAdjustmentY) ))
            self.pos_next_left_down += surface.get_height()

        # RIGHT SIDE
        elif drawAtPos == SmartDisplay.RIGHT_MID:
            self.pos_next_right_padding = surface.get_width() + self.pos_horz_padding
            self.pygamescreen.blit(surface, (self.x_end - self.pos_next_right_padding+posAdjustmentX, (self.heightCenter-(surface.get_height()/2)+self.y_start+posAdjustmentY)))
            self.pos_next_right_up += surface.get_height()/2
            self.pos_next_right_down += surface.get_height()/2

        elif drawAtPos == SmartDisplay.RIGHT_MID_UP:
            self.pygamescreen.blit(surface, (self.x_end - self.pos_next_right_padding+posAdjustmentX, (self.heightCenter-surface.get_height()+self.y_start-self.pos_next_right_up+posAdjustmentY) ))
            self.pos_next_right_up += surface.get_height() # first get the new postion..

        elif drawAtPos == SmartDisplay.RIGHT_MID_DOWN:
            self.pygamescreen.blit(surface, (self.x_end - self.pos_next_right_padding+posAdjustmentX, (self.heightCenter+self.y_start+self.pos_next_right_down+posAdjustmentY) ))
            self.pos_next_right_down += surface.get_height()

        # TOP
        elif drawAtPos == SmartDisplay.TOP:
            self.pygamescreen.blit(surface, (self.x_start+posAdjustmentX, self.y_start+posAdjustmentY))

        elif drawAtPos == SmartDisplay.TOP_MID:
            self.pygamescreen.blit(surface, (self.x_start+self.widthCenter-(surface.get_width()/2)+posAdjustmentX, self.y_start+posAdjustmentY ))

        elif drawAtPos == SmartDisplay.TOP_RIGHT:
            self.pygamescreen.blit(surface, (self.x_end-surface.get_width()+posAdjustmentX, (self.y_start+posAdjustmentY) ))

        # BOTTOM
        elif drawAtPos == SmartDisplay.BOTTOM:
            self.pos_next_bottom_padding = surface.get_height()
            self.pygamescreen.blit(surface, (self.x_start+posAdjustmentX, self.y_end+posAdjustmentY-self.pos_next_bottom_padding))

        elif drawAtPos == SmartDisplay.BOTTOM_MID:
            self.pos_next_bottom_padding = surface.get_height()
            self.pygamescreen.blit(surface, (self.x_start+self.widthCenter-(surface.get_width()/2)+posAdjustmentX, self.y_end+posAdjustmentY-self.pos_next_bottom_padding ))

        elif drawAtPos == SmartDisplay.BOTTOM_RIGHT:
            self.pos_next_bottom_padding = surface.get_height()
            self.pygamescreen.blit(surface, (self.x_end-surface.get_width()+posAdjustmentX, (self.y_end+posAdjustmentY)-self.pos_next_bottom_padding ))

        # CENTER
        elif drawAtPos == SmartDisplay.CENTER_LEFT:
            self.pygamescreen.blit(surface, (self.x_start+posAdjustmentX, self.y_start+self.heightCenter-(surface.get_height()/2)+posAdjustmentY))

        elif drawAtPos == SmartDisplay.CENTER_CENTER:
            self.pygamescreen.blit(surface, (self.x_start+self.widthCenter-(surface.get_width()/2)+posAdjustmentX, self.y_start + self.heightCenter - (surface.get_height()/2) + posAdjustmentY  ))

        elif drawAtPos == SmartDisplay.CENTER_RIGHT:
            self.pygamescreen.blit(surface, (self.x_end-surface.get_width()+posAdjustmentX, (self.y_start+self.heightCenter-(surface.get_height()/2)+posAdjustmentY) ))


    # draw box with text in it.
    # drawPos = DrawPos on screen.. example smartdisplay.RIGHT_MID for right middle of display.
    # width,height of box.
    # justify: 0=left justify text, 1=right, 2= center in box.
    def draw_box_text( self, drawAtPos, font, text, textcolor, width, height, linecolor, thickness,posAdjustment=(0,0),justify=0):
        newSurface = pygame.Surface((width, height))
        label = font.render(text, 1, textcolor)
        pygame.draw.rect(newSurface, linecolor, (0, 0, width, height), thickness)
        if justify==0:
            newSurface.blit(label, (0,0))
        elif justify==1:
            newSurface.blit(label, (newSurface.get_width()-label.get_width(),0))
        elif justify==2:
            newSurface.blit(label, (newSurface.get_width()/2-label.get_width()/2,0))
        self.blit_next(newSurface,drawAtPos,posAdjustment)

    # smart draw text.
    def draw_text(self, drawAtPos, font, text, color,posAdjustment=(0,0),justify=0):
        if justify==0:
            self.blit_next(font.render(text, 1, color), drawAtPos,posAdjustment)
        elif justify==1:
            label = font.render(text, 1, color)
            self.blit_next(label, drawAtPos, (label.get_width(),0))
        elif justify==2:
            label = font.render(text, 1, color)
            self.blit_next(label, drawAtPos, (label.get_width()/2,0))

    # draw a circle.
    def draw_circle(self,color,center,radius,thickness):
        pygame.draw.circle(
            self.pygamescreen,
            color,
            (int(center[0]),int(center[1])),
            radius,
            thickness,
        )

    # draw circle with text in it.
    # drawPos = postion example smartdisplay.RIGHT_MID for right middle of display.
    # radius of circle.
    # justify (the text): 0=left justify text, 1=right, 2= center in circle.
    def draw_circle_text( self, pos, font, text, textcolor, radius , linecolor, thickness,posAdjustment=(0,0),justify=0):
        newSurface = pygame.Surface((radius*2, radius*2))
        label = font.render(text, 1, textcolor)
        ylabelStart = (radius) - label.get_height() /2
        pygame.draw.circle(
            newSurface,
            linecolor,
            (radius,radius),
            radius,
            thickness,
        )
        if justify==0:
            newSurface.blit(label, (0,ylabelStart))
        elif justify==1:
            newSurface.blit(label, (newSurface.get_width()-label.get_width(),ylabelStart))
        elif justify==2:
            newSurface.blit(label, (newSurface.get_width()/2-label.get_width()/2,ylabelStart))
        self.blit_next(newSurface,pos,posAdjustment)
# vi: modeline tabstop=8 expandtab shiftwidth=4 softtabstop=4 syntax=python

