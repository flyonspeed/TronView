# TronView
Project for connecting efis/flight data to a 2nd screen or HUD (Heads Up Display)

## Features Include:
- Supports serial from MGL, Garmin G3x, Dynon Skyview & D100.
- Supports wifi from Stratux, iLevil BOM, iLevil 3, uAvionix Echo UAT, Dual XGPS190, Dynon ADSB wifi, etc.
- Build custom efis or hud screens
- Record and Playback flight log data to external usb drive (fast forward playback avail)
- All screens look and work the same for all supported data input.
- All display screen sizes and ratios supported. (set through config)
- Touch screen support
- 30 + FPS on Raspberry Pi 4 
- Remote keypad / user input support. (USB 10-key number pad works good)
- Display flight data in Knots, Standard, Metric, F or C (set in config)
- Designed for Raspberry Pi but also runs on Mac OSx, Windows, and other linux systems.
- Show NAV needles for approaches. (If NAV data is available)
- Use multiple data sources (IE. Serial and Wifi at the same time)
- Shows traffic as scope or target flags (When traffic source input available)
- User dropped buoy targets for virtual dogfighting
- Text mode (Helpful to see raw data values during playback)
- Now updated to Python 3!

## Example of HUD in Vans RV-8
![cockpithud1](docs/efis_HUD_rv8.jpg?raw=true)


## Use as backup display screen on dash
![cockpit1](docs/efis_cockpit1.jpeg?raw=true)
![cockpit2](docs/efis_cockpit2.jpeg?raw=true)


## Traditional EFIS looking screen
![screenshot1](docs/efis_screenshot.png?raw=true)


## F18 Style HUD
![hud_animation](docs/hud_animated_example.gif?raw=true)


## Text Mode
![hud_animation](docs/efis_screenshot_text.png?raw=true)


# About

This is a python3 application that will take in data from different input sources, process them into a common format, then output (draw) them to custom screens (HUD or efis style).  The system is created to have the inputs and screens seperate and non-dependent of each other.  For example a user running a MGL iEFIS can run the same screen as a user with a Dynon D100.  Issues can come up with a input source does not have all the data available as other input sources do.  But if the screen is written well enough it will hide or show data if it's available.


## Currently supports:

MGL iEFIS

Garmin G3x

Dynon Skyview

Dynon D10/100

Levil BOM , uAvionix Echo UAT, and other Stratux wifi compatiable devices (Uses wifi connection)


We are using the rapberry pi 4B for taking serial data from a EFIS (MGL,Dynon,G3x) and displaying a graphical Display out the hdmi output on the pi.  This is plugged into a Display or HUD device like the Hudly Classic.  Any sort of HDMI screen could be hooked to the Pi for displaying this flight data.

Code is written in Python 3.7 and the Pygame 2.0 module for handling the graphics.

You can run this code in either raspbian full or lite.

Raspbian full install contains the xwindow desktop system.  The lite version does not.
This supports both versions.

Get raspbian-stretch-lite SD image for pi. Latest can be gotten here.
https://downloads.raspberrypi.org/raspbian_lite_latest

Following install guide if you need help.  https://www.raspberrypi.org/documentation/installation/installing-images/README.md

Setup your serial input using the GPIO pins on pi zero.  This page will help you. https://www.instructables.com/id/Read-and-write-from-serial-port-with-Raspberry-Pi/

## Steps to get the software running on raspberry pi

1) WIFI and autologin. You’ll want to get the pi on your wifi network so it can download the latest source.  Here are some instructions online that might help.  https://www.raspberrypi.org/documentation/configuration/wireless/wireless-cli.md

To setup auto login. (so you don't have to login to pi every time it boots up)

Enter the command `sudo raspi-config` Scroll down to Boot Options and select Console Autologin. Then exit the configuration menu and reboot.

2) Install git command.   This will let you get the latest source from github directly onto the pi.

`sudo apt-get -y install git`

3) clone the source from github

`git clone https://github.com/flyonspeed/TronView.git`

this will ask for username/email password from github.

when done this will create a TronView dir

4) run the setup.sh script to finish install.  This will setup serial port (if not allready setup), and install python libraries needed.

go into the TronView by typing

`cd TronView/util`

then to run the script type

`./setup.sh`

5) reboot the device.  type

`reboot`

6) Test the hud/efis screen with existing example data.  
run the following.  First make sure you are in the efis_hud dir.

`cd TronView`

Then run the python script and use the example data for dynon d100.

`sudo python main.py -i serial_d100 -e`

You should see a basic hud on the screen.  And it slowy moving around.  
If not then your video setup maybe be F'd up.  

To exit you hit "q" on the keyboard.


7a) Next if you want to run live serial data from your efis.
run the serial_read.py script to confirm data being sent is correct.
go into TronView dir then type

`cd TronView`

`sudo python util/serial_read.py`

you will have to pass in -m or -s for mgl or skyview data.

make sure the data is coming through and looks good.

to exit hit cntrl-c

7b) run it

Note:  You have to run using sudo in order to get access to serial port.

Example:

`sudo python3 main.py -i serial_mgl`

will show you command line arguments.

`-i {input data source 1}` 

load a input module for where to get the air data from. 

--in1 {input source 1} (same as -i)

--in2 {input source 2} 

-s (optional) {screen module name to load} (located in the lib/screens folder)

-t (optional) start up in text mode

-e (optional) demo mode. load default example demo data for input source selected.

-c FILENAME (optional) custom playback file. Enter filename of custom example demo file to use.

--playfile1 (optional) same as -c.. set playback file for input 1

--playfile2 (optional) set playback file for input 2

--listlogs (optional) show logs you saved. location id defined in config.cfg

--listusblogs (optional) show logs saved to usb drive (if available)

-- listexamplelogs (optional) show example log files to playback


Run the command with no arguments and it will show you which input modules and screen modules are available to use.

`sudo python main.py`

## More help on raspberry pi.

Here are more instructions on setting up for raspberry pi.

https://github.com/flyonspeed/TronView/blob/master/docs/rpi_setup.md

## DefaultScreen

The default screen has the following keyboard commands.

current commands are:

q - quit

t - switch to text mode  ( can not switch back to graphic mode after you enter text mode )

p - pause/unpause play back of log file (only if you are playing back a log file)

cntrl right arrow - fast forward play back file.

cntrl left arrow - rewind play back file (currently doesn't really work great)

cntrl d - show some debug info (same as using the number 7 key)

1 - create flight data log file

2 - close flight data log file

3 - cylce through traffic scope modes and ranges (if traffic input source available)

4 - drop target buoy at current location and altitude.  Will be visiable on traffic scope

5 - drop target buoy exactly 1 mile ahead of aircraft heading.

6 - clear all target buoys.

7 - cycle through debug modes (in graphic mode)

PAGE UP - jump to next screen

PAGE DOWN - go to previous screen

To run with


## Creating your own custom screen file

Screen files are located in lib/screens folder.  For a quick start you can duplicate the DefaultScreen.py file and rename it to your own.  What ever name you give it you must name the Class in that file to the same name.  For exmaple if I create MyHud.py then in that file I must set the class to the following

`class MyHud(Screen):`


Functions for custom screens:

### initDisplay(self,pygamescreen,width,height):

this is called once on screen init and tells your class the screen width and height

### draw(self,aircraft):

draw() is called in the main draw loop.  And the current aircraft object is passed in with all current postion values.

### clearScreen(self):

each time the screen is drawn it first has to clear it.  this is called to do that.

### processEvent(self,event):

handles events like key presses.

## Creating your own Input source module

Input sources are located in lib/inputs folder.  Create your own!  You can use existing modules as examples for how to do this.


## Screen resolution for hudly


1.        Type “sudo raspi-config”
2.        Select "Advanced options"
3.        Select A5 – Resolution  (Screen)  -> Select “CEA Mode 3  720x480  60 Hz  16:9”
6.        Select “OK”
7.        Select:  "Finish"
8.        Select:  "Yes"
9.        Wait for the reboot



## config.cfg

config.cfg can be created and sit in the same dir as the main.py python app.  It's used for configuring the hud.  View config_example.cfg for a example of options.

Here is a example config.cfg file:

<pre>

[Main]
#when running in xwindows,mac,win this will show hud in window if set.
window=640,480

# define the drawable area for hud to use.  Useful on displays that have hidden areas.
# this is defined as x1,y1,x2,y2 to draw up a box of usable area.
#drawable_area=0,144,1280,624
#For Epic HUD use the following
#drawable_area=0,159,1280,651

# Show Mouse? set to true if you want to show the mouse. Defaults to false
#showMouse = true

#Which screen to run on startup.. "Default" screen is used if nothing entered.
#screen = Default

# Set max frame rate. defaults to 30 
#maxframerate = 30

# Ignore any traffic targets beyond a given distance in miles (defaults to importing all traffic into aircraft traffic object)
#ignore_traffic_beyond_distance = 5

[DataInput]
# input source of data. These modules are located in lib/inputs. 
inputsource = serial_d100
#inputsource = serial_skyview
#inputsource = serial_mgl
#inputsource = serial_g3x
#inputsource = levil_wifi
#inputsource = serial_logger
#inputsource = stratux_wifi


# port name for serial input. Default is /dev/ttyS0, for Windows you need to know the COM port you want to use ie: COM1, COM2, etc.
# rpi built in serial is /dev/ttyS0
# rpi usb serial is /dev/ttyUSB0
port = /dev/ttyS0 

# baud rate. Default is 115200
# set this to the baud rate of your efis output.
baudrate = 115200 

[DataInput2]
# set this to use a 2nd data input source
# 2nd input source will overwrite the data from the 1st source (if data exists)
#inputsource = stratux_wifi

[Stratux]
# To ignore ahrs data from stratux set use_ahrs=false, defaults to true
#use_ahrs = false

# set UPD port for network input.. defaults to 4000
#udpport = 4000

[Formats]
# Set speed and distance to Knots, Standard, Metric (default is Standard)
#speed_distance = Metric 
# Set temperate to F or C (defaults to F)
#temperature = C

[DataRecorder]
# change the path were the default flight log files are saved. Make sure this dir exists.
# default path is /flightlog/
#path = /home/pi/flightlog/

# check if usb drive is available for creating log files?
# defaults to true
#check_usb_drive = True

</pre>

# Demo Sample EFIS Data

  Demo data is saved in lib/inputs/_example_data .  Demo data lets you run previously recorded data through the hud app for demo or testing purposes.  Each input source module uses it's own format for data.  So for example if you want to run dynon demo data then you must run it through the dynon input source module.
  
  Using the -c FILENAME command line option loads data from the _example_data folder.
  
  Example to run the MGL_V2.bin demo data file would look like this:
  
  `sudo python main.py -i serial_mgl -c MGL_V2.bin`


# Stratux Data (Also works as iLevil BOM data)

  stratux_1.dat = basic stratux data with traffic

# MGL Data

  MGL EFIS Sample Data Link: https://drive.google.com/open?id=1mPOmQuIT-Q5IvIoVmyfRCtvBxCsLUuvz

  MGL EFIS Serial Protocol Link: https://drive.google.com/open?id=1OYj000ghHJqSfvacaHMO-jOcfd1raoVo

  MGL example data in this git repo include: (they can be ran by using the -c <filename> command line option.)

  MGL_V2.bin = G430_Bit_Test_24Mar19
  
  MGL_V3.bin = G430_Data_3Feb19_VertNdlFullUp_HzNdl_SltRt_toCtr
  
  MGL_V4.bin = G430_Data_3Feb19_HSI_Nedl_2degsRt_Vert_SlightLow
  
  MGL_V5.bin = G430_Data_3Feb19_HSI_Nedl_2degsLft_Vert_2Degs_Dwn
  
  MGL_V6.bin = G430_Data_3Feb19_HSI_Nedl_2degsRt_Vert_2Degs_Up
  
  MGL_V7.bin = G430_Data_3Feb19_Horz_Vert_Nedl_come to center
  
  MGL_V8.bin = G430_Data_13Ap19_VertNdlFullDwn_HzNdl_FullLft
  
  MGL_V9.bin = 13Ap_AltBug_0_500_1k_1.5k_to_10k_5.1K_5.2k_5.9kv10_v10
  
  MGL_V10.bin = 13Ap_XC_Nav 
  
  MGL_V11.bin = iEfis_NavDataCapture_5Feb19
  
  MGL_V12.bin = NavData_13Ap_HdgBug_360_10_20_30_to_360_001_002_003_to_010_v9

# Dynon Data

  Dynon Skyview EFIS Sample Data Link: https://drive.google.com/open?id=1jQ0q4wkq31C7BRn7qzMSMClqPw1Opwnp

  Dynon Skyview EFIS Serial Protocol Link: https://drive.google.com/open?id=1isurAOIiTzki4nh59lg6IDsy1XcsJqoG
  
  Dynon D100 Series EFIS Sample Data Link: https://drive.google.com/open?id=1_os-xv0Cv0AGFVypLfSeg6ucGv5lwDVj
  
  Dynon D100 Series EFIS Serial Protocol Link: https://drive.google.com/open?id=1vUBMJZC3W85fBu33ObuurYx81kj09rqE

# Garmin Data

  Garmin G3X EFIS Sample Data Link: https://drive.google.com/open?id=1gHPC3OipAs9K06wj5zMw_uXn3_iqZriS

  Garmin G3X EFIS Serial Protocol Link: https://drive.google.com/open?id=1uRRO-wdG7ya6_6-CfDVrZaKJsiYit-lm
