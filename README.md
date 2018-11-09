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

`cd efis_to_hud`

then to run the script type

`./setup.sh`

5) reboot the device.  type

`reboot`

6) run the serial_read.py script to confirm data being sent is correct.
go into efis_hud dir then type

`cd efis_hud`

`python serial_read.py`

make sure the data is coming through and looks good.

to exit hit cntrl-c

7) run hud

`python hud.py`

current commands are:

q - quit

d - show some debug info

space - large/small toggle

a - show alt/airspeed tape (work in progress)

l - adjust line thickness

c - center circle mode



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

# line mode.  0 = skinny, 2 = bigger
line_mode = 1

# line thickness.  1 to 6 
line_thickness = 2

# center circle.  size of center circle. 0 = none. 1 tiny - 3 large
center_circle = 2

[DataInput]
# format of serial input. mgl or skyview
format = mgl

# port name for serial input. Default is /dev/ttyS0
port = /dev/ttyS0 

# baud rate. Default is 115200
baudrate = 115200 


</pre>

