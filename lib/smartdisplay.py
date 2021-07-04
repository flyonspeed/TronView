#!/usr/bin/env python


from . import drawpos
import pygame

#############################################
## Class: smartdisplay
## Store display information for viewable display.
##
class SmartDisplay(object):
    def __init__(self):
        print("SmartDisplay Init")
        self.x_start = 0
        self.y_start = 0
        self.x_end = 0
        self.y_end = 0
        self.width = 0
        self.height = 0
        self.widthCenter = (self.width / 2) 
        self.heightCenter = (self.height / 2)
        self.pygamescreen = 0

        self.pos_next_left_up = 0
        self.pos_next_left_down = 0

        self.pos_next_right_up = 0
        self.pos_next_right_down = 0
        self.pos_next_right_padding = 0

        self.pos_next_bottom_padding = 0

        self.pos_horz_padding = 25

    def setDrawableArea(self,x_start,y_start,x_end,y_end):
        self.x_start = x_start
        self.y_start = y_start
        self.x_end = x_end
        self.y_end = y_end
        self.width = x_end - x_start
        self.height = y_end - y_start
        self.widthCenter = (self.width / 2) 
        self.heightCenter = (self.height / 2) 
        print(("SmartDisplay drawable offset: %d,%d to %d,%d"%(self.x_start,self.y_start,self.x_end,self.y_end)))
        print(("SmartDisplay New screen width/height: %d,%d"%(self.width,self.height)))
        print(("SmartDisplay center x/y: %d,%d"%(self.widthCenter,self.heightCenter)))

    def setPyGameScreen(self,pygamescreen):
        self.pygamescreen = pygamescreen


    # this resets the counters in this object to keep track of where to draw things.
    def blit_loop_reset(self):
        self.pos_next_left_up = 0
        self.pos_next_left_down = 0
        self.pos_next_right_up = 0
        self.pos_next_right_down = 0
        self.pos_next_right_padding = 0
        self.pos_next_bottom_padding = 0

    # smart blit the next surface to the display given a location.
    # this automatically pads space from the last item that was displayed.
    def blit_next(self,surface,drawAtPos,posAdjustment=(0,0)):

        posAdjustmentX, posAdjustmentY = posAdjustment

        # LEFT SIDE
        if drawAtPos == drawpos.DrawPos.LEFT_MID:
            self.pygamescreen.blit(surface, (self.x_start + self.pos_horz_padding+posAdjustmentX, (self.heightCenter+self.y_start+posAdjustmentY)))
            self.pos_next_left_up += surface.get_height()
            self.pos_next_left_down += surface.get_height()

        elif drawAtPos == drawpos.DrawPos.LEFT_MID_UP:
            self.pygamescreen.blit(surface, (self.x_start + self.pos_horz_padding+posAdjustmentX, (self.heightCenter+self.y_start-self.pos_next_left_up+posAdjustmentY) ))
            self.pos_next_left_up += surface.get_height() # first get the new postion..

        elif drawAtPos == drawpos.DrawPos.LEFT_MID_DOWN:
            self.pygamescreen.blit(surface, (self.x_start + self.pos_horz_padding+posAdjustmentX, (self.heightCenter+self.y_start+self.pos_next_left_down+posAdjustmentY) ))
            self.pos_next_left_down += surface.get_height()

        # RIGHT SIDE
        elif drawAtPos == drawpos.DrawPos.RIGHT_MID:
            self.pos_next_right_padding = surface.get_width() + self.pos_horz_padding
            self.pygamescreen.blit(surface, (self.x_end - self.pos_next_right_padding+posAdjustmentX, (self.heightCenter+self.y_start+posAdjustmentY)))
            self.pos_next_right_up += surface.get_height()
            self.pos_next_right_down += surface.get_height()

        elif drawAtPos == drawpos.DrawPos.RIGHT_MID_UP:
            self.pygamescreen.blit(surface, (self.x_end - self.pos_next_right_padding+posAdjustmentX, (self.heightCenter+self.y_start-self.pos_next_right_up+posAdjustmentY) ))
            self.pos_next_right_up += surface.get_height() # first get the new postion..

        elif drawAtPos == drawpos.DrawPos.RIGHT_MID_DOWN:
            self.pygamescreen.blit(surface, (self.x_end - self.pos_next_right_padding+posAdjustmentX, (self.heightCenter+self.y_start+self.pos_next_right_down+posAdjustmentY) ))
            self.pos_next_right_down += surface.get_height()

        # TOP
        elif drawAtPos == drawpos.DrawPos.TOP:
            self.pygamescreen.blit(surface, (self.x_start+posAdjustmentX, self.y_start+posAdjustmentY))

        elif drawAtPos == drawpos.DrawPos.TOP_MID:
            self.pygamescreen.blit(surface, (self.x_start+self.widthCenter-(surface.get_width()/2)+posAdjustmentX, self.y_start+posAdjustmentY ))

        elif drawAtPos == drawpos.DrawPos.TOP_RIGHT:
            self.pygamescreen.blit(surface, (self.x_end-surface.get_width()+posAdjustmentX, (self.y_start+posAdjustmentY) ))

        # BOTTOM
        elif drawAtPos == drawpos.DrawPos.BOTTOM:
            self.pos_next_bottom_padding = surface.get_height()
            self.pygamescreen.blit(surface, (self.x_start+posAdjustmentX, self.y_end+posAdjustmentY-self.pos_next_bottom_padding))

        elif drawAtPos == drawpos.DrawPos.BOTTOM_MID:
            self.pos_next_bottom_padding = surface.get_height()
            self.pygamescreen.blit(surface, (self.x_start+self.widthCenter-(surface.get_width()/2)+posAdjustmentX, self.y_end+posAdjustmentY-self.pos_next_bottom_padding ))

        elif drawAtPos == drawpos.DrawPos.BOTTOM_RIGHT:
            self.pos_next_bottom_padding = surface.get_height()
            self.pygamescreen.blit(surface, (self.x_end-surface.get_width()+posAdjustmentX, (self.y_end+posAdjustmentY)-self.pos_next_bottom_padding ))


    # draw box with text in it.
    # drawPos = DrawPos on screen.. example drawpos.DrawPos.RIGHT_MID for right middle of display.
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
    def draw_circle(self,color,center,radius,width):
        pygame.draw.circle(
            self.pygamescreen,
            color,
            (int(center[0]),int(center[1])),
            radius,
            width,
        )

# vi: modeline tabstop=8 expandtab shiftwidth=4 softtabstop=4 syntax=python

