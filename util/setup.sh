#!/bin/bash

echo "Setup Pi for running HUD software? (y or n)"
read -p " " yn;
case $yn in
	[Yy]* )echo "Enabling serial port"
		sudo bash -c 'echo " " >> /boot/config.txt'
		sudo bash -c 'echo "enable_uart=1" >> /boot/config.txt'
		sudo apt-get -y install python python-serial python-pygame python-pyaudio
		echo "Please reboot your pi now.  Type reboot"
		;;
	[Nn]* )echo "Ok. Nothing done."; exit;;
esac



