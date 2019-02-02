#!/usr/bin/env python

# Input class.
# All input types should inherit from this class.

from lib import hud_text

class Input:
    def __init__(self):
        self.name = "Input Class"
        self.version = 1.0
        self.inputtype = ""

    def initInput(self, aircraft):
        print("init input parent")


# vi: modeline tabstop=8 expandtab shiftwidth=4 softtabstop=4 syntax=python
