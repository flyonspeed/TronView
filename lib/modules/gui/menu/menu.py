#!/usr/bin/env python

#################################################
# Module: Menu
# Topher 2021.

from lib.modules._module import Module
from lib import hud_graphics
from lib import hud_utils
from lib import smartdisplay
from lib import aircraft
import pygame
import math
import pygame_menu
from typing import Tuple, Any

class menu(Module):
    # called only when object is first created.
    def __init__(self):
        Module.__init__(self)
        self.name = "Menu"  # set name

    # called once for setup
    def initMod(self, pygamescreen, width, height,title):
        Module.initMod(
            self, pygamescreen, width, height
        )  # call parent init screen.
        print(("Init Mod: %s %dx%d"%(self.name,self.width,self.height)))

        self.menu = pygame_menu.Menu(title, self.width, self.height,
                               theme=pygame_menu.themes.THEME_BLUE)

        #self.menu.add.text_input('Name :', default='John Doe')
        #self.menu.add.selector('Difficulty :', [('Hard', 1), ('Easy', 2)], onchange=self.set_difficulty)
        self.menu.add.button('Back', self.stop)
        self.menu.add.button('Quit', pygame_menu.events.EXIT)


    def set_difficulty(self, selected: Tuple, value: Any) -> None:
        print('Set difficulty to {} ({})'.format(selected[0], value))

    def stop(self):
        self.menu.disable()

    # called every redraw for the mod
    def draw(self, aircraft, smartdisplay):

        print("draw menu")

        self.menu.enable()
        self.menu.mainloop(smartdisplay.pygamescreen)

    # called before screen draw.  To clear the screen to your favorite color.
    def clear(self):
        pass

    # handle key events
    def processEvent(self, event):
        pass


# vi: modeline tabstop=8 expandtab shiftwidth=4 softtabstop=4 syntax=python
