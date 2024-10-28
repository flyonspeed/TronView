# TronView
Project for connecting efis/flight data to a 2nd screen or HUD.
![cockpit1](docs/efis_cockpit1.jpeg?raw=true)
## Active development! (Sept 2024!)
If you want to help with development or testing please join our [Join Discord](https://discord.gg/pdnxWa32aW) sever.
We are working on several new features. 
- XReal glasses support
- Editor to make creating or editing your own screen very easy.
- Better G3x support
- Show/Hide screen modules based on key commands or other inputs.

## Features Include:
- Build custom efis or hud screens
- Record and Playback flight log data ( and fast forward through playback )
- All screens look and work the same for all supported data input.
- All display screen sizes and ratios supported.
- Built in editor to make creating or editing your own screen.
- Text mode
- Touch screen support
- 30 + FPS on Raspberry Pi 4 
- Remote keypad / user input support.
- Display flight data in Knots, Standard, Metric, F or C
- Designed for Raspberry Pi 4/5 but also runs on Mac OSx, Windows, and other linux systems.
- Show NAV needles for approaches. (If NAV data is available)
- Use multiple data input sources, (MGL, G3x, Dynon, iLevil, stratux, Adafruit ADS1115, BNO055, BNO085, Generic Serial Logger)


# Quick Start for Raspberry Pi and Mac OS

[Quick Start for Raspberry Pi](docs/quick_start_raspberry_pi.MD)

[Quick Start for Mac OS](docs/quick_start_macos.MD)

## Use as backup display screen on dash

![cockpit2](docs/efis_cockpit2.jpeg?raw=true)

## Traditional EFIS looking screen
![screenshot1](docs/efis_screenshot.png?raw=true)

## F18 Style HUD
![hud_animation](docs/hud_animated_example.gif?raw=true)

![rv8Hud](docs/efis_HUD_rv8.jpg?raw=true)

## Text Mode
![hud_animation](docs/efis_screenshot_text.png?raw=true)


# About

This is a python3 application that will take in data from different input sources, process them into a common format, then output (draw) 
them to custom screens.  The system is created to have the inputs and screens seperate and non-dependent of each other.  
For example a user running a MGL iEFIS can run the same screen as a user with a Dynon D100.  Issues can come up with a input source does not 
have all the data available as other input sources do.  But if the screen is written well enough it will hide or show data if it's available.


## Currently supported input sources:

MGL iEFIS

Garmin G3x

Dynon Skyview

Dynon D10/100

Levil BOM (wifi)

Stratux or any stratux compatiable device (wifi)

IFR Navigator (Analog CDI) (ADS 1115)

BNO055 IMU (9DOF) and BNO085 (9DOF)

Generic serial logger (Used for recording any serial data)

We are using the rapberry pi 4B, or 5 for taking serial data from a EFIS (MGL,Dynon,G3x,etc) and displaying a graphical Display out the hdmi output on the pi.  This can be displayed on a screen (touchscreen, etc) or a HUD, or glasses.  

Code is written in Python 3.7 and the Pygame 2.0 module for handling the graphics.


# More details

Analog CDI from IFR Navigator: [input_analog.MD](https://github.com/flyonspeed/TronView/blob/master/lib/inputs/input_analog.MD)

Config example:  [config_example.cfg](https://github.com/flyonspeed/TronView/blob/master/config_example.cfg)

View demo data in the docs folder.
https://github.com/flyonspeed/TronView/blob/master/docs/efis_data.MD

IncludesF-18 style HUD screen: [screen_F18.MD](https://github.com/flyonspeed/TronView/blob/master/docs/screen_F18.MD)