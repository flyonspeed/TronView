#!/usr/bin/env python

#################################################
# Module: Play Controls
# Topher 2024

from lib.modules._module import Module
from lib import hud_graphics
from lib import hud_utils
from lib import smartdisplay
from lib.common.dataship import dataship
import pygame
import math
from lib.common import shared


class play_controls(Module):
    # called only when object is first created.
    def __init__(self):
        Module.__init__(self)
        self.name = "Play Controls"  # set name
        self.buoyDistance = 10
        self.buoyAlt = 0 # altitude above or below aircraft

    # called once for setup, or when module is being resized in editor
    def initMod(self, pygamescreen, width=None, height=None):
        if width is None:
            width = 120 # default width
        if height is None:
            height = 100 # default height
        Module.initMod( self, pygamescreen, width, height )  # call parent init screen.
        if shared.Dataship.debug_mode > 0:
            print(("Init Mod: %s %dx%d"%(self.name,self.width,self.height)))

        self.buttonsInit()
        # Create a surface with per-pixel alpha
        self.surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)

        # create buttons
        self.buttonAdd("btnFastBackwards1", "<<", self.buttonFastBackwards)
        self.buttonAdd("btnFastBackwards2", "<", self.buttonFastBackwards)
        self.buttonAdd("btnPlay", "Play", self.buttonPlay)
        self.buttonAdd("btnFastForward1", ">", self.buttonFastForward)
        self.buttonAdd("btnFastForward2", ">>", self.buttonFastForward)
        self.buttonAdd("btnRecord", "REC", self.buttonRecord)
        
        #self.buttonAdd("Label_dist", "PlayBack:", newRow=True, type="label")
        #self.buttonAdd("test",  "Test", self.buttonPlay, newRow=True)

        self.buttonSelected("btnPlay",not shared.Inputs[0].isPaused) # set the button to selected
        self.buttonSelected("btnRecord",shared.Inputs[0].output_logFile != None)

    # called every redraw for the module
    def draw(self, aircraft: dataship, smartdisplay, pos=(0, 0)):
        # Clear the surface with full transparency
        self.surface.fill((0, 0, 0, 0))
        self.buttonsDraw(aircraft, smartdisplay, pos)  # draw buttons

        # next_line = self.buttonLastY + 10
        # for input in aircraft.inputs:
        #     text = self.button_font.render(input.name, True, (200,200,200))
        #     self.surface.blit(text, (10, next_line))
        #     next_line += text.get_height() + 5

        # # draw text at the bottom of the module (use the button font from the parent class)
        # text = self.button_font.render("Buoys: "+str(aircraft.traffic.buoyCount), True, (200,200,200))
        # self.surface.blit(text, (10, self.buttonLastY + 10))

        # Use alpha blending when blitting to the screen
        smartdisplay.pygamescreen.blit(self.surface, pos, special_flags=pygame.BLEND_ALPHA_SDL2)


    # handle mouse clicks
    def processClick(self, aircraft: dataship, mx, my):
        self.buttonsCheckClick(aircraft, mx, my) # call parent.

    # button to play the scenario
    def buttonPlay(self,aircraft,button):
        shared.Inputs[0].isPaused = not shared.Inputs[0].isPaused
        self.buttonSelected("btnPlay",not shared.Inputs[0].isPaused) # set the button to selected
        if len(shared.Inputs) > 1:
            shared.Inputs[1].isPaused = not shared.Inputs[1].isPaused

    def buttonFastForward(self,aircraft,button):
        if button["text"] == ">>":
            shared.Inputs[0].fastForward(shared.Dataship,1000)
            if len(shared.Inputs) > 1:
                shared.Inputs[1].fastForward(shared.Dataship,1000)
        else:
            shared.Inputs[0].fastForward(shared.Dataship,500)
            if len(shared.Inputs) > 1:
                shared.Inputs[1].fastForward(shared.Dataship,500)

    def buttonFastBackwards(self,aircraft,button):
        if button["text"] == "<<":
            shared.Inputs[0].fastBackwards(shared.Dataship,1000)
            if len(shared.Inputs) > 1:
                shared.Inputs[1].fastBackwards(shared.Dataship,1000)
        else:
            shared.Inputs[0].fastBackwards(shared.Dataship,500)
            if len(shared.Inputs) > 1:
                shared.Inputs[1].fastBackwards(shared.Dataship,500)

    def buttonRecord(self,aircraft,button):
        if shared.Inputs[0].output_logFile == None:
            shared.Inputs[0].startLog(shared.Dataship)
            self.buttonSelected("btnRecord",True)
        else:
            shared.Inputs[0].stopLog(shared.Dataship)
            self.buttonSelected("btnRecord",False)
        if len(shared.Inputs) > 1: # check if there is a second input
            if shared.Inputs[1].output_logFile == None:
                shared.Inputs[1].startLog(shared.Dataship)
            else:
                shared.Inputs[1].stopLog(shared.Dataship)

    # return a dict of objects that are used to configure the module.
    def get_module_options(self):
        # each item in the dict represents a configuration option.  These are variable in this class that are exposed to the user to edit.
        return {
            "button_font_size": {
                "type": "int",
                "default": self.button_font_size,
                "min": 10,
                "max": 100,
                "label": "Button Font Size",
                "description": "Font size for buttons",
                "post_change_function": "fontSizeChanged"
            },
        }

    def fontSizeChanged(self):
        self.initMod(self.pygamescreen, self.width, self.height)


# vi: modeline tabstop=8 expandtab shiftwidth=4 softtabstop=4 syntax=python
