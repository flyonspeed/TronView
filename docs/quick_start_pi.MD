
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

4) run the util/rpi/setup.sh script to finish install.  This will enable built in serial port, enable i2c , and install python libraries needed.  


`sudo ./util/rpi/setup.sh`

5) reboot the device.  type

`sudo reboot`

6) Test the hud/efis screen with existing example data.  
run the following.  First make sure you are in the efis_hud dir.

`cd TronView`

Run a demo

`./util/run_choose.sh`

This will show you a list of options to run.

Some keyboard commands:

q - quit

? - show help


7) Next if you want to run live serial data from your efis.
run the serial_read.py script to confirm data being sent is correct.
go into TronView dir then type

`cd TronView`

`sudo python util/serial_read.py`

you will have to pass in -m or -s for mgl or skyview data.

make sure the data is coming through and looks good.

to exit hit cntrl-c

8) run it

Note:  You have to run using sudo in order to get access to serial port.

Example:

`sudo python3 main.py -i serial_mgl -e`

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

--listexamplelogs (optional) show example log files to playback


Run the command with no arguments and it will show you which input modules and screen modules are available to use.

`sudo python3 main.py`

## Examples command line arguments

To set Input1 to garmin g3x and Input2 to stratux wifi and run default example data run the following.

`sudo python3 main.py --in1 serial_g3x --in2 stratux_wifi -e`


To run Input1 to MGL and Input2 as stratux.  then supply custom example log files...  Note that these custom log files are in the example data dir.  This will also check the DataRecorder path dir that you set in the config file. 

`python3 main.py --in1 serial_mgl --playfile1 mgl_1.dat --in2 stratux_wifi --playfile2 startux_1.dat`


Lauch app in text mode playing dynon D100 example data. Press 'Q' to exit Text Mode.

`python3 main.py --in1 serial_d100 -t -e`

## More help on raspberry pi.

Here are more instructions on setting up for raspberry pi.

https://github.com/flyonspeed/TronView/blob/master/docs/rpi_setup.md

