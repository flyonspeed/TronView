#!/bin/bash

echo "Setup Pi for running HUD software? (y or n)"
read -p " " yn;
case $yn in
	[Yy]* )echo "Enabling serial port"
		sudo bash -c 'echo " " >> /boot/config.txt'
		sudo bash -c 'echo "enable_uart=1" >> /boot/config.txt'
		sudo apt-get install python-serial python-pygame
		echo "Please reboot your pi now.  Type reboot"
		;;
	[Nn]* )echo "Ok. Nothing done."; exit;;
esac



