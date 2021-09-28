#!/bin/bash

echo "Test iLevil UDP connection ? (y or n)"
echo "If hex data shows then its connected. Then hit cntrl-c to exit"
read -p " " yn;
case $yn in
	[Yy]* )echo "Listening on port 43211"
		sudo nc -u -l 0.0.0.0 43211 -k |hd
		;;
	[Nn]* )echo "Later dude!."; exit;;
esac



