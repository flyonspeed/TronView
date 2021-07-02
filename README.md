# efis_to_hud
Project for connecting efis/flight data to a HUD or 2nd screen.  

![hud_animation](https://github.com/flyonspeed/efis_to_hud/blob/master/docs/hud_animated_example.gif?raw=true)


This is a python application that will take in data from different input sources, process them into a common format, then output (draw) them to custom screens (HUD or efis style).  The system is created to have the inputs and screens seperate and non-dependent of each other.  For example a user running a MGL iEFIS can run the same HUD screen as a user with a Dynon D100.  Issues can come up with a input source does not have all the data available as other input sources do.  But if the screen is written well enough it will hide or show data if it's available.


Currently supports:

MGL iEFIS

Garmin G3x

Dynon Skyview

Dynon D10/100


We are using the rapberry pi zero w for taking serial data from a EFIS (MGL,Dynon,G3x) and displaying a graphical HUD out the hdmi output on the pi.  This is plugged into a HUD device like the Hudly Classic.  Any sort of HDMI screen could be hooked to the Pi for displaying this flight data.

Code is written in Python 3.7 and the Pygame module for handling the graphics.

You can run this code in either raspbian full or lite.

Raspbian full install contains the xwindow desktop system.  The lite version does not.
Efis2Hud supports both versions.

Get raspbian-stretch-lite SD image for pi. Latest can be gotten here.
https://downloads.raspberrypi.org/raspbian_lite_latest

Following install guide if you need help.  https://www.raspberrypi.org/documentation/installation/installing-images/README.md

Setup your serial input using the GPIO pins on pi zero.  This page will help you. https://www.instructables.com/id/Read-and-write-from-serial-port-with-Raspberry-Pi/

## Steps to get the HUD software running on raspberry pi

1) WIFI and autologin. You’ll want to get the pi on your wifi network so it can download the latest source.  Here are some instructions online that might help.  https://www.raspberrypi.org/documentation/configuration/wireless/wireless-cli.md

To setup auto login. (so you don't have to login to pi every time it boots up)

Enter the command `sudo raspi-config` Scroll down to Boot Options and select Console Autologin. Then exit the configuration menu and reboot.

2) Install git command.   This will let you get the latest source from github directly onto the pi.

`sudo apt-get -y install git`

3) clone the source from github

`git clone https://github.com/flyonspeed/efis_to_hud.git`

this will ask for username/email password from github.

when done this will create a efis_to_hud dir

4) run the setup.sh script to finish install.  This will setup serial port (if not allready setup), and install python libraries needed.

go into the efis_to_hud by typing

`cd efis_to_hud/util`

then to run the script type

`./setup.sh`

5) reboot the device.  type

`reboot`

6) Test the hud/efis screen with existing example data.  
run the following.  First make sure you are in the efis_hud dir.

`cd efis_hud`

Then run the python script and use the example data for dynon d100.

`sudo python hud.py -i serial_d100 -e`

You should see a basic hud on the screen.  And it slowy moving around.  
If not then your video setup maybe be F'd up.  

To exit you hit "q" on the keyboard.


7a) Next if you want to run live serial data from your efis.
run the serial_read.py script to confirm data being sent is correct.
go into efis_hud dir then type

`cd efis_hud`

`sudo python util/serial_read.py`

you will have to pass in -m or -s for mgl or skyview data.

make sure the data is coming through and looks good.

to exit hit cntrl-c

7b) run hud

Note:  You have to run using sudo in order to get access to serial port.

Example:

`sudo python hud.py -i serial_mgl`

will show you command line arguments.

`-i {input data source module}`

load a input module for where to get the air data from. 

-s (optional) {screen module name to load} (located in the lib/screens folder)

-t (optional) will let you see the data in text mode

-e (optional) demo mode. load default example demo data for input source selected.

-c FILENAME (optional) custom demo mode file. Enter filename of custom example demo file to use.

Run the command with no arguments and it will show you which input modules and screen modules are available to use.

`sudo python hud.py`

## More help on raspberry pi.

Here are more instructions on setting up for raspberry pi.

https://github.com/flyonspeed/efis_to_hud/blob/master/docs/rpi_setup.md

## DefaultScreen

The default screen has the following keyboard commands.

current commands are:

q - quit

d - show some debug info

space - large/small toggle

a - show alt/airspeed tape (work in progress)

l - adjust line thickness

c - center circle mode

f - show frame rate at bottom.

PAGE UP - jump to next screen

PAGE DOWN - go to previous screen

To run with


## Creating your own Hud screen file

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



## hud.cfg

hud.cfg can be created and sit in the same dir as the hud.py python app.  It's used for configuring the hud.

Here is a example hud.cfg file:

<pre>

[HUD]
#when running in xwindows this will show hud in window.
window=true

# define the drawable area for hud to use.  Useful on displays that have hidden areas.
# this is defined as x1,y1,x2,y2 to draw up a box of usable area.
#
#drawable_area=0,144,1280,624


#how many degrees to show on the vert hud lines. 5, 10, or 15
vertical_degrees = 10

#load a screen file on startup
screen = default screen module name to load

# line mode.  0 = skinny, 2 = bigger
line_mode = 1

# line thickness.  1 to 6 
line_thickness = 2

# center circle.  size of center circle. 0 = none. 1 tiny - 3 large
center_circle = 2

[DataInput]
# input source of data. These modules are located in lib/inputs.  currently supprt 'serial_mgl' or 'serial_skyview'
inputsource = serial_mgl

# port name for serial input. Default is /dev/ttyS0, for Windows you need to know the COM port you want to use ie: COM1, COM2, etc.
port = /dev/ttyS0 

# baud rate. Default is 115200
baudrate = 115200 


</pre>

# Demo Sample EFIS Data

  Demo data is saved in lib/inputs/_example_data .  Demo data lets you run previously recorded data through the hud app for demo or testing purposes.  Each input source module uses it's own format for data.  So for example if you want to run dynon demo data then you must run it through the dynon input source module.
  
  Using the -c FILENAME command line option loads data from the _example_data folder.
  
  Example to run the MGL_V2.bin demo data file would look like this:
  
  `sudo python hud.py -i serial_mgl -c MGL_V2.bin`


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
  
  Dynon D?? Series EFIS Sample Data Link: https://drive.google.com/open?id=1_os-xv0Cv0AGFVypLfSeg6ucGv5lwDVj
  
  Dynon D?? Series EFIS Serial Protocol Link: https://drive.google.com/open?id=1vUBMJZC3W85fBu33ObuurYx81kj09rqE

# Garmin Data

  Garmin G3X EFIS Sample Data Link: https://drive.google.com/open?id=1gHPC3OipAs9K06wj5zMw_uXn3_iqZriS

  Garmin G3X EFIS Serial Protocol Link: https://drive.google.com/open?id=1uRRO-wdG7ya6_6-CfDVrZaKJsiYit-lm
