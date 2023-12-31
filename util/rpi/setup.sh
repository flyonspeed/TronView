#!/bin/bash

echo "Setup Pi for running HUD software? (y or n)"
read -p " " yn;
if [ "$yn" != "y" ]; then
	echo "Ok. Not doing anything. Exiting..."
	exit;
fi

# bookworm?
if grep -q bookworm "/etc/os-release"; then
	echo "Running on Debian GNU/Linux 12 (bookworm)"

	echo "Enabling serial port"
	sudo bash -c 'echo " " >> /boot/config.txt'
	sudo bash -c 'echo "enable_uart=1" >> /boot/config.txt'

	echo "disable splash image"
	sudo bash -c 'echo "disable_splash=1" >> /boot/config.txt'

	echo "installing/updating python3"
	sudo apt-get -y install python3-full python-serial python-pygame python-pyaudio

	echo "installing required packages"
	sudo pip3 install pygame_menu --break-system-packages
	sudo pip3 install geographiclib --break-system-packages

	sudo apt install libsdl2-ttf-2.0-0

	echo "Please reboot your pi now.  Type reboot"
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







