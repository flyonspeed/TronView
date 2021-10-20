#!/usr/bin/env python

#######################################################################################################################################
#######################################################################################################################################
# graphic mode
#
#
#
from lib.common import shared

import threading
import math, os, sys, random
import argparse, pygame
import time
import configparser
import importlib
import curses
from lib import hud_graphics
from lib import hud_utils
from lib import hud_text
from lib import aircraft
from lib import smartdisplay
from lib.util.virtualKeyboard import VirtualKeyboard
from lib.util import drawTimer


#############################################
## Function: main
## Main loop.  read global var data of efis data and display graphicaly
def main_graphical():
    #global aircraft
    # init common things.
    maxframerate = hud_utils.readConfigInt("HUD", "maxframerate", 30)
    clock = pygame.time.Clock()
    pygame.time.set_timer(pygame.USEREVENT, 1000) # fire User events ever sec.

    ##########################################
    # Main graphics draw loop
    while not shared.aircraft.errorFoundNeedToExit and not shared.aircraft.textMode:
        clock.tick(maxframerate)
        for event in pygame.event.get():  # check for event like keyboard input.
            if event.type == pygame.QUIT:
                shared.aircraft.errorFoundNeedToExit = True
            # KEY MAPPINGS
            if event.type == pygame.KEYDOWN:
                mods = pygame.key.get_mods()
                if event.key == pygame.K_RIGHT and mods & pygame.KMOD_CTRL :
                    print("fast forward...")
                    shared.CurrentInput.fastForward(shared.aircraft,500)
                elif event.key == pygame.K_LEFT and mods & pygame.KMOD_CTRL :
                    print("jump backwards data...")
                    shared.CurrentInput.fastBackwards(shared.aircraft,500)
                elif (event.key == pygame.K_w and mods & pygame.KMOD_CTRL) or event.key == pygame.K_1 or event.key == pygame.K_KP1 :
                    try:
                        shared.CurrentInput.startLog(shared.aircraft)
                        drawTimer.addGrowlNotice("Created log: %s"%(shared.CurrentInput.output_logFileName),3000,drawTimer.nerd_yellow,drawTimer.CENTER)
                    except :
                        drawTimer.addGrowlNotice("Unable to create log: "+shared.CurrentInput.name,3000,drawTimer.nerd_yellow,drawTimer.CENTER)
                elif (event.key == pygame.K_e and mods & pygame.KMOD_CTRL) or event.key == pygame.K_2 or event.key == pygame.K_KP2:
                    try:
                        Saved,SendingTo = shared.CurrentInput.stopLog(shared.aircraft)
                        drawTimer.addGrowlNotice("Saved log: %s"%(shared.CurrentInput.output_logFileName),3000,drawTimer.nerd_yellow,drawTimer.CENTER) 
                        if(SendingTo!=None):
                            drawTimer.addGrowlNotice("Uploading to %s"%(SendingTo),3000,drawTimer.nerd_yellow,drawTimer.TOP_LEFT) 
                    except ValueError:
                        pass  
                elif event.key == pygame.K_d and mods & pygame.KMOD_CTRL:
                    shared.CurrentScreen.debug = not shared.CurrentScreen.debug
                elif event.key == pygame.K_q or event.key == pygame.K_ESCAPE:
                    shared.aircraft.errorFoundNeedToExit = True
                elif event.key == pygame.K_PAGEUP:
                    loadScreen(hud_utils.findScreen("prev"))
                elif event.key == pygame.K_PAGEDOWN:
                    loadScreen(hud_utils.findScreen("next"))
                elif event.key == pygame.K_HOME:
                    loadScreen(hud_utils.findScreen("current"))
                elif event.key == pygame.K_t:
                    shared.aircraft.textMode = True # switch to text mode?
                elif event.key == pygame.K_m:
                    pygame.mouse.set_visible(True)
                elif event.key == pygame.K_k:
                    vkey = VirtualKeyboard(pygamescreen) # create a virtual keyboard
                    #vkey.run("test")
                else:
                    shared.CurrentScreen.processEvent(event,shared.aircraft,shared.smartdisplay)  # send this key command to the hud screen object
            # Mouse Mappings (not droppings)
            if event.type == pygame.MOUSEBUTTONDOWN:
                mx, my = pygame.mouse.get_pos()
                if(mx>shared.smartdisplay.x_end-100 and my < 100):  # top right - goto next screen
                    loadScreen(hud_utils.findScreen("next"))
                elif(mx < 100 and my > shared.smartdisplay.y_end-100): # bottom left - debug on
                    shared.CurrentScreen.debug = not shared.CurrentScreen.debug
                else:
                    #print("Touch %d x %d"%(mx,my))
                    drawTimer.addGrowlNotice("%dx%d"%(mx,my),3000,drawTimer.blue,drawTimer.BOTTOM_LEFT)
                    drawTimer.addCustomDraw(drawMouseBox,1000)
                    shared.CurrentScreen.processEvent(event,shared.aircraft,shared.smartdisplay)
            # User event
            #if event.type == pygame.USEREVENT:
                #print("user event")
                

        # main draw loop.. clear screen then draw frame from current screen object.
        shared.aircraft.fps = clock.get_fps();
        shared.CurrentScreen.clearScreen()
        shared.smartdisplay.draw_loop_start()
        shared.CurrentScreen.draw(shared.aircraft,shared.smartdisplay)  # draw method for current screen object
        drawTimer.processAllDrawTimers(pygamescreen) # process / remove / draw any active drawTimers...
        if(shared.aircraft.demoMode==True):
            shared.smartdisplay.draw_text(shared.smartdisplay.LEFT_MID_UP, None, "PLAYBACK Log: %s" % (shared.aircraft.demoFile), (255, 255, 0))
        shared.smartdisplay.draw_loop_done()

        #now make pygame update display.
        pygame.display.update()


    # once exists main loop, close down pygame. and exit.
    pygame.quit()
    pygame.display.quit()


#############################################
## Function: loadScreen
# load screen module name.  And init screen with screen size.
def loadScreen(ScreenNameToLoad):
    global pygamescreen
    print(("Loading screen module: %s"%(ScreenNameToLoad)))
    module = ".%s" % (ScreenNameToLoad)
    mod = importlib.import_module(
        module, "lib.screens"
    )  # dynamically load screen class
    class_ = getattr(mod, ScreenNameToLoad)
    shared.CurrentScreen = class_()
    pygamescreen, screen_size = hud_graphics.initDisplay(0)
    width, height = screen_size
    shared.smartdisplay.setDisplaySize(width,height)
    shared.CurrentScreen.initDisplay(
        pygamescreen, width, height
    )  # tell the screen we are about to start. 
    shared.smartdisplay.setPyGameScreen(pygamescreen)
    drawableAreaString = hud_utils.readConfig("HUD", "drawable_area", "")
    if len(drawableAreaString)>0:
        print(("Found drawable area: %s"%(drawableAreaString)))
        area = drawableAreaString.split(",")
        try:
            shared.smartdisplay.setDrawableArea(int(area[0]),int(area[1]),int(area[2]),int(area[3]))  
        except AttributeError:
            print("No drawable function to set")
    else:
        shared.smartdisplay.setDrawableArea(0,0,width,height) # else set full screen as drawable area.
    # show notice of the screen name we are loading.
    drawTimer.addGrowlNotice(ScreenNameToLoad,3000,drawTimer.nerd_yellow) 

def drawMouseBox():
    global pygamescreen
    x, y = pygame.mouse.get_pos()
    padding = 15
    pygame.draw.rect(pygamescreen, (drawTimer.red), (x-padding,y-padding,padding*2,padding*2),0)


# vi: modeline tabstop=8 expandtab shiftwidth=4 softtabstop=4 syntax=python
