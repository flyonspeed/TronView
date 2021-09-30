#!/bin/bash

echo "Setup Pi for running HUD software? (y or n)"
read -p " " yn;
case $yn in
	[Yy]* )echo "Enabling serial port"
		sudo bash -c 'echo " " >> /boot/config.txt'
		sudo bash -c 'echo "enable_uart=1" >> /boot/config.txt'
		echo "disable splash image"
		sudo bash -c 'echo "disable_splash=1" >> /boot/config.txt'
		sudo apt-get -y install python3 python-serial python-pygame python-pyaudio
		sudo pip3 install pygame_menu
		sudo apt install libsdl2-ttf-2.0-0
		echo "Please reboot your pi now.  Type reboot"
		;;
	[Nn]* )echo "Ok. Nothing done."; exit;;
esac



