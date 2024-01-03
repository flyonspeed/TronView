#!/bin/bash

echo "Installing tools and setup for running TronView..."
#echo "Setup Pi for running HUD software? (y or n)"
#read -p " " yn;
#if [ "$yn" != "y" ]; then
#	echo "Ok. Not doing anything. Exiting..."
#	exit;
#fi

# make flight log dir.
echo "Creating /flightlog folder to save flight logs."
sudo mkdir /flightlog
sudo chmod 777 /flightlog

# print out pi model.
print_head "- Pi Model -"
cat /proc/device-tree/model && echo

# bookworm?
if grep -q bookworm "/etc/os-release"; then
	echo "Running on Debian GNU/Linux 12 (bookworm)"

	# check if pi 5
	if grep -q "Raspberry Pi 5" "/proc/device-tree/model"; then
		# running on pi 5.  Set serial port.
		if ! grep -q "dtparam=uart0=on" "/boot/config.txt"; then
			echo "Enabling Raspberry pi 5 serial port"
			sudo bash -c 'echo " " >> /boot/config.txt'
			sudo bash -c 'echo "dtparam=uart0=on" >> /boot/config.txt'
			echo "This requires restart to use serial port."
		else
			echo "Serial port already enabled (pi 5)"
		fi
	else
		# running pi 4 or below.. set serial port.
		if ! grep -q "enable_uart=1" "/boot/config.txt"; then
			echo "Enabling Raspberry pi 4 serial port"
			sudo bash -c 'echo " " >> /boot/config.txt'
			sudo bash -c 'echo "enable_uart=1" >> /boot/config.txt'
			echo "This requires restart to use serial port."
		else
			echo "Serial port already enabled (pi 4)"
		fi
	fi

	# boot splash screen?
	if ! grep -q "disable_splash=1" "/boot/config.txt"; then
		echo "Disable boot up splash image"
		sudo bash -c 'echo "disable_splash=1" >> /boot/config.txt'
	fi

	echo "installing/updating python3"
	sudo apt-get -y install python3-full python-serial python-pygame python-pyaudio

	echo "installing required packages"
	sudo pip3 install pygame_menu --break-system-packages
	sudo pip3 install geographiclib --break-system-packages

	sudo apt install libsdl2-ttf-2.0-0

fi

# bullseye?
if grep -q bullseye "/etc/os-release"; then
	echo "Running on Debian GNU/Linux 11 (bullseye)"

	echo "Enabling serial port"
	sudo bash -c 'echo " " >> /boot/config.txt'
	sudo bash -c 'echo "enable_uart=1" >> /boot/config.txt'

	echo "disable splash image"
	sudo bash -c 'echo "disable_splash=1" >> /boot/config.txt'

	echo "installing/updating python3"
	sudo apt-get -y install python3 python-serial python-pygame python-pyaudio

	echo "installing required packages"
	sudo pip3 install pygame_menu 
	sudo pip3 install geographiclib 

	sudo apt install libsdl2-ttf-2.0-0

	echo "Please reboot your pi now.  Type reboot"
fi







