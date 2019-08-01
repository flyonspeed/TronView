#!/usr/bin/env python

import pygame


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

def addGrowlNotice(text,time,color,postion=8,cb=0):
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
    screen_w, screen_h = pygame.display.get_surface().get_size()
    width, height = font.size(text)
    padding = 15

    if postion == 0:  # center of screen.
        x = (screen_w/2)-(width/2)
        y = (screen_h/2)-(height/2)
    if postion == 1:  # top left
        x = padding
        y = padding
    if postion == 2:  # top middle
        x = (screen_w/2)-(width/2)
        y = padding
    if postion == 3:  # top right
        x = (screen_w)-(width)-padding
        y = padding
    if postion == 4:  # middle left
        x = padding
        y = (screen_h/2)-(height/2)
    if postion == 5:  # middle right
        x = (screen_w)-(width)-padding
        y = (screen_h/2)-(height/2)
    if postion == 6:  # bottom left
        x = padding
        y = (screen_h)-(height)-padding
    if postion == 7:  # bottom middle
        x = (screen_w/2)-(width/2)
        y = (screen_h)-(height)-padding
    if postion == 8:  # bottom right
        x = (screen_w)-(width)-padding
        y = (screen_h)-(height)-padding

    pygame.draw.rect(pyscreen, colour, (x-padding,y-padding,width+padding+10,height+padding+10),0)
    label=font.render(text, 1, (0,0,0))
    pyscreen.blit(label,(x,y))

# vi: modeline tabstop=8 expandtab shiftwidth=4 softtabstop=4 syntax=python

