#!/bin/bash

echo "Setup mac osx for running software efis code"
echo "-----------------------------------"


echo "Install Homebrew?.. it's required to install python3 and pygame ? (y or n)"
read -p " " yn;
case $yn in
	[Yy]* )echo "Installing homebrew"
		ruby -e '$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install)'
		echo export PATH='usr/local/bin:$PATH' >> ~/.bash_profile
		brew update
		brew doctor
		;;
	[Nn]* )echo "..."; 
esac


echo "Install python3? (y or n)"
read -p " " yn;
case $yn in
	[Yy]* )echo "Installing python3 via homebrew"
		brew install python3
		;;
	[Nn]* )echo "..."; 
esac


echo "Install other python packages via pip3?  (y or n)"
read -p " " yn;
case $yn in
	[Yy]* )echo "Installing pygame via pip3"
		pip3 install pygame
		echo "Installing python serial via pip3"
		pip3 install serial
		pip3 install pygame_menu
		pip3 install MacTmp
		pip3 install geographiclib 
		;;
	[Nn]* )echo "..."; 
esac

