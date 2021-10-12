#!/usr/bin/env python

import pygame
from lib.common import shared

white    = (255, 255, 255)
tron_whi = (189, 254, 255)
red      = (255,   80,   60)
green    = (  50, 255,   50)
blue     = (  120,   90, 255)
tron_blu = (  0, 219, 232)
black    = (  0,   0,   0)
cyan     = ( 50, 255, 255)
magenta  = (255,   0, 255)
yellow   = (255, 255,   0)
tron_yel = (255, 218,  10)
orange   = (255, 127,   0)
tron_ora = (255, 202,   0)
nerd_yellow = (255, 202, 100)

tron_regular = tron_ora
tron_light   = tron_yel
tron_inverse = tron_whi

CENTER = 1
TOP_CENTER = 2
TOP_LEFT = 3
TOP_RIGHT = 4

MIDDLE_LEFT = 5
MIDDLE_RIGHT = 6
MIDDLE_CENTER = 1

BOTTOM_LEFT = 7
BOTTOM_RIGHT = 8 
BOTTOM_CENTER = 9


globalDrawTimers = []

#############################################
## Class: DrawTimer
## 
##
class DrawTimer(object):



    def __init__(self,ttype,text,ticksTillDone,color,postion=0,callBackHandler=0):
        self.type = ttype  # type: 0=none, 1=growl notice 
        self.startTime = pygame.time.get_ticks()
        self.endTime = self.startTime + ticksTillDone
        self.callBackHandler = callBackHandler
        self.text = text
        self.font = pygame.font.SysFont( "monospace", 32,True)
        self.postion = postion
        self.color = color
        self.customDrawCallBack = 0

    def draw(self,pyscreen):
        if self.customDrawCallBack != 0:
            self.customDrawCallBack()
        elif self.type == 1:
            make_box_label(self.font,self.text,self.postion,self.color,pyscreen)

    def checkIfDone(self):
        now = pygame.time.get_ticks()
        if now >= self.endTime:
            if self.callBackHandler != 0:
                self.callBackHandler()
            return True
        return False

def addCustomDraw(drawFunc,time,cb=0):
    timer = DrawTimer(0,"",time,cb)
    timer.customDrawCallBack = drawFunc
    globalDrawTimers.append(timer)

def addGrowlNotice(text,time,color,postion=BOTTOM_RIGHT,cb=0):
    # first check if there is any in this same postion. if so remove it.
    for existingTimer in globalDrawTimers:
        if existingTimer.postion == postion: 
            globalDrawTimers.remove(existingTimer)
    timer = DrawTimer(1,text,time,color,postion,cb)
    globalDrawTimers.append(timer)

def processAllDrawTimers(pyscreen):
    if len(globalDrawTimers) > 0:
        for timer in globalDrawTimers:
            if timer.checkIfDone() == True: # if timer is done then remove it from the array of timers.
                globalDrawTimers.remove(timer)
            else:
                timer.draw(pyscreen)

def make_box_label(font,text, postion, colour, pyscreen):
    width, height = font.size(text)
    padding = 15

    x_start = shared.smartdisplay.x_start
    y_start = shared.smartdisplay.y_start
    x_end = shared.smartdisplay.x_end
    y_end = shared.smartdisplay.y_end
    screen_w = shared.smartdisplay.width
    screen_h = shared.smartdisplay.height

    if postion == CENTER:  # center of screen.
        x = x_start + (shared.smartdisplay.widthCenter)-(width/2)
        y = y_start + (shared.smartdisplay.heightCenter)-(height/2)
    if postion == TOP_LEFT:  # top left
        x = x_start + padding
        y = y_start + padding
    if postion == TOP_CENTER:  # top middle
        x = x_start + (shared.smartdisplay.widthCenter)-(width/2)
        y = y_start + padding
    if postion == TOP_RIGHT:  # top right
        x = (x_end)-(width)-padding
        y = y_start + padding
    if postion == MIDDLE_LEFT:  # middle left
        x = x_start + padding
        y = (screen_h/2)-(height/2)
    if postion == MIDDLE_RIGHT:  # middle right
        x = (x_end)-(width)-padding
        y = (shared.smartdisplay.heightCenter)-(height/2)
    if postion == BOTTOM_LEFT:  # bottom left
        x = x_start + padding
        y = (y_end)-(height)-padding
    if postion == BOTTOM_CENTER:  # bottom middle
        x = (shared.smartdisplay.widthCenter)-(width/2)
        y = (y_end)-(height)-padding
    if postion == BOTTOM_RIGHT:  # bottom right
        x = (screen_w)-(width)-padding
        y = (y_end)-(height)-padding

    pygame.draw.rect(pyscreen, colour, (x-padding,y-padding,width+padding+10,height+padding+10),0)
    label=font.render(text, 1, (0,0,0))
    pyscreen.blit(label,(x,y))

# vi: modeline tabstop=8 expandtab shiftwidth=4 softtabstop=4 syntax=python

