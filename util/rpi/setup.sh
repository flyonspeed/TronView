#!/bin/bash

# make sure they are on linux
if [[ $(uname) != "Linux" ]]; then
	echo "This script is only supported on Linux."
	exit 1
fi

# Get absolute paths. remove 2 levels from the path because we are in util/macosx
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
TRONVIEW_DIR="$(dirname "$(dirname "$SCRIPT_DIR")")"
echo "TronView directory: $TRONVIEW_DIR"

# cat docs/imgs/logo_txt_small.txt
cat "$TRONVIEW_DIR/docs/imgs/logo_txt_small.txt"
echo ""
printf "Raspberry Pi / Linux Setup script Version 0.1.3 \n\n"
echo "-----------------------------------"

# update apt-get quietly
echo "Updating apt-get"
sudo apt-get -qq update

# get 32 or 64 bit version os?
bit_size=$(getconf LONG_BIT)
printf "OS detected as $bit_size bit \n"

# get memory size of pi?
#free -h
#               total        used        free      shared  buff/cache   available
#Mem:           3.7Gi       2.3Gi       174Mi       371Mi       1.6Gi       1.4Gi
#Swap:          199Mi          0B       199Mi
total_memory=$(free -h | grep Mem: | awk '{print $2}')
# if Gi is not in total memory, then its the 1GB version
if [[ $total_memory != *"Gi"* ]]; then
	total_memory="1Gi"
fi
# remove Gi from total memory
total_memory=${total_memory::-2}
# convert total memory to int (round up)
pi_size=$(echo $total_memory | awk '{print int($1+0.5) " Gb version"}')
printf "Pi detected size: $pi_size \n"

# os name
os_pretty_name=$(cat /etc/os-release | grep PRETTY_NAME | cut -d'=' -f2 | sed 's/"//g')
printf "OS is $os_pretty_name \n\n"

# check serial port is already enabled
if grep -q "enable_uart=1" /boot/config.txt; then
	echo "Built in Serial port already enabled"
else
	echo "Enabling serial port (ttyS0 is the built in serial port on the GPIO pins)"
	sudo bash -c 'echo " " >> /boot/config.txt'
	sudo bash -c 'echo "enable_uart=1" >> /boot/config.txt'
fi

# check splash image is already disabled
if grep -q "disable_splash=1" /boot/config.txt; then
	echo "Splash image already disabled."
else
	echo "disabling splash image (anoying boot up logo)"
	sudo bash -c 'echo "disable_splash=1" >> /boot/config.txt'
fi

# check if i2c is already enabled by running sudo raspi-config nonint get_i2c
if [ $(sudo raspi-config nonint get_i2c) -eq 0 ]; then
	echo "i2c already enabled (used for ADS1115 analog to digital converter and BNO085/BNO055 IMU)"
else
	echo "Enabling i2c for use of ADS1115 (analog to digital converter) and BNO085/BNO055 IMU"
	sudo raspi-config nonint do_i2c 0
fi

# check rpi os is Debian GNU/Linux 12 (bookworm).. check by running cat /etc/os-release
if [ $(cat /etc/os-release | grep "Debian GNU/Linux 12" | wc -l) -eq 1 ]; then
	echo "OS is Debian GNU/Linux 12 (bookworm)"		

	# install required packages
	echo "Installing required python3 packages"
	sudo apt-get -y install python3 python3-serial python3-pyaudio
	sudo apt-get -y install dialog
	sudo pip3 install pygame-ce --break-system-packages
	sudo pip3 install geographiclib --break-system-packages
	sudo apt install libsdl2-ttf-2.0-0 
	sudo pip3 install Adafruit_ADS1x15 --break-system-packages
	sudo pip3 install numpy --break-system-packages
	sudo pip3 install pygame_gui --break-system-packages 
	sudo pip3 install numpy-stl --break-system-packages
	sudo pip3 install kivy --break-system-packages
	sudo pip3 install https://github.com/kivy/kivy3/archive/master.zip --break-system-packages

	pip_args="--break-system-packages"

fi

# check rpi os is Raspbian GNU/Linux 11 (bullseye).. check by running cat /etc/os-release
# bullseye comes with python 3.9.2
if [ $(cat /etc/os-release | grep "GNU/Linux 11" | wc -l) -eq 1 ]; then
	# get os pretty name
	echo "OS is $os_pretty_name.  "

	# install required packages
	echo "Installing required python3 packages"
	sudo apt-get -y install python3 python3-serial python3-pyaudio
	sudo apt-get -y install libsdl2-ttf-2.0-0 
	sudo apt-get -y install dialog
	sudo pip3 install pygame-ce
	sudo pip3 install geographiclib
	sudo pip3 install Adafruit_ADS1x15
	sudo pip3 install numpy
	sudo pip3 install pygame_gui
	sudo pip3 install numpy-stl
	sudo pip3 install kivy
	sudo pip3 install https://github.com/kivy/kivy3/archive/master.zip

	# check if python 3.9.2 is installed
	if [ $(python3 --version | grep "3.9.2" | wc -l) -eq 1 ]; then
		$pip_args=""
	fi
fi

# Create temporary file for dialog output
temp_file=$(mktemp)

# Main dialog menu
dialog --clear --title "Sensor Installation" \
       --checklist "Select options to install:" 15 60 3 \
       "BNO055" "Bosch BNO055 9-DOF sensor" ON \
       "BNO085" "Bosch BNO085 9-DOF sensor" ON \
       "AutoRun" "Setup autorun on boot" ON \
	   "Desktop" "Create desktop run shortcut" ON \
       2> $temp_file

# Read selections
selections=$(cat $temp_file)

# Process selections
if [[ $selections == *"BNO055"* ]]; then
    echo "Installing BNO055 IMU python library"
    sudo pip3 install adafruit-circuitpython-bno055 $pip_args
fi

if [[ $selections == *"BNO085"* ]]; then
    echo "Installing BNO085 IMU python library"
    sudo pip3 install adafruit-circuitpython-bno08x $pip_args
    
    # Automatically set I2C baud rate for BNO085
    if ! grep -q "dtparam=i2c_arm_baudrate=400000" /boot/config.txt; then
        echo "Setting i2c baud rate to 400000"
        sudo bash -c 'echo "dtparam=i2c_arm_baudrate=400000" >> /boot/config.txt'
    fi
fi

if [[ $selections == *"AutoRun"* ]] && [ $(cat /etc/os-release | grep "Debian GNU/Linux 12" | wc -l) -eq 1 ]; then
    echo "Setting up autorun"
    sudo bash -c 'echo "[Desktop Entry]
Type=Application
Name=StartTronView
Path='$TRONVIEW_DIR'
Exec=lxterminal -e '$TRONVIEW_DIR'/util/run.sh
Terminal=true
StartupNotify=false" > /etc/xdg/autostart/start_tronview.desktop'
fi

if [[ $selections == *"Desktop"* ]]; then
	echo "Creating desktop run shortcut"
	# get user home directory
	user_home=$(eval echo ~$(whoami))
	echo '[Desktop Entry]
	Type=Application
	Name=TronView
	Icon='$TRONVIEW_DIR/docs/imgs/tronview_thumb.png'
	Path='$TRONVIEW_DIR'
	Exec=lxterminal -e '$TRONVIEW_DIR'/util/run.sh
	Terminal=true
	StartupNotify=false' >> $user_home/Desktop/TronView.desktop
fi

# Clean up
rm -f $temp_file

echo "" # blank line
echo "----------------------------------------"
echo "Done. Your Pi may need to be rebooted to enable serial or i2c.  Type sudo reboot"




