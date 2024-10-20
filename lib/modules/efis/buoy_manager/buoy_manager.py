#!/usr/bin/env python

#################################################
# Module: Buoy Manager
# Topher 2024

from lib.modules._module import Module
from lib import hud_graphics
from lib import hud_utils
from lib import smartdisplay
from lib import aircraft
import pygame
import math
from lib.common import shared


class buoy_manager(Module):
    # called only when object is first created.
    def __init__(self):
        Module.__init__(self)
        self.name = "Buoy Manager"  # set name
        self.target_font_size = hud_utils.readConfigInt("HUD", "target_font_size", 20)
        self.buttons = []
        self.buoyDistance = 10
        self.buoyAlt = 0 # altitude above or below aircraft
        self.bottom = 0
        self.right = 0

    # called once for setup, or when module is being resized in editor
    def initMod(self, pygamescreen, width=None, height=None):
        if width is None:
            width = 120 # default width
        if height is None:
            height = 100 # default height
        Module.initMod(
            self, pygamescreen, width, height
        )  # call parent init screen.
        if shared.aircraft.debug_mode > 0:
            print(("Init Mod: %s %dx%d"%(self.name,self.width,self.height)))

        self.buttons = []

        # fonts
        self.font_target = pygame.font.SysFont("Monospace", self.target_font_size)
        # Create a surface with per-pixel alpha
        self.surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)

        # create buttons
        self.addButton("addBuoy", "Add Buoy", self.addBuoy)
        self.addButton("Label_dist", "Set Distance:", newRow=True, type="label")
        self.addButton("setDistance_1",  "1", self.setDistance, newRow=True)
        self.addButton("setDistance_2",  "2", self.setDistance)
        self.addButton("setDistance_3",  "3", self.setDistance)
        self.addButton("setDistance_5",  "5", self.setDistance)
        self.addButton("setDistance_10", "10", self.setDistance)
        self.addButton("setDistance_20", "20", self.setDistance)
        self.addButton("setDistance_30", "30", self.setDistance)
        self.addButton("setDistance_40", "40", self.setDistance)
        self.addButton("setDistance_50", "50", self.setDistance)
        # go through the buttons and find the setDistance_ with value self.buoyDistance and set it to selected.
        for b in self.buttons:
            if b["id"].startswith("setDistance_") and int(b["text"]) == self.buoyDistance:
                b["selected"] = True

        # set altitude buttons
        self.addButton("Label_alt", "Set Altitude:", newRow=True, type="label")
        self.addButton("setAlt_-2000", "-2000", self.setAlt, newRow=True)
        self.addButton("setAlt_-1000", "-1000", self.setAlt)
        self.addButton("setAlt_-500", "-500", self.setAlt)
        self.addButton("setAlt_-100", "-100", self.setAlt)
        self.addButton("setAlt_0", "0", self.setAlt)
        self.addButton("setAlt_100", "100", self.setAlt, newRow=True)
        self.addButton("setAlt_500", "500", self.setAlt)
        self.addButton("setAlt_1000", "1000", self.setAlt)
        self.addButton("setAlt_2000", "2000", self.setAlt)
        # go through the buttons and find the setAlt_ with value self.buoyAlt and set it to selected.
        for b in self.buttons:
            if b["id"].startswith("setAlt_") and int(b["text"]) == self.buoyAlt:
                b["selected"] = True

    # called every redraw for the module
    def draw(self, aircraft, smartdisplay, pos=(0, 0)):
        # Clear the surface with full transparency
        self.surface.fill((0, 0, 0, 0))

        # draw buttons
        last_y = 0
        for button in self.buttons: 
            if button["selected"]:
                color = (0,200,0)
                text_color = (0,0,0)
            else:
                color = (50,50,50)
                text_color = (200,200,200)
            if button["draw_background"]:
                pygame.draw.rect(self.surface, color, (button["x"], button["y"], button["width"], button["height"]), 0, border_radius=5)
            # draw text
            text = self.font_target.render(button["text"], True, text_color)
            self.surface.blit(text, (button["x"] + (button["width"]/2 - text.get_width()/2), button["y"] + (button["height"]/2 - text.get_height()/2)))
            last_y = button["y"] + button["height"]

        # draw text at the bottom of the module
        text = self.font_target.render("Buoys: "+str(aircraft.traffic.buoyCount), True, (200,200,200))
        self.surface.blit(text, (10, last_y + 10))

        # Use alpha blending when blitting to the screen
        smartdisplay.pygamescreen.blit(self.surface, pos, special_flags=pygame.BLEND_ALPHA_SDL2)

    ##########################################################
    # add a button to the module
    ##########################################################
    def addButton(self, id, text, function = None, x=-1, y=-1, width=0, height=30, newRow=False, center=False, selected=False, type="button"):
        # Calculate the button width based on text if width is 0
        label_width = self.font_target.size(text)[0]
        if width == 0:
            width = label_width + 10  # Add 5px padding on each side
        else:
            width = max(width, label_width + 10)  # Ensure the width is at least as wide as the text plus padding

        # Find the last button's position
        last_button = None if len(self.buttons) == 0 else self.buttons[-1]

        # Handle newRow
        if newRow:
            y = (last_button['y'] + last_button['height'] + 10) if last_button else 10
            x = 10
        else:
            if last_button:
                x = last_button['x'] + last_button['width'] + 10
                y = last_button['y']
            else:
                x = 10
                y = 10

        # Handle centering
        if center:
            row_buttons = [b for b in self.buttons if b['y'] == y]
            row_width = sum(b['width'] for b in row_buttons) + width + ((len(row_buttons) + 1) * 10)
            x = (self.width - row_width) / 2 + sum(b['width'] for b in row_buttons) + (len(row_buttons) * 10)

        if type == "label":
            draw_background = False
        else:
            draw_background = True

        button = {  
            "id": id,
            "x": x,
            "y": y,
            "width": width,
            "height": height,
            "text": text,
            "function": function,
            "selected": False,
            "center": center,
            "newRow": newRow,
            "type": type,
            "draw_background": draw_background
        }
        self.buttons.append(button)

        # Update the bottom-right coordinates
        self.bottom = max(self.bottom, y + height)
        self.right = max(self.right, x + width)

    def clear(self):
        #self.ahrs_bg.fill((0, 0, 0))  # clear screen
        print("clear")

    # handle mouse clicks
    def processClick(self, aircraft, mx, my):
        for button in self.buttons:
            if button["x"] <= mx <= button["x"] + button["width"] and button["y"] <= my <= button["y"] + button["height"]:
                if button["function"]:
                    button["function"]( aircraft, button )


    def addBuoy(self,aircraft,button):
        print("adding buoy at distance ", self.buoyDistance, " and altitude ", self.buoyAlt)
        aircraft.traffic.dropTargetBuoy(aircraft,distance=self.buoyDistance,direction="ahead",alt=self.buoyAlt)

    def setDistance(self,aircraft,button):
        #print("setDistance clicked")
        # unselect all buttons that start with setDistance_
        for b in self.buttons:
            if b["id"].startswith("setDistance_"):
                b["selected"] = False
        # select the button that was clicked
        button["selected"] = True
        self.buoyDistance = int(button["text"])

    def setAlt(self,aircraft,button):
        #print("setAlt clicked")
        # unselect all buttons that start with setAlt_
        for b in self.buttons:
            if b["id"].startswith("setAlt_"):
                b["selected"] = False
        # select the button that was clicked
        button["selected"] = True
        self.buoyAlt = int(button["text"])

    # return a dict of objects that are used to configure the module.
    def get_module_options(self):
        # each item in the dict represents a configuration option.  These are variable in this class that are exposed to the user to edit.
        return {
            "target_font_size": {
                "type": "int",
                "default": self.target_font_size,
                "min": 10,
                "max": 100,
                "label": "Target Font Size",
                "description": "Font size for target labels",
                "post_change_function": "fontSizeChanged"
            },
            "buoyDistance": {  # This is here so it will get saved to the screen file.  But we don't want to show it in the options bar.
                "type": "int",
                "default": self.buoyDistance,
                "min": 1,
                "max": 50,
                "label": "Buoy Distance",
                "description": "Distance to drop the buoy",
                "hidden": True
            },
            "buoyAlt": {     # This is here so it will get saved to the screen file.
                "type": "int",
                "default": self.buoyAlt,
                "min": -2000,
                "max": 2000,
                "label": "Buoy Altitude",
                "description": "Altitude to drop the buoy",
                "hidden": True
            }
        }

    def fontSizeChanged(self):
        self.initMod(self.pygamescreen, self.width, self.height)

    def changeHappened(self):
        self.initMod(self.pygamescreen, self.width, self.height)

# vi: modeline tabstop=8 expandtab shiftwidth=4 softtabstop=4 syntax=python
