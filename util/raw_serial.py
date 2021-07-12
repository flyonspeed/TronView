#!/usr/bin/env python


import time
import serial
import struct
import sys
import os, getopt

version = "0.1"

ser = serial.Serial(
    # port="/dev/ttyUSB0",
    port="/dev/ttyS0",
    baudrate=115200,
    parity=serial.PARITY_NONE,
    stopbits=serial.STOPBITS_ONE,
    bytesize=serial.EIGHTBITS,
    timeout=1,
)
counter = 0

# print at location
def print_xy(x, y, text):
    sys.stdout.write("\x1b7\x1b[%d;%df%s\x1b8" % (x, y, text))
    sys.stdout.flush()


def readMessage(showBin):
    global ser
    try:
        if showBin == 1:
            t = ser.read(1)  
            x = str(t)
        else:
            t = ser.read(1).decode()
            x = t

        print(x, end=" ")

    except serial.serialutil.SerialException:
        print("exception")

if sys.platform.startswith('win'):
    os.system('cls')  # on windows
else:
    os.system("clear")  # on Linux / os X
argv = sys.argv[1:]
showBin = 0
try:
    opts, args = getopt.getopt(argv, "hb", ["bin="])
except getopt.GetoptError:
    print("raw_serial.py -b")
    sys.exit(2)
for opt, arg in opts:
    if opt == "-h":
        print("raw_serial.py <options>")
        print(" -b (show binary)")
        sys.exit()
    elif opt == "-b":
        showBin = 1


while 1:
    readMessage(showBin)

