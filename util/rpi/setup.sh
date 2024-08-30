#!/bin/bash

read -p "Setup Pi for running HUD software? (y or n)" yn;
case $yn in
	[Yy]* )
		# check serial port is already enabled
		if grep -q "enable_uart=1" /boot/config.txt; then
			echo "Serial port already enabled"
		else
			echo "Enabling serial port (ttyS0 is the built in serial port on the GPIO pins)"
			sudo bash -c 'echo " " >> /boot/config.txt'
			sudo bash -c 'echo "enable_uart=1" >> /boot/config.txt'
		fi

		# check splash image is already disabled
		if grep -q "disable_splash=1" /boot/config.txt; then
			echo "Splash image already disabled"
		else
			echo "disabling splash image (anoying boot up logo)"
			sudo bash -c 'echo "disable_splash=1" >> /boot/config.txt'
		fi

		# check if i2c is already enabled by running sudo raspi-config nonint get_i2c
		if [ $(sudo raspi-config nonint get_i2c) -eq 0 ]; then
			echo "i2c already enabled"
		else
			echo "Enabling i2c for use of ADS1115 (analog to digital converter)"
			sudo raspi-config nonint do_i2c 0
		fi


		# install required packages
		echo "Installing required python packages"
		sudo apt-get -y install python3 python-serial python-pygame python-pyaudio
		sudo pip3 install pygame_menu
		sudo pip3 install geographiclib
		sudo apt install libsdl2-ttf-2.0-0
		sudo pip3 install Adafruit_ADS1x15
		echo "Please reboot your pi now.  Type sudo reboot"
		;;
	[Nn]* )echo "Ok. Nothing done."; exit;;
esac



