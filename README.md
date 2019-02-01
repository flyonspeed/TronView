# efis_to_hud
Project for connecting efis data to a HUD.  

We are using the rapberry pi zero w for taking serial data from a EFIS (MGL or Dynon Skyview) and displaying a graphical HUD out the hdmi output on the pi.  This is plugged into a HUD device like the Hudly Classic.

Get raspbian-stretch-lite SD image for pi. Latest can be gotten here.
https://downloads.raspberrypi.org/raspbian_lite_latest

Following install guide if you need help.  https://www.raspberrypi.org/documentation/installation/installing-images/README.md

Setup your serial input using the GPIO pins on pi zero.  This page will help you. https://www.instructables.com/id/Read-and-write-from-serial-port-with-Raspberry-Pi/

## Steps to get the HUD software running

1) WIFI and autologin. You’ll want to get the pi on your wifi network so it can download the latest source.  Here are some instructions online that might help.  https://www.raspberrypi.org/documentation/configuration/wireless/wireless-cli.md

To setup auto login. (so you don't have to login to pi every time it boots up)

Enter the command `sudo raspi-config` Scroll down to Boot Options and select Console Autologin. Then exit the configuration menu and reboot.

2) Install git command.   This will let you get the latest source from github directly onto the pi.

`sudo apt-get -y install git`

3) clone the source from github

`git clone https://github.com/dinglewanker/efis_to_hud.git`

this will ask for username/email password from github.

when done this will create a efis_to_hud dir

4) run the setup.sh script to finish install.  This will setup serial port (if not allready setup), and install python libraries needed.

go into the efis_to_hud by typing

`cd efis_to_hud/util`

then to run the script type

`./setup.sh`

5) reboot the device.  type

`reboot`

6) run the serial_read.py script to confirm data being sent is correct.
go into efis_hud dir then type

`cd efis_hud`

`sudo python util/serial_read.py`

you will have to pass in -m or -s for mgl or skyview data.

make sure the data is coming through and looks good.

to exit hit cntrl-c

7) run hud

Note:  You have to run using sudo in order to get access to serial port.

Example:

`sudo python hud.py -i serial_mgl -s ReallyBigHud`

will show you command line arguments.

`-i {input data source module}`

load a input module for where to get the air data from. 

-s {screen module name to load} (located in the lib/screens folder)

-t (optional) will let you see the data in text mode

Run the command with no arguments and it will show you which input modules and screen modules are available to use.

`sudo python hud.py`


## DefaultScreen

The default screen has the following keyboard commands.

current commands are:

q - quit

d - show some debug info

space - large/small toggle

a - show alt/airspeed tape (work in progress)

l - adjust line thickness

c - center circle mode

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

Input sources are located in lib/inputs folder.  Create your own!


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

# port name for serial input. Default is /dev/ttyS0
port = /dev/ttyS0 

# baud rate. Default is 115200
baudrate = 115200 


</pre>

# Sample EFIS Data

  MGL EFIS Sample Data Link: https://drive.google.com/open?id=1mPOmQuIT-Q5IvIoVmyfRCtvBxCsLUuvz

  MGL EFIS Serial Protocol Link: https://drive.google.com/open?id=1OYj000ghHJqSfvacaHMO-jOcfd1raoVo


  Dynon Skyview EFIS Sample Data Link:https://drive.google.com/open?id=1jQ0q4wkq31C7BRn7qzMSMClqPw1Opwnp

  Dynon Skyview EFIS Serial Protocol Link: https://drive.google.com/open?id=1isurAOIiTzki4nh59lg6IDsy1XcsJqoG


  Garmin G3X EFIS Sample Data Link: https://drive.google.com/open?id=1gHPC3OipAs9K06wj5zMw_uXn3_iqZriS

  Garmin G3X EFIS Serial Protocol Link: https://drive.google.com/open?id=1uRRO-wdG7ya6_6-CfDVrZaKJsiYit-lm
