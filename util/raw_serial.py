#!/usr/bin/env python


import time
import serial
import struct
import sys
import os, getopt, subprocess, platform

version = "0.1"

ser = None
counter = 0

def list_serial_ports(printthem):

    # List all the Serial COM Ports on Raspberry Pi
    proc = subprocess.Popen(['ls /dev/tty[A-Za-z]*'], shell=True, stdout=subprocess.PIPE)
    com_ports = proc.communicate()[0]
    com_ports_list = str(com_ports).split("\\n") # find serial ports
    rtn = []
    for com_port in com_ports_list:
        if 'ttyS' in com_port:
            if(printthem==True): print("found serial port: "+com_port)
            rtn.append(com_port)
        if 'ttyUSB' in com_port:
            if(printthem==True): print("found serial port: "+com_port)
            rtn.append(com_port)
    return rtn


# print at location
def print_xy(x, y, text):
    sys.stdout.write("\x1b7\x1b[%d;%df%s\x1b8" % (x, y, text))
    sys.stdout.flush()


def readMessage():
    global ser
    try:
        t = ser.read(1)
        if(len(t)>0):
            if int(t[0]) < 32:  # if its binary then convert it to string first.
                x = str(t)
            else:
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
port = "/dev/ttyS0"  # default serial port
try:
    opts, args = getopt.getopt(argv, "hbi:l", ["bin="])
except getopt.GetoptError:
    print("raw_serial.py -b")
    sys.exit(2)
for opt, arg in opts:
    if opt == "-h":
        print("raw_serial.py [-i <serial port>] -l")
        print(" -l (list serial ports found)")
        print(" -i select input serial port")
        sys.exit()
    if opt == "-i":
        port=arg
    if opt == "-l":
        list_serial_ports(True)
        sys.exit()

try:
    ser=serial.Serial(
        port=port,
        baudrate=115200,
        parity=serial.PARITY_NONE,
        stopbits=serial.STOPBITS_ONE,
        bytesize=serial.EIGHTBITS,
        timeout=1,
    )

except:
    print("Unable to open serial port: "+port)
    print("Here is a list of ports found:")
    list_serial_ports(True)
    sys.exit()
print("Opened port: "+port+ " @115200 baud (cntrl-c to quit)")
while 1:
    readMessage()

