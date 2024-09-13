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
    global debug_font
    # init common things.
    maxframerate = hud_utils.readConfigInt("Main", "maxframerate", 30)
    clock = pygame.time.Clock()
    pygame.time.set_timer(pygame.USEREVENT, 1000) # fire User events ever sec.
    debug_mode = 0
    debug_font = pygame.font.SysFont("monospace", 25, bold=False)

    exit_graphic_mode = False

    ##########################################
    # Main graphics draw loop
    while not shared.aircraft.errorFoundNeedToExit and not shared.aircraft.textMode and not exit_graphic_mode:
        clock.tick(maxframerate)
        for event in pygame.event.get():  # check for event like keyboard input.
            if event.type == pygame.QUIT:
                shared.aircraft.errorFoundNeedToExit = True
            # KEY MAPPINGS
            if event.type == pygame.KEYDOWN:
                mods = pygame.key.get_mods()
                if event.key == pygame.K_RIGHT and mods & pygame.KMOD_CTRL :
                    shared.CurrentInput.fastForward(shared.aircraft,500)
                    if(shared.CurrentInput2 != None): shared.CurrentInput2.fastForward(shared.aircraft,500)
                elif event.key == pygame.K_LEFT and mods & pygame.KMOD_CTRL :
                    shared.CurrentInput.fastBackwards(shared.aircraft,500)
                    if(shared.CurrentInput2 != None): shared.CurrentInput2.fastBackwards(shared.aircraft,500)
                elif event.key == pygame.K_p :
                    if(shared.CurrentInput.isPlaybackMode==True):
                        if(shared.CurrentInput.isPaused==False):
                            shared.CurrentInput.isPaused = True
                            print("Playback Paused!")
                            drawTimer.addGrowlNotice("Playback paused",1000,drawTimer.nerd_yellow,drawTimer.CENTER)
                        else:
                            shared.CurrentInput.isPaused = False
                            print("Plaback resumed.")
                            drawTimer.addGrowlNotice("Fullspeed ahead!",1000,drawTimer.nerd_yellow,drawTimer.CENTER)
                #### Press 1 - Start logging flight data
                elif (event.key == pygame.K_w and mods & pygame.KMOD_CTRL) or event.key == pygame.K_1 or event.key == pygame.K_KP1 :
                    try:
                        shared.CurrentInput.startLog(shared.aircraft)
                        drawTimer.addGrowlNotice("Log: %s"%(shared.CurrentInput.output_logFileName),3000,drawTimer.nerd_yellow,drawTimer.CENTER)
                        if(shared.CurrentInput2 != None): 
                            shared.CurrentInput2.startLog(shared.aircraft)
                            drawTimer.addGrowlNotice("Log2: %s"%(shared.CurrentInput2.output_logFileName),3000,drawTimer.nerd_yellow,drawTimer.BOTTOM_CENTER)
                    except :
                        drawTimer.addGrowlNotice("Unable to create log: "+shared.CurrentInput.name,3000,drawTimer.nerd_yellow,drawTimer.CENTER)
                #### Press 2 - Stop log
                elif (event.key == pygame.K_e and mods & pygame.KMOD_CTRL) or event.key == pygame.K_2 or event.key == pygame.K_KP2:
                    try:
                        Saved,SendingTo = shared.CurrentInput.stopLog(shared.aircraft)
                        drawTimer.addGrowlNotice("Log: %s"%(shared.CurrentInput.output_logFileName),3000,drawTimer.nerd_yellow,drawTimer.CENTER) 
                        if(shared.CurrentInput2 != None):
                            Saved,SendingTo = shared.CurrentInput2.stopLog(shared.aircraft)
                            drawTimer.addGrowlNotice("Log2: %s"%(shared.CurrentInput2.output_logFileName),3000,drawTimer.nerd_yellow,drawTimer.BOTTOM_CENTER) 
                        if(SendingTo!=None):
                            drawTimer.addGrowlNotice("Uploading to %s"%(SendingTo),3000,drawTimer.nerd_yellow,drawTimer.TOP_LEFT) 
                    except ValueError:
                        pass
                #### Press 3 - Cycle traffic modes.
                elif event.key == pygame.K_3 or event.key == pygame.K_KP3:
                    obj = MyEvent("modechange","traffic",-1)
                    shared.CurrentScreen.processEvent(obj,shared.aircraft,shared.smartdisplay)

                #### Press 4 - Drop target Buoy
                elif event.key == pygame.K_4 or event.key == pygame.K_KP4:
                    shared.aircraft.traffic.dropTargetBuoy(shared.aircraft,speed=-1)

                #### Press 5 - Drop target Buoy ahead of us.
                elif event.key == pygame.K_5 or event.key == pygame.K_KP5:
                    shared.aircraft.traffic.dropTargetBuoy(shared.aircraft,speed=-1, direction="ahead")

                #### Press 6 - Clear all Buouy targets
                elif event.key == pygame.K_6 or event.key == pygame.K_KP6 or (event.key == pygame.K_d and mods & pygame.KMOD_CTRL):
                    shared.aircraft.traffic.clearBuoyTargets()

                #### Enable debug graphics mode.
                elif event.key == pygame.K_7 or event.key == pygame.K_KP7 or (event.key == pygame.K_d and mods & pygame.KMOD_CTRL):
                    debug_mode += 1
                    if(debug_mode>5): debug_mode = 0
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
                elif event.key == pygame.K_e:
                    shared.aircraft.editMode = True
                    exit_graphic_mode = True
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
        if(shared.aircraft.inputs[1].PlayFile!=None):
            shared.smartdisplay.draw_text(shared.smartdisplay.LEFT_MID_UP, None, "PLAYBACK log2: %s" % (shared.aircraft.inputs[1].PlayFile), (255, 255, 0))
        if(shared.aircraft.inputs[0].PlayFile!=None):
            shared.smartdisplay.draw_text(shared.smartdisplay.LEFT_MID_UP, None, "PLAYBACK log1: %s" % (shared.aircraft.inputs[0].PlayFile), (255, 255, 0))
        shared.smartdisplay.draw_loop_done()

        if(debug_mode>0):
            draw_debug(debug_mode,shared.aircraft,shared.smartdisplay)

        #now make pygame update display.
        pygame.display.update()

    print("Exiting graphic mode.")

    # once exists main loop, close down pygame. and exit.
    # pygame.quit()
    # pygame.display.quit()

# used to pass along custom events to screens.
class MyEvent(object):
    def __init__(self, thetype,key,value):
        self.type = thetype
        self.key = key
        self.value = value

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
    drawableAreaString = hud_utils.readConfig("Main", "drawable_area", "")
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


    debug_font = 0
    last_debug_x = 0
    last_debug_y = 0

def draw_label_debug_value(key,value,postfix="",newline=False,precsion=4):
    global last_debug_x,last_debug_y,debug_font
    theType = type(value)
    if(value==None):
        showValue = "None"
    elif( theType is str):
        showValue = value
    elif( theType is int):
        showValue = str(value)
    elif( theType is float):
        if 'lat' in key.lower() or 'lon' in key.lower():  # if showing lat/lon then show all decimals.
            showValue = "%f" %(value)
        else:
            showValue = str(round(value,precsion))
    elif( theType is bool):
        showValue = str(value)
    elif( theType is bytes):
        showValue = str(value)
    elif( theType is bytearray):
        showValue = str(value)
    elif( isinstance(value, list)):
        # list
        if(len(value)>1):
            # if list of str,int,floats.. then print it out.
            if(isCustomObject(value[0])==False):
                showValue = str(value)
            else:
                # else it's a list of objects.. print out each obj.
                # skip
                return
        else:
            showValue = "[]"
    else :
        # else object.
        #showValue = "obj"
        return

    label = debug_font.render(key+":"+showValue+postfix, 1, (255, 255, 0),(0,0,0))
    label_rect = label.get_rect()

    if(newline==True):
        last_debug_x = 0
        last_debug_y += label_rect.height + 4
    else:
        # if we are at end of line.. goto next line.
        if(last_debug_x+label_rect.width >= shared.smartdisplay.x_end):
            last_debug_x = 0
            last_debug_y += label_rect.height + 4
            newline = False

    shared.smartdisplay.pygamescreen.blit(label, (last_debug_x, last_debug_y))

    last_debug_x += label_rect.width + 10


def draw_label_debug_title(title,newline=True):
    global last_debug_x,last_debug_y,debug_font

    label = debug_font.render(title, 1, (255, 255, 180),(0,0,0))
    label_rect = label.get_rect()

    if(newline==True):
        last_debug_x = 0
        last_debug_y += label_rect.height + 2
    else:
        # if we are at end of line.. goto next line.
        if(last_debug_x+label_rect.width >= shared.smartdisplay.x_end):
            last_debug_x = 0
            last_debug_y += label_rect.height + 4
            newline = False

    shared.smartdisplay.pygamescreen.blit(label, (last_debug_x, last_debug_y))

    last_debug_x += label_rect.width + 10


#############################################
## Function to print all object values.
def draw_debug_object(obj):
    count = 0
    for attr, value in list(vars(obj).items()):
        count += 1
        draw_label_debug_value(attr,value)


def draw_debug(debug_mode,aircraft,smartdisplay):
    global last_debug_x,last_debug_y,debug_font
    last_debug_x = 0
    last_debug_y = smartdisplay.y_start + 20

    if(debug_mode==1):
        draw_label_debug_title("Aircraft Object")
        draw_debug_object(aircraft)

    if(debug_mode==2):
        draw_label_debug_title("GPS  Object")
        draw_debug_object(aircraft.gps)

        draw_label_debug_title("Nav  Object")
        draw_debug_object(aircraft.nav)

    if(debug_mode==3):
        draw_label_debug_title("Traffic  Object")
        draw_debug_object(aircraft.traffic)
        count = 0
        for t in aircraft.traffic.targets:
            count += 1
            draw_label_debug_title(str(count))
            draw_debug_object(t)

    if(debug_mode==4):
        draw_label_debug_title("Engine  Object")
        draw_debug_object(aircraft.engine)
        draw_label_debug_title("Fuel  Object")
        draw_debug_object(aircraft.fuel)

    if(debug_mode==5):
        draw_label_debug_title("Input1")
        draw_debug_object(aircraft.inputs[0])
        draw_label_debug_title("Input2")
        draw_debug_object(aircraft.inputs[1])
        draw_label_debug_title("Internatl")
        draw_debug_object(aircraft.internal)

    smartdisplay.draw_text(smartdisplay.BOTTOM_RIGHT, debug_font, "%0.2f FPS" % (aircraft.fps), (255, 255, 0))



def isCustomObject(v):
    theType = type(v)
    if( theType is str):
        return False
    elif( theType is int):
        return False
    elif( theType is float):
        return False
    elif( theType is bool):
        return False
    elif( theType is bytes):
        return False
    elif( theType is bytearray):
        return False
    elif( isinstance(v, list)):
        return False
    else :
        return True


    # # render debug text
    # label = font.render("Pitch: %0.1f Roll: %0.1f" % (aircraft.pitch,aircraft.roll), 1, (255, 255, 0))
    # smartdisplay.pygamescreen.blit(label, (smartdisplay.x_start, smartdisplay.y_start+20))
    
    # label = font.render("IAS: %d mph  VSI: %d fpm gndspeed: %0.1f" % (aircraft.ias, aircraft.vsi,aircraft.gndspeed), 1, (255, 255, 0))
    # smartdisplay.pygamescreen.blit(label, (smartdisplay.x_start, smartdisplay.y_start+40))

    # label = font.render(
    #     "Alt: %d ft  PresALT:%d  BaroAlt:%d   AGL: %d"
    #     % (aircraft.alt, aircraft.PALT, aircraft.BALT, aircraft.agl),
    #     1,
    #     (255, 255, 0),
    # )
    # smartdisplay.pygamescreen.blit(label, (smartdisplay.x_start, smartdisplay.y_start+60))
    # if aircraft.aoa != None:
    #     label = font.render("AOA: %d" % (aircraft.aoa), 1, (255, 255, 0))
    #     smartdisplay.pygamescreen.blit(label, (smartdisplay.x_start, smartdisplay.y_start+80))
    # else:
    #     label = font.render("AOA: NA", 1, (255, 255, 0))
    #     smartdisplay.pygamescreen.blit(label, (smartdisplay.x_start, smartdisplay.y_start+80))
    # # Mag heading
    # label = font.render(
    #     "MagHead: %d  TrueTrack: %d" % (aircraft.mag_head, aircraft.gndtrack),
    #     1,
    #     (255, 255, 0),
    # )
    # smartdisplay.pygamescreen.blit(label, (smartdisplay.x_start, smartdisplay.y_start+100))
    # label = font.render(
    #     "Baro: %0.2f diff: %0.4f" % (aircraft.baro, aircraft.baro_diff),
    #     1,
    #     (20, 255, 0),
    # )
    # smartdisplay.pygamescreen.blit(label, (smartdisplay.x_start, smartdisplay.y_start+120))

    # label = font.render("time: %s msg count: %d msg bad: %d" % (aircraft.sys_time_string,aircraft.msg_count,aircraft.msg_bad), 1, (255, 255, 0))
    # smartdisplay.pygamescreen.blit(label, (smartdisplay.x_start, smartdisplay.y_start+140))

    # label = font.render("turn_rate: %0.2f  slip_skid: %0.2f" % (aircraft.turn_rate,aircraft.slip_skid), 1, (255, 255, 0))
    # smartdisplay.pygamescreen.blit(label, (smartdisplay.x_start, smartdisplay.y_start+160))

    # # print FPS on the bottom of screen.
    # smartdisplay.draw_text(smartdisplay.BOTTOM_RIGHT, font, "%0.2f FPS" % (aircraft.fps), (255, 255, 0))


# vi: modeline tabstop=8 expandtab shiftwidth=4 softtabstop=4 syntax=python
