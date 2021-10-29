#!/bin/bash

echo "Test stratux UDP connection Port 4000? (press u)"
echo "For UDP, If hex data shows then its connected. Then hit cntrl-c to exit"
read -p " " yn;
case $yn in
	[Uu]* )echo "Listening on port 4000"
		sudo nc -u -l 0.0.0.0 4000 -k |hd
		;;
	[Nn]* )echo "Later dude!."; exit;;
esac



