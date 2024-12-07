#!/usr/bin/env python

# i2c test

import time
import math
import binascii
import traceback
import board
import busio

# Normal I2C initialization
i2c = busio.I2C(board.SCL, board.SDA)

# scan for devices
devices = i2c.scan()
print("Devices addresses found:", devices)

# 40 is bno055
if 40 in devices:
    print("BNO055 (1st imu gyro) found (hex: 0x{:02X} decimal: {:02})".format(40, 40))

# 41 is 2nd bno055
if 41 in devices:
    print("BNO055 (2nd imu gyro) found (hex: 0x{:02X} decimal: {:02})".format(41, 41))

# 64 is INA3221 (current sensor)
if 64 in devices:
    print("INA3221 (current sensor) found (hex: 0x{:02X} decimal: {:02})".format(64, 64))

# check if 72. (ads1115) analog voltage sensor
if 72 in devices:
    print("ADS1115 (analog voltage sensor) found (hex: 0x{:02X} decimal: {:02})".format(72, 72))

# 74 is bno085
if 74 in devices:
    print("BNO085 (1st imu gyro) found (hex: 0x{:02X} decimal: {:02})".format(74, 74))

# 75 is 2nd bno085
if 75 in devices:
    print("BNO085 (2nd imu gyro) found (hex: 0x{:02X} decimal: {:02})".format(75, 75))

# 92 LPS28
if 92 in devices:
    print("LPS28 (pressure sensor) found (hex: 0x{:02X} decimal: {:02})".format(92, 92))

# 93 LSP22 (pressure sensor)
if 93 in devices:
    print("LSP22 (pressure sensor) found (hex: 0x{:02X} decimal: {:02})".format(93, 93))

# 104 is mcp3421
if 104 in devices:
    print("MCP3421 (voltage sensor) found (hex: 0x{:02X} decimal: {:02})".format(104, 104))

