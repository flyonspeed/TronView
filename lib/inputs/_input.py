#!/usr/bin/env python

# Input class.
# All input types should inherit from this class.

from lib import hud_text

class Input:
    def __init__(self):
        self.name = "Input Class"
        self.version = 1.0
        self.inputtype = ""

    def initInput(self, inputtype):
        print("init input parent")
        self.inputtype = inputtype
        efis_data_format = hud_utils.readConfig("DataInput", "format", "none")
        efis_data_port = hud_utils.readConfig("DataInput", "port", "/dev/ttyS0")
        efis_data_baudrate = hud_utils.readConfigInt("DataInput", "baudrate", 115200)

        # open serial connection.
        ser = serial.Serial(
            port=efis_data_port,
            baudrate=efis_data_baudrate,
            parity=serial.PARITY_NONE,
            stopbits=serial.STOPBITS_ONE,
            bytesize=serial.EIGHTBITS,
            timeout=1,
        )


# vi: modeline tabstop=8 expandtab shiftwidth=4 softtabstop=4 syntax=python
