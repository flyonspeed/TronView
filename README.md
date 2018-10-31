# efis_to_hud
Project for connecting efis data to a HUD

Get raspbian-stretch-lite SD image for pi. Latest can be gotten here.
https://downloads.raspberrypi.org/raspbian_lite_latest
Following install guide if you need help.  https://www.raspberrypi.org/documentation/installation/installing-images/README.md


## Steps to get the HUD software running

1) WIFI. You’ll want to get the pi on your wifi network so it can download the latest source.  You can google for directions on how to do that.

2) install git command.   running the following on the command line.

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
a - show alt/airspeed tape (still working on this)
